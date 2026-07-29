import math
import cv2
import numpy as np


def detect_openings(
    image: np.ndarray,
    detections: list[dict] | None = None,
    walls: list[dict] | None = None,
    class_map: dict | None = None,
    wall_mask: np.ndarray | None = None,
) -> list[dict]:
    """
    Detect openings (doors & windows) and project them onto host wall segments.
    Uses AI detections if available, or CV arc/line analysis on wall gaps.
    """
    if not walls:
        return []

    openings = []
    door_class = (class_map or {}).get('door', 1)
    window_class = (class_map or {}).get('window', 2)

    if detections:
        for d in detections:
            cls = d.get('class_id')
            label = d.get('label')
            is_door = cls == door_class or label == 'door'
            is_window = cls == window_class or label == 'window'

            if not (is_door or is_window):
                continue

            x1, y1, x2, y2 = d['bbox']
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            width = max(30.0, float(max(abs(x2 - x1), abs(y2 - y1))))

            wall_id, position = _find_nearest_wall(cx, cy, walls)
            if not wall_id:
                continue

            openings.append({
                'type': 'door' if is_door else 'window',
                'wall_id': wall_id,
                'position': round(position, 3),
                'width': round(width, 2),
                'height': 210.0 if is_door else 120.0,
                'sill_height': 0.0 if is_door else 90.0,
                'swing_direction': 'inward' if is_door else None,
            })
    else:
        # Fallback: wall-gap analysis with perpendicular verification
        openings = _detect_openings_from_cv(image, walls, wall_mask=wall_mask)

    return openings


def _detect_openings_from_cv(image: np.ndarray, walls: list[dict], wall_mask: np.ndarray | None = None) -> list[dict]:
    """Detects openings (doors & windows) via wall-gap analysis only.

    HoughCircles has been intentionally removed — it produced massive
    false-positive counts by matching round furniture (chairs, toilets, sinks).
    Instead we rely purely on wall-gap scanning with perpendicular verification
    to distinguish real openings from furniture texture crossing the wall line.
    """
    # Use preprocessed wall_mask if available (much cleaner than re-thresholding
    # the raw color image, which picks up furniture/text noise).
    if wall_mask is not None:
        binary = wall_mask.copy()
    else:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        if np.mean(gray) > 127:
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            binary = gray.copy()

    h_img, w_img = binary.shape[:2]

    # Pre-compute exterior wall IDs: walls whose midpoint is within 15px of any image border.
    _border_margin = 15
    exterior_wall_ids = set()
    for wall in walls:
        sx, sy = wall['start']['x'], wall['start']['y']
        ex, ey = wall['end']['x'], wall['end']['y']
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        if mx < _border_margin or mx > w_img - _border_margin or my < _border_margin or my > h_img - _border_margin:
            exterior_wall_ids.add(wall.get('id', ''))

    openings = []
    seen_keys = set()

    for wall in walls:
        wall_id = wall.get('id', '')
        sx, sy = wall['start']['x'], wall['start']['y']
        ex, ey = wall['end']['x'], wall['end']['y']
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy)
        if length < 50.0:
            continue

        # Unit vectors along and perpendicular to the wall.
        ux, uy = dx / length, dy / length
        # Perpendicular direction (rotate 90°).
        nx, ny = -uy, ux

        # Sample along the wall center-line at 1px resolution.
        num_samples = max(2, int(length))
        samples = []
        for i in range(num_samples):
            t = i / num_samples
            px = int(min(w_img - 1, max(0, sx + t * dx)))
            py = int(min(h_img - 1, max(0, sy + t * dy)))
            samples.append(binary[py, px] > 0)

        # Scan for gaps (stretches of False) in the wall sample line.
        gap_start = None
        for i, is_wall_pixel in enumerate(samples):
            if not is_wall_pixel and gap_start is None:
                gap_start = i
            elif is_wall_pixel and gap_start is not None:
                gap_len = i - gap_start

                # Only consider gaps in a realistic door/window width range.
                if 10 <= gap_len <= 120:
                    # --- Verification 1: wall continuity on at least ONE side ---
                    # Require at least 3 contiguous wall pixels on at least one
                    # side of the gap. Gaps at the very start/end of a detected
                    # segment are still valid if one side has wall continuity.
                    min_wall_run = 3
                    left_ok = (gap_start >= min_wall_run and
                               all(samples[gap_start - k - 1] for k in range(min(min_wall_run, gap_start))))
                    right_ok = (i + min_wall_run <= num_samples and
                                all(samples[i + k] for k in range(min(min_wall_run, num_samples - i))))

                    if not (left_ok or right_ok):
                        gap_start = None
                        continue

                    # --- Verification 2: perpendicular clearance ---
                    # A real opening has clear space on at least one side
                    # perpendicular to the wall. Furniture crossing the wall
                    # line has dark pixels (wall material) on both sides.
                    t_mid = (gap_start + i) / (2.0 * num_samples)
                    mid_px = sx + t_mid * dx
                    mid_py = sy + t_mid * dy

                    perp_clear = 0
                    perp_check_dist = 10  # Sample 10px each side
                    for sign in [1, -1]:
                        clear_count = 0
                        for d in range(2, perp_check_dist + 1):
                            cpx = int(min(w_img - 1, max(0, mid_px + sign * d * nx)))
                            cpy = int(min(h_img - 1, max(0, mid_py + sign * d * ny)))
                            if binary[cpy, cpx] == 0:  # No wall material
                                clear_count += 1
                        if clear_count >= (perp_check_dist - 1) * 0.3:
                            perp_clear += 1

                    if perp_clear == 0:
                        # Both sides have wall-like material => not a real opening
                        gap_start = None
                        continue

                    # --- Classify: exterior wall gap = window, interior = door ---
                    is_exterior = wall_id in exterior_wall_ids
                    is_window = is_exterior and gap_len < 50
                    opening_type = 'window' if is_window else 'door'

                    key = (wall_id, round(t_mid, 1))
                    if key not in seen_keys:
                        seen_keys.add(key)
                        openings.append({
                            'type': opening_type,
                            'wall_id': wall_id,
                            'position': round(t_mid, 3),
                            'width': round(gap_len * 1.5, 2),
                            'height': 120.0 if is_window else 210.0,
                            'sill_height': 90.0 if is_window else 0.0,
                            'swing_direction': None if is_window else 'inward',
                        })

                gap_start = None

    return openings


def _find_nearest_wall(cx: float, cy: float, walls: list[dict]) -> tuple[str, float]:
    best_wall = None
    best_dist = float('inf')
    best_pos = 0.5

    for w in walls:
        wall_id = w.get('id', '')
        sx, sy = w['start']['x'], w['start']['y']
        ex, ey = w['end']['x'], w['end']['y']

        dx, dy = ex - sx, ey - sy
        length_sq = dx * dx + dy * dy
        if length_sq < 1e-3:
            continue

        t = max(0.0, min(1.0, ((cx - sx) * dx + (cy - sy) * dy) / length_sq))
        px = sx + t * dx
        py = sy + t * dy
        dist = math.hypot(cx - px, cy - py)

        if dist < best_dist and dist <= 25.0:  # Tightened max distance threshold from 80 to 25
            best_dist = dist
            best_wall = wall_id
            best_pos = t

    return best_wall or '', best_pos

