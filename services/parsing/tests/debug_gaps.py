"""Quick debug: sample along each wall line on the wall_mask and print
the gap pattern to understand why detect_openings finds 0 gaps."""
import sys
import math
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent.parent
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

import cv2
import numpy as np
from app.processors.wall_detector import detect_walls
from app.utils.image_preprocessing import load_image, preprocess_floorplan


def main():
    # Load
    img_path = sorted(
        (_PKG_ROOT.parent.parent / 'apps' / 'api' / 'data' / 'uploads').glob('*.jpg')
    )[0]
    img = load_image(img_path.read_bytes())
    prep = preprocess_floorplan(img)
    wall_mask = prep['wall_mask']
    scale = prep.get('scale', 1.0)

    walls_raw = detect_walls(wall_mask, [])
    walls_fmt = []
    for i, w in enumerate(walls_raw):
        walls_fmt.append({
            'id': f'w{i+1}',
            'start': {'x': round(w['start']['x'] * scale, 1), 'y': round(w['start']['y'] * scale, 1)},
            'end': {'x': round(w['end']['x'] * scale, 1), 'y': round(w['end']['y'] * scale, 1)},
        })

    h_img, w_img = wall_mask.shape[:2]
    print(f"Wall mask shape: {wall_mask.shape}, dtype: {wall_mask.dtype}")
    print(f"Non-zero pixels: {cv2.countNonZero(wall_mask)}")
    print(f"Mean pixel value: {np.mean(wall_mask):.1f}")
    print()

    for wall in walls_fmt:
        wid = wall['id']
        sx, sy = wall['start']['x'], wall['start']['y']
        ex, ey = wall['end']['x'], wall['end']['y']
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy)
        if length < 50:
            continue

        num_samples = max(2, int(length))
        samples = []
        for i in range(num_samples):
            t = i / num_samples
            px = int(min(w_img - 1, max(0, sx + t * dx)))
            py = int(min(h_img - 1, max(0, sy + t * dy)))
            samples.append(wall_mask[py, px] > 0)

        # Count gaps
        gaps = []
        gap_start = None
        for i, is_wall in enumerate(samples):
            if not is_wall and gap_start is None:
                gap_start = i
            elif is_wall and gap_start is not None:
                gaps.append((gap_start, i, i - gap_start))
                gap_start = None

        wall_pct = sum(samples) / len(samples) * 100
        pattern = ''.join('█' if s else '·' for s in samples)
        # Show condensed pattern (every 3rd sample)
        condensed = ''.join('#' if s else '.' for i, s in enumerate(samples) if i % 3 == 0)

        print(f"{wid} ({sx:.0f},{sy:.0f})->({ex:.0f},{ey:.0f}) len={length:.0f} "
              f"wall%={wall_pct:.0f}% gaps={len(gaps)}")
        for gs, ge, gl in gaps:
            t_gs = gs / num_samples
            t_ge = ge / num_samples
            print(f"  gap: samples[{gs}:{ge}] len={gl}px t={t_gs:.3f}-{t_ge:.3f}")
        if len(condensed) <= 80:
            print(f"  pattern: {condensed}")
        else:
            print(f"  pattern: {condensed[:40]}...{condensed[-40:]}")
        print()


if __name__ == '__main__':
    main()
