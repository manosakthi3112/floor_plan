"""Regression tests for the floor-plan parsing pipeline.

These guard against the bug that motivated this rewrite: the old pipeline
returned ZERO rooms and fragmented walls because a morphological opening
erased thin interior partitions. They also lock the serialization data
contract consumed by the TypeScript frontend (camelCase openings keys,
{x,y} point objects, >=3-point room polygons).
"""
import os
from pathlib import Path

import pytest

# The parsing package is not installed; add its parent to sys.path so
# `from app.orchestrator import ...` resolves when pytest runs from anywhere.
_THIS_DIR = Path(__file__).resolve().parent
_PKG_ROOT = _THIS_DIR.parent  # .../services/parsing
import sys
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from app.orchestrator import parse_floor_plan  # noqa: E402
from app.processors.room_extractor import extract_rooms  # noqa: E402
from app.processors.wall_detector import detect_walls  # noqa: E402
from app.utils.image_preprocessing import load_image, preprocess_floorplan  # noqa: E402


def _find_sample_image() -> Path:
    """Locate a real uploaded floor plan to run the pipeline against.

    Search order: explicit env var, then known upload dirs relative to the
    repo root, then any .jpg/.png under apps/api/data/uploads.
    """
    env = os.environ.get('FLOORPLAN_TEST_IMAGE')
    if env and Path(env).exists():
        return Path(env)

    candidates = [
        _PKG_ROOT.parent.parent / 'apps' / 'api' / 'data' / 'uploads',
        _PKG_ROOT / 'tests' / 'fixtures',
    ]
    for d in candidates:
        if not d.exists():
            continue
        images = sorted(d.glob('*.jpg')) + sorted(d.glob('*.png'))
        if images:
            return images[0]

    pytest.skip('No sample floor plan image found for parsing tests')


@pytest.fixture(scope='module')
def sample_image_bytes() -> bytes:
    return _find_sample_image().read_bytes()


@pytest.fixture(scope='module')
def parsed_graph(sample_image_bytes):
    import asyncio
    return asyncio.run(parse_floor_plan(sample_image_bytes, project_id='test'))


def test_pipeline_returns_walls(parsed_graph):
    """The old pipeline returned only a handful of fragmented walls; the fix
    must vectorize the full wall network (outer shell + interior partitions)."""
    walls = parsed_graph.model_dump()['walls']
    assert len(walls) >= 4, f'expected several walls, got {len(walls)}'


def test_pipeline_returns_rooms(parsed_graph):
    """The headline regression: previously returned 0 rooms."""
    rooms = parsed_graph.model_dump()['rooms']
    assert len(rooms) >= 2, f'expected multiple rooms, got {len(rooms)}'


def test_wall_contract(parsed_graph):
    """Every wall must carry the fields the frontend meshBuilder reads."""
    for w in parsed_graph.model_dump()['walls']:
        assert {'id', 'start', 'end', 'thickness', 'height', 'type'} <= w.keys()
        assert isinstance(w['start'], dict) and {'x', 'y'} <= w['start'].keys()
        assert isinstance(w['end'], dict) and {'x', 'y'} <= w['end'].keys()
        assert isinstance(w['height'], (int, float)) and w['height'] > 0
        assert isinstance(w['thickness'], (int, float)) and w['thickness'] > 0


def test_room_polygon_has_at_least_three_points(parsed_graph):
    """meshBuilder and the 2D canvas both require >=3 polygon points or the
    room is dropped from rendering."""
    for r in parsed_graph.model_dump()['rooms']:
        assert len(r['polygon']) >= 3, f"room {r['id']} has <3 polygon points"
        for p in r['polygon']:
            assert {'x', 'y'} <= p.keys()


def test_openings_use_camel_case_not_snake_case(parsed_graph):
    """The TS frontend reads wallId/sillHeight exclusively. The orchestrator
    hand-builds dicts to emit camelCase (the schema uses list[dict], so these
    pass through model_dump unchanged). This must not regress to snake_case."""
    graph = parsed_graph.model_dump()
    for o in graph['openings']:
        assert 'wallId' in o, 'opening missing camelCase wallId'
        assert 'sillHeight' in o, 'opening missing camelCase sillHeight'
        assert 'wall_id' not in o, 'snake_case wall_id leaked into output'
        assert 'sill_height' not in o, 'snake_case sill_height leaked into output'


def test_confidence_is_in_range(parsed_graph):
    c = parsed_graph.model_dump()['confidence']
    assert 0.0 <= c <= 1.0
    # A parse that found both walls and rooms should be reasonably confident.
    assert c >= 0.5


def test_confidence_low_without_rooms():
    """If segmentation produced walls but no rooms, confidence must be low so
    the frontend's 'Low Confidence Parse' fallback UI triggers."""
    from app.orchestrator import _compute_confidence
    c = _compute_confidence(
        walls=[{'id': 'w1', 'start': {'x': 0, 'y': 0}, 'end': {'x': 10, 'y': 0}}],
        rooms=[],
        detections=[],
    )
    assert c < 0.5


def test_room_extractor_does_not_return_zero(sample_image_bytes):
    """Direct unit check of the room extractor in isolation — the exact layer
    that returned 0 rooms before the fix."""
    img = load_image(sample_image_bytes)
    prep = preprocess_floorplan(img)
    rooms = extract_rooms(prep['binary'], [])
    assert len(rooms) >= 2, f'room extractor returned {len(rooms)} rooms (was 0 before fix)'


def test_walls_include_internal_partitions(sample_image_bytes):
    """The wall mask must retain interior partitions, not just the outer shell.

    A plan with only an outer rectangle would have <=4 walls after merging;
    a real partitioned plan yields many more (outer + internal)."""
    img = load_image(sample_image_bytes)
    prep = preprocess_floorplan(img)
    walls = detect_walls(prep['wall_mask'], [])
    assert len(walls) > 4, f'only {len(walls)} walls — internal partitions likely erased again'


def test_preprocessing_returns_scale_and_orig_shape(sample_image_bytes):
    """Coordinates are scaled back to original pixels; the preprocessor must
    expose the scale factor and original shape."""
    img = load_image(sample_image_bytes)
    prep = preprocess_floorplan(img)
    assert 'scale' in prep and prep['scale'] >= 1.0
    assert 'orig_shape' in prep
    assert prep['orig_shape'] == img.shape[:2]
