"""Diagnostic script: runs the full parsing pipeline against the first uploaded
floor plan image and dumps detailed per-stage results to JSON + a visual
overlay image so we can see EXACTLY what the wall detector, opening detector,
and room extractor produce.
"""
import sys
import json
import math
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent.parent
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

import cv2
import numpy as np
from app.processors.wall_detector import detect_walls
from app.processors.opening_detector import detect_openings
from app.processors.room_extractor import extract_rooms
from app.utils.image_preprocessing import load_image, preprocess_floorplan

OUT_DIR = Path(__file__).resolve().parent / 'diagnostic_output'
OUT_DIR.mkdir(exist_ok=True)


def find_test_image() -> bytes:
    candidates = [
        _PKG_ROOT.parent.parent / 'apps' / 'api' / 'data' / 'uploads',
        _PKG_ROOT / 'tests' / 'fixtures',
    ]
    for d in candidates:
        if d.exists():
            images = sorted(d.glob('*.jpg')) + sorted(d.glob('*.png'))
            if images:
                print(f"  Using test image: {images[0]}")
                return images[0].read_bytes()
    raise FileNotFoundError("No test image found")


def draw_walls_overlay(canvas, walls, color=(0, 0, 255), thickness=2):
    """Draw wall segments on canvas as red lines."""
    for w in walls:
        pt1 = (int(w['start']['x']), int(w['start']['y']))
        pt2 = (int(w['end']['x']), int(w['end']['y']))
        cv2.line(canvas, pt1, pt2, color, thickness)
        # Mark endpoints
        cv2.circle(canvas, pt1, 4, (255, 0, 0), -1)
        cv2.circle(canvas, pt2, 4, (255, 0, 0), -1)
    return canvas


def draw_openings_overlay(canvas, openings, walls, color_door=(0, 200, 0), color_window=(200, 200, 0)):
    """Draw openings as circles on their host wall positions."""
    wall_map = {w.get('id', ''): w for w in walls}
    for o in openings:
        wid = o.get('wall_id', '')
        w = wall_map.get(wid)
        if not w:
            continue
        t = o['position']
        sx, sy = w['start']['x'], w['start']['y']
        ex, ey = w['end']['x'], w['end']['y']
        px = int(sx + t * (ex - sx))
        py = int(sy + t * (ey - sy))
        color = color_door if o['type'] == 'door' else color_window
        cv2.circle(canvas, (px, py), 8, color, 2)
        cv2.putText(canvas, o['type'][0].upper(), (px - 5, py + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    return canvas


def draw_rooms_overlay(canvas, rooms, color=(200, 100, 50)):
    """Draw room polygons and centroid labels."""
    for r in rooms:
        pts = np.array([[int(p['x']), int(p['y'])] for p in r['polygon']], dtype=np.int32)
        if len(pts) >= 3:
            cv2.polylines(canvas, [pts], isClosed=True, color=color, thickness=2)
            cx = int(sum(p['x'] for p in r['polygon']) / len(r['polygon']))
            cy = int(sum(p['y'] for p in r['polygon']) / len(r['polygon']))
            cv2.putText(canvas, r['label'], (cx - 30, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    return canvas


def main():
    print("=" * 70)
    print("FLOOR PLAN PARSING DIAGNOSTIC")
    print("=" * 70)

    # Load image
    image_bytes = find_test_image()
    img = load_image(image_bytes)
    print(f"\n[INPUT] Image shape: {img.shape}")

    # Preprocess
    prep = preprocess_floorplan(img)
    wall_mask = prep['wall_mask']
    binary = prep['binary']
    scale = prep.get('scale', 1.0)
    print(f"[PREPROCESS] Scale factor: {scale:.3f}")
    print(f"[PREPROCESS] Wall mask shape: {wall_mask.shape}, non-zero pixels: {cv2.countNonZero(wall_mask)}")

    # Save masks
    cv2.imwrite(str(OUT_DIR / '1_wall_mask.png'), wall_mask)
    cv2.imwrite(str(OUT_DIR / '1_binary.png'), binary)
    print(f"  Saved: 1_wall_mask.png, 1_binary.png")

    # ===== STEP 1: WALL DETECTION =====
    print(f"\n{'='*50}")
    print("STEP 1: WALL DETECTION")
    print(f"{'='*50}")
    walls_raw = detect_walls(wall_mask, [])
    print(f"  Walls detected: {len(walls_raw)}")
    for i, w in enumerate(walls_raw):
        length = math.hypot(w['end']['x'] - w['start']['x'], w['end']['y'] - w['start']['y'])
        print(f"  Wall {i}: ({w['start']['x']:.0f},{w['start']['y']:.0f}) -> "
              f"({w['end']['x']:.0f},{w['end']['y']:.0f}) len={length:.0f} thick={w['thickness']:.0f}")

    # Scale walls
    walls_formatted = []
    for i, w in enumerate(walls_raw):
        walls_formatted.append({
            'id': f'w{i+1}',
            'start': {'x': round(w['start']['x'] * scale, 1), 'y': round(w['start']['y'] * scale, 1)},
            'end': {'x': round(w['end']['x'] * scale, 1), 'y': round(w['end']['y'] * scale, 1)},
            'thickness': w.get('thickness', 12.0),
            'height': 270.0,
            'type': 'interior',
        })

    # Draw walls overlay
    canvas_walls = cv2.cvtColor(wall_mask, cv2.COLOR_GRAY2BGR)
    draw_walls_overlay(canvas_walls, walls_raw)
    cv2.imwrite(str(OUT_DIR / '2_walls_overlay.png'), canvas_walls)
    print(f"  Saved: 2_walls_overlay.png")

    # ===== STEP 2: OPENING DETECTION =====
    print(f"\n{'='*50}")
    print("STEP 2: OPENING (DOOR/WINDOW) DETECTION")
    print(f"{'='*50}")
    openings_raw = detect_openings(img, None, walls_formatted, wall_mask=wall_mask)
    doors = [o for o in openings_raw if o['type'] == 'door']
    windows = [o for o in openings_raw if o['type'] == 'window']
    print(f"  Total openings: {len(openings_raw)} (doors={len(doors)}, windows={len(windows)})")
    for o in openings_raw:
        print(f"    {o['type']:7s} on wall={o['wall_id']:4s} pos={o['position']:.3f} "
              f"width={o['width']:.0f}")

    # Draw openings overlay
    canvas_openings = cv2.cvtColor(wall_mask, cv2.COLOR_GRAY2BGR)
    draw_walls_overlay(canvas_openings, walls_raw, color=(150, 150, 150))
    draw_openings_overlay(canvas_openings, openings_raw, walls_formatted)
    cv2.imwrite(str(OUT_DIR / '3_openings_overlay.png'), canvas_openings)
    print(f"  Saved: 3_openings_overlay.png")

    # ===== STEP 3: ROOM EXTRACTION =====
    print(f"\n{'='*50}")
    print("STEP 3: ROOM POLYGON EXTRACTION")
    print(f"{'='*50}")
    rooms_raw = extract_rooms(binary, [])
    print(f"  Rooms extracted: {len(rooms_raw)}")
    for r in rooms_raw:
        print(f"    {r['label']:15s} area={r['area']:6.2f}m²  polygon_pts={len(r['polygon'])}")

    # Scale room polygons
    for r in rooms_raw:
        r['polygon'] = [
            {'x': round(p['x'] * scale, 1), 'y': round(p['y'] * scale, 1)}
            for p in r['polygon']
        ]

    # Draw rooms overlay
    canvas_rooms = cv2.cvtColor(wall_mask, cv2.COLOR_GRAY2BGR)
    draw_walls_overlay(canvas_rooms, walls_raw, color=(150, 150, 150))
    draw_rooms_overlay(canvas_rooms, rooms_raw)
    cv2.imwrite(str(OUT_DIR / '4_rooms_overlay.png'), canvas_rooms)
    print(f"  Saved: 4_rooms_overlay.png")

    # ===== COMBINED OVERLAY =====
    canvas_combined = img.copy()
    if scale != 1.0:
        h, w = wall_mask.shape[:2]
        canvas_combined = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    draw_walls_overlay(canvas_combined, walls_raw, color=(0, 0, 255), thickness=2)
    draw_openings_overlay(canvas_combined, openings_raw, walls_formatted)
    draw_rooms_overlay(canvas_combined, rooms_raw)
    cv2.imwrite(str(OUT_DIR / '5_combined_overlay.png'), canvas_combined)
    print(f"\n  Saved: 5_combined_overlay.png (FINAL combined overlay)")

    # Save JSON report
    report = {
        'image_shape': list(img.shape),
        'scale': scale,
        'walls_count': len(walls_raw),
        'openings_count': len(openings_raw),
        'doors_count': len(doors),
        'windows_count': len(windows),
        'rooms_count': len(rooms_raw),
        'walls': walls_formatted,
        'openings': openings_raw,
        'rooms': rooms_raw,
    }
    with open(OUT_DIR / 'diagnostic_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"  Saved: diagnostic_report.json")

    print(f"\n{'='*70}")
    print(f"DIAGNOSTIC COMPLETE — All output in: {OUT_DIR}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
