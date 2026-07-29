import math
import re
from shapely.geometry import Point, Polygon


def label_rooms_from_ocr(image, rooms: list[dict]) -> list[dict]:
    try:
        import pytesseract
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        texts = _extract_text_regions(data)
    except Exception:
        texts = []

    labeled = []
    for i, room in enumerate(rooms):
        pts = [(p['x'], p['y']) for p in room['polygon']]
        poly = Polygon(pts) if len(pts) >= 3 else None

        matched_label = None
        if poly and poly.is_valid:
            # 1. Match text strictly inside room polygon
            inside_texts = []
            for t in texts:
                p = Point(t['x'], t['y'])
                if poly.contains(p):
                    inside_texts.append(t['text'])
            if inside_texts:
                matched_label = ' '.join(inside_texts)

        # 2. Fallback to centroid nearest distance
        if not matched_label:
            cx = sum(p['x'] for p in room['polygon']) / max(1, len(room['polygon']))
            cy = sum(p['y'] for p in room['polygon']) / max(1, len(room['polygon']))
            matched_label = _find_nearest_text(cx, cy, texts)

        if not matched_label or len(matched_label.strip()) < 2:
            matched_label = room.get('label') or f'Room {i + 1}'

        room['label'] = _clean_room_label(matched_label)
        labeled.append(room)

    return labeled


def _extract_text_regions(data: dict) -> list[dict]:
    texts = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        conf = int(data['conf'][i]) if 'conf' in data and data['conf'][i] != '-1' else 0
        if not text or conf < 25:
            continue
        texts.append({
            'text': text,
            'x': float(data['left'][i] + data['width'][i] / 2),
            'y': float(data['top'][i] + data['height'][i] / 2),
        })
    return texts


def _find_nearest_text(cx: float, cy: float, texts: list[dict], max_dist: float = 150.0) -> str:
    best = None
    best_dist = max_dist
    for t in texts:
        d = math.hypot(t['x'] - cx, t['y'] - cy)
        if d < best_dist:
            best_dist = d
            best = t['text']
    return best or ''


def _clean_room_label(label: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9\s\-]', '', label).strip()
    return clean.title() if clean else 'Room'

