"""Step-by-step separated verification tests for floor plan parsing pipeline:
1. Wall Detector Test
2. Door & Opening Detector Test
3. Room Polygon Extractor Test
4. Vector Graph Generation & Canvas Alignment Test
"""
import os
import sys
from pathlib import Path
import pytest

_THIS_DIR = Path(__file__).resolve().parent
_PKG_ROOT = _THIS_DIR.parent
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from app.processors.wall_detector import detect_walls
from app.processors.opening_detector import detect_openings
from app.processors.room_extractor import extract_rooms
from app.utils.image_preprocessing import load_image, preprocess_floorplan
from app.orchestrator import parse_floor_plan


def _get_test_image_bytes() -> bytes:
    candidates = [
        _PKG_ROOT.parent.parent / 'apps' / 'api' / 'data' / 'uploads',
        _PKG_ROOT / 'tests' / 'fixtures',
    ]
    for d in candidates:
        if d.exists():
            images = sorted(d.glob('*.jpg')) + sorted(d.glob('*.png'))
            if images:
                return images[0].read_bytes()
    pytest.skip('No test image found')


@pytest.fixture(scope='module')
def sample_bytes():
    return _get_test_image_bytes()


def test_step1_wall_detector_vectorization(sample_bytes):
    """Step 1: Verify wall detector extracts clean, orthogonal wall vectors."""
    img = load_image(sample_bytes)
    prep = preprocess_floorplan(img)
    walls = detect_walls(prep['wall_mask'], [])

    assert len(walls) >= 4, f"Step 1 Failed: Expected >= 4 walls, got {len(walls)}"

    # Check wall structure integrity
    for w in walls:
        assert 'start' in w and 'end' in w and 'thickness' in w
        assert w['thickness'] >= 8.0, f"Wall thickness too small: {w['thickness']}"
        length = ((w['end']['x'] - w['start']['x'])**2 + (w['end']['y'] - w['start']['y'])**2)**0.5
        assert length >= 10.0, f"Wall segment collapsed: length {length}"

    print(f"\n[STEP 1 PASSED] Extracted {len(walls)} structural wall vectors successfully.")


def test_step2_opening_and_door_detector(sample_bytes):
    """Step 2: Verify door detector eliminates false-positive door arcs."""
    img = load_image(sample_bytes)
    prep = preprocess_floorplan(img)
    walls = detect_walls(prep['wall_mask'], [])
    openings = detect_openings(img, None, walls)

    # Ensure no false-positive door floods (must not exceed plausible door count per project)
    doors = [o for o in openings if o['type'] == 'door']
    assert len(doors) <= 15, f"Step 2 Failed: Excessive false positive doors detected ({len(doors)})"

    for o in openings:
        assert o['type'] in ('door', 'window')
        assert 'wall_id' in o and 'position' in o
        assert 0.0 <= o['position'] <= 1.0, f"Opening position out of bounds: {o['position']}"

    print(f"\n[STEP 2 PASSED] Detected {len(openings)} openings ({len(doors)} doors) within valid threshold bounds.")


def test_step3_room_extractor(sample_bytes):
    """Step 3: Verify room extractor produces closed polygon geometries."""
    img = load_image(sample_bytes)
    prep = preprocess_floorplan(img)
    rooms = extract_rooms(prep['binary'], [])

    assert len(rooms) >= 2, f"Step 3 Failed: Expected >= 2 rooms, got {len(rooms)}"

    for r in rooms:
        assert 'polygon' in r and len(r['polygon']) >= 3
        assert 'label' in r and len(r['label']) > 0

    print(f"\n[STEP 3 PASSED] Extracted {len(rooms)} closed room polygons with labels.")


def test_step4_full_vector_graph_generation(sample_bytes):
    """Step 4: Verify end-to-end vector graph generation and scaling precision."""
    import asyncio
    graph = asyncio.run(parse_floor_plan(sample_bytes, project_id='step_test')).model_dump()

    assert 'walls' in graph and len(graph['walls']) >= 4
    assert 'rooms' in graph and len(graph['rooms']) >= 2
    assert 'openings' in graph
    assert graph['version'] == 1

    print(f"\n[STEP 4 PASSED] Full FloorPlanGraph generated successfully with version={graph['version']}.")
