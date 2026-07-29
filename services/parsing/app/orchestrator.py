import datetime
import logging

from .processors.wall_detector import detect_walls
from .processors.opening_detector import detect_openings
from .processors.room_extractor import extract_rooms
from .processors.ocr_labeler import label_rooms_from_ocr
from .schemas.floor_plan_graph import FloorPlanGraph
from .utils.image_preprocessing import load_image, preprocess_floorplan

logger = logging.getLogger('parsing.orchestrator')


async def parse_floor_plan(image_bytes: bytes, project_id: str = '') -> FloorPlanGraph:
    # 1. Load image and run multi-stage preprocessing.
    # The preprocessor returns masks in *canonical* (resized) pixel space and a
    # `scale` factor; we vectorize in canonical space for resolution-independent
    # thresholds, then scale coordinates back to the original image dimensions
    # so the frontend overlay lines up with the source image.
    img = load_image(image_bytes)
    preprocessed = preprocess_floorplan(img)
    wall_mask = preprocessed['wall_mask']
    binary = preprocessed['binary']
    scale = preprocessed.get('scale', 1.0)
    scale_back = float(scale)

    # 2. Try object detection (Ultralytics YOLO / Transformers) as an OPTIONAL
    # enhancement layer. Classic CV is the primary, reliable path; the model is
    # used only to augment/override when a trained model file is actually
    # available. Detection errors are LOGGED (not silently swallowed) so a
    # missing/corrupt model is visible in logs instead of looking like success.
    detections: list[dict] = []
    try:
        from .models.detection_model import detect_elements
        detections = detect_elements(img)
        if detections:
            logger.info('Object detection returned %d elements', len(detections))
    except Exception as exc:  # noqa: BLE001 - we want to log ANY model-path failure
        logger.warning('Object detection unavailable (%s); falling back to CV only', exc)

    # 3. Detect & vectorize structural walls (Hough/LSD + orthogonal snapping +
    # junction merging). CV is primary; the model only overrides if it produced
    # wall boxes.
    walls_raw = detect_walls(wall_mask, detections)

    walls_formatted = []
    for i, w in enumerate(walls_raw):
        wall_id = f'w{i + 1}'
        # Scale coordinates from canonical space back to original pixels.
        formatted = {
            'id': wall_id,
            'start': {'x': round(w['start']['x'] * scale_back, 1),
                      'y': round(w['start']['y'] * scale_back, 1)},
            'end': {'x': round(w['end']['x'] * scale_back, 1),
                    'y': round(w['end']['y'] * scale_back, 1)},
            'thickness': w.get('thickness', 12.0),
            'height': 270.0,
            'type': 'interior',
        }
        walls_formatted.append(formatted)

    # 4. Detect openings (doors & windows) and project onto nearby wall segments.
    openings_raw = detect_openings(img, detections, walls_formatted, wall_mask=wall_mask)
    # Serialize with camelCase aliases for the TS frontend
    # (wall_id -> wallId, sill_height -> sillHeight). The FloorPlanGraph schema
    # uses untyped list[dict], so these keys pass straight through model_dump().
    openings_dicts = []
    for i, o in enumerate(openings_raw):
        openings_dicts.append({
            'id': f'o{i + 1}',
            'type': o['type'],
            'wallId': o['wall_id'],
            'position': o['position'],
            'width': o['width'],
            'height': o['height'],
            'sillHeight': o['sill_height'],
        })

    # 5. Extract closed room polygons via flood-fill segmentation.
    rooms_raw = extract_rooms(binary, [])

    # Scale room polygons back to original pixels.
    for r in rooms_raw:
        r['polygon'] = [
            {'x': round(p['x'] * scale_back, 1), 'y': round(p['y'] * scale_back, 1)}
            for p in r['polygon']
        ]

    # 6. OCR room labeling & text matching (overwrites geometric fallback labels).
    try:
        rooms_raw = label_rooms_from_ocr(img, rooms_raw)
    except Exception as exc:  # noqa: BLE001
        logger.warning('OCR labeling failed (%s); keeping geometric labels', exc)

    rooms_dicts = []
    for r in rooms_raw:
        rooms_dicts.append({
            'id': r['id'],
            'label': r['label'],
            'polygon': [{'x': p['x'], 'y': p['y']} for p in r['polygon']],
            'level': r.get('level', 0),
            'area': r.get('area', 0.0),
        })

    # 7. Confidence score evaluation.
    # A parse with walls but no rooms is almost certainly a failed segmentation,
    # so room presence is a strong sanity signal. This makes the frontend's
    # low-confidence fallback UI actually trigger on bad parses.
    confidence = _compute_confidence(walls_formatted, rooms_dicts, detections)

    return FloorPlanGraph(
        version=1,
        unit='mm',
        walls=walls_formatted,
        rooms=rooms_dicts,
        openings=openings_dicts,
        confidence=confidence,
        metadata={
            'projectId': project_id,
            'source': 'upload',
            'createdAt': datetime.datetime.utcnow().isoformat(),
        },
    )


def _compute_confidence(walls: list[dict], rooms: list[dict], detections: list[dict]) -> float:
    """Blend structural sanity signals into a single 0..1 confidence score.

    - walls present  -> baseline lift
    - rooms present  -> strong lift (segmentation succeeded)
    - model detections -> lift when available
    """
    has_walls = len(walls) > 0
    has_rooms = len(rooms) > 0

    if not has_walls and not has_rooms:
        return 0.25
    if has_walls and not has_rooms:
        # Walls but no rooms = a failed seal; low confidence so the user is
        # warned and can manually correct.
        confidence = 0.4
    else:
        confidence = 0.8
        # Reward a believable number of rooms; cap the bonus.
        confidence += min(0.1, len(rooms) * 0.02)

    if detections:
        det_conf = sum(d.get('confidence', 0.5) for d in detections) / max(len(detections), 1)
        confidence = (confidence + det_conf) / 2.0

    return round(min(1.0, max(0.0, confidence)), 2)
