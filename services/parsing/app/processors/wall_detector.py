import math
import cv2
import numpy as np


def detect_walls(
    image: np.ndarray,
    detections: list[dict] | None = None,
    class_map: dict | None = None,
) -> list[dict]:
    """
    Detect structural walls from a preprocessed floor plan image.
    Uses AI detections if available; otherwise performs LSD / Hough vectorization
    on the *full* wall structure, orthogonal snapping, junction merging,
    collinear consolidation, and a connectivity filter that drops furniture
    lines while keeping real interior partitions.
    """
    if detections:
        model_walls = _detect_from_model(detections, class_map or {})
        if model_walls:
            return model_walls

    return _detect_from_image_vectorization(image)


def _detect_from_model(detections: list[dict], class_map: dict) -> list[dict]:
    wall_class = class_map.get('wall', 0)
    walls = []
    for d in detections:
        if d.get('class_id') == wall_class or d.get('label') == 'wall':
            x1, y1, x2, y2 = d['bbox']
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            thickness = min(dx, dy) if min(dx, dy) > 0 else 10.0

            # Orient long axis
            if dx > dy:
                start = {'x': float(x1), 'y': float((y1 + y2) / 2)}
                end = {'x': float(x2), 'y': float((y1 + y2) / 2)}
            else:
                start = {'x': float((x1 + x2) / 2), 'y': float(y1)}
                end = {'x': float((x1 + x2) / 2), 'y': float(y2)}

            walls.append({
                'start': start,
                'end': end,
                'thickness': max(5.0, float(thickness)),
            })
    return walls


def _detect_from_image_vectorization(image: np.ndarray) -> list[dict]:
    """Vectorize the full wall network preserved by the new preprocessor.

    The old pipeline ran a 15x3 / 3x15 morphological OPENING here, which
    erased thin interior partitions and left only the outer shell. We now
    receive a mask that retains ALL walls, so we must instead *suppress
    furniture* via a connectivity filter rather than by erosion.
    """
    # The input is already an inverted binary (walls = 255) from the
    # preprocessor. Normalise to be safe.
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Walls should already be white (255). Guard against a non-inverted input.
    if np.mean(gray) > 127:
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        binary = gray.copy()

    # === Stage 1: emphasise long straight runs (suppress furniture noise)
    # without deleting partitions. A *light* directional open keeps walls
    # >= ~9px of contiguous straight pixels; real partitions easily survive,
    # but isolated scribbles/dashes from furniture textures are removed.
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 9))
    horiz_walls = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_h)
    vert_walls = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_v)
    struct_mask = cv2.bitwise_or(horiz_walls, vert_walls)

    # Reconnect junctions eroded by the open.
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    struct_mask = cv2.dilate(struct_mask, kernel_dilate, iterations=1)

    # Fall back to the raw mask if directional filtering removed too much
    # (e.g. a plan dominated by diagonal walls).
    if np.count_nonzero(struct_mask) > 200:
        target_mask = struct_mask
    else:
        target_mask = binary

    # === Stage 2: skeletonize -> 1px centerlines (handles L / T / + junctions)
    skeleton = _morphological_skeleton(target_mask)

    # === Stage 3: Hough line segments on the skeleton
    raw_segments = []
    lines = cv2.HoughLinesP(
        skeleton, rho=1, theta=np.pi / 180,
        threshold=15, minLineLength=20, maxLineGap=12,
    )
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = math.hypot(x2 - x1, y2 - y1)
            if length >= 15.0:
                raw_segments.append({
                    'x1': float(x1), 'y1': float(y1),
                    'x2': float(x2), 'y2': float(y2),
                    'length': length,
                })

    # Fallback: supplement with LSD if Hough yields too few walls.
    if len(raw_segments) < 4:
        lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
        lsd_lines, _, _, _ = lsd.detect(target_mask)
        if lsd_lines is not None:
            for line in lsd_lines:
                x1, y1, x2, y2 = line[0]
                length = math.hypot(x2 - x1, y2 - y1)
                if length >= 20.0:
                    raw_segments.append({
                        'x1': float(x1), 'y1': float(y1),
                        'x2': float(x2), 'y2': float(y2),
                        'length': length,
                    })

    if not raw_segments:
        return []

    # === Stage 4: orthogonal snapping
    snapped_segments = [_snap_orthogonal(seg, angle_tolerance_deg=10.0) for seg in raw_segments]

    # === Stage 5: junction merging
    junction_segments = _merge_junction_nodes(snapped_segments, snap_radius=25.0)

    # === Stage 6: connectivity filter — keep walls that touch the connected
    # wall network, drop isolated furniture rectangles / floating artifacts.
    connected_segments = _filter_by_network_connectivity(
        junction_segments, snap_dist=25.0, min_isolated_length=60.0
    )

    if not connected_segments:  # don't let an aggressive filter nuke everything
        connected_segments = [
            s for s in junction_segments
            if math.hypot(s['x2'] - s['x1'], s['y2'] - s['y1']) >= 30.0
        ]

    # === Stage 7: collinear consolidation (multiple passes for full merge)
    consolidated_walls = connected_segments
    for _ in range(5):
        prev_count = len(consolidated_walls)
        consolidated_walls = _merge_collinear_segments(consolidated_walls, max_dist=35.0)
        if len(consolidated_walls) == prev_count:
            break

    # === Stage 7B: remove near-duplicate walls
    consolidated_walls = _remove_duplicate_walls(consolidated_walls, threshold=25.0)

    # === Stage 7C: drop short fragments (furniture edges surviving merge)
    consolidated_walls = [
        w for w in consolidated_walls
        if math.hypot(w['x2'] - w['x1'], w['y2'] - w['y1']) >= 30.0
    ]

    # === Stage 8: wall thickness estimation
    dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    final_walls = []
    for wall in consolidated_walls:
        thickness = _estimate_wall_thickness(wall, dist_transform)
        final_walls.append({
            'start': {'x': round(wall['x1'], 1), 'y': round(wall['y1'], 1)},
            'end': {'x': round(wall['x2'], 1), 'y': round(wall['y2'], 1)},
            'thickness': round(max(8.0, min(30.0, thickness)), 1),
        })

    return final_walls


def _filter_by_network_connectivity(
    segments: list[dict], snap_dist: float = 25.0, min_isolated_length: float = 60.0,
) -> list[dict]:
    """Keep segments that are part of the connected wall network.

    A segment survives if at least one of its endpoints touches another
    segment within `snap_dist`. A segment touching *nothing* survives only if
    it is long enough to plausibly be a real standalone wall — this drops
    short furniture fragments while avoiding the old approach of deleting
    every short line (which also deleted real partitions at door gaps).
    """
    if not segments:
        return segments

    output = []
    for i, s1 in enumerate(segments):
        x1, y1, x2, y2 = s1['x1'], s1['y1'], s1['x2'], s1['y2']
        length = math.hypot(x2 - x1, y2 - y1)

        conn1 = False
        conn2 = False
        for j, s2 in enumerate(segments):
            if i == j:
                continue
            p1_near = (
                math.hypot(x1 - s2['x1'], y1 - s2['y1']) <= snap_dist
                or math.hypot(x1 - s2['x2'], y1 - s2['y2']) <= snap_dist
            )
            p2_near = (
                math.hypot(x2 - s2['x1'], y2 - s2['y1']) <= snap_dist
                or math.hypot(x2 - s2['x2'], y2 - s2['y2']) <= snap_dist
            )
            if p1_near:
                conn1 = True
            if p2_near:
                conn2 = True

        # Drop only if BOTH ends are disconnected AND it's short.
        if (not conn1 and not conn2) and length < min_isolated_length:
            continue

        output.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'length': length})

    return output


def _remove_duplicate_walls(segments: list[dict], threshold: float = 15.0) -> list[dict]:
    """Remove near-duplicate wall segments (endpoints within threshold of each other)."""
    if not segments:
        return segments

    result = []
    used = [False] * len(segments)

    for i in range(len(segments)):
        if used[i]:
            continue
        best = segments[i]
        best_len = math.hypot(best['x2'] - best['x1'], best['y2'] - best['y1'])

        for j in range(i + 1, len(segments)):
            if used[j]:
                continue
            other = segments[j]

            # Check if endpoints are close (in either orientation)
            d1 = math.hypot(best['x1'] - other['x1'], best['y1'] - other['y1']) + \
                 math.hypot(best['x2'] - other['x2'], best['y2'] - other['y2'])
            d2 = math.hypot(best['x1'] - other['x2'], best['y1'] - other['y2']) + \
                 math.hypot(best['x2'] - other['x1'], best['y2'] - other['y1'])

            if min(d1, d2) < threshold * 2:
                used[j] = True
                # Keep the longer one
                other_len = math.hypot(other['x2'] - other['x1'], other['y2'] - other['y1'])
                if other_len > best_len:
                    best = other
                    best_len = other_len

        result.append(best)

    return result


def _morphological_skeleton(binary_mask: np.ndarray) -> np.ndarray:
    """
    Compute morphological skeleton (medial axis) of a binary mask.
    Produces 1-pixel-wide lines along the center of wall structures.
    """
    skeleton = np.zeros_like(binary_mask)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    img = binary_mask.copy()

    while True:
        eroded = cv2.erode(img, element)
        opened = cv2.dilate(eroded, element)
        diff = cv2.subtract(img, opened)
        skeleton = cv2.bitwise_or(skeleton, diff)
        img = eroded.copy()
        if cv2.countNonZero(img) == 0:
            break

    return skeleton


def _snap_orthogonal(seg: dict, angle_tolerance_deg: float = 8.0) -> dict:
    x1, y1, x2, y2 = seg['x1'], seg['y1'], seg['x2'], seg['y2']
    dx = x2 - x1
    dy = y2 - y1
    angle = math.degrees(math.atan2(dy, dx)) % 180

    # Horizontal snap (0 / 180)
    if angle <= angle_tolerance_deg or angle >= (180 - angle_tolerance_deg):
        mid_y = (y1 + y2) / 2
        return {'x1': x1, 'y1': mid_y, 'x2': x2, 'y2': mid_y}

    # Vertical snap (90)
    if abs(angle - 90) <= angle_tolerance_deg:
        mid_x = (x1 + x2) / 2
        return {'x1': mid_x, 'y1': y1, 'x2': mid_x, 'y2': y2}

    # 45 diagonal snap
    if abs(angle - 45) <= angle_tolerance_deg or abs(angle - 135) <= angle_tolerance_deg:
        dist = (abs(dx) + abs(dy)) / 2
        sign_x = 1 if dx >= 0 else -1
        sign_y = 1 if dy >= 0 else -1
        return {'x1': x1, 'y1': y1, 'x2': x1 + sign_x * dist, 'y2': y1 + sign_y * dist}

    return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}


def _merge_junction_nodes(segments: list[dict], snap_radius: float = 15.0) -> list[dict]:
    """Clusters endpoints within snap_radius into unified junction coordinates."""
    nodes = []
    for s in segments:
        nodes.append([s['x1'], s['y1']])
        nodes.append([s['x2'], s['y2']])

    if not nodes:
        return segments

    nodes = np.array(nodes)
    clustered_nodes = np.copy(nodes)

    # Simple greedy clustering
    n = len(nodes)
    visited = np.zeros(n, dtype=bool)

    for i in range(n):
        if visited[i]:
            continue
        dists = np.hypot(nodes[:, 0] - nodes[i, 0], nodes[:, 1] - nodes[i, 1])
        neighbors = np.where(dists <= snap_radius)[0]
        visited[neighbors] = True
        avg_point = np.mean(nodes[neighbors], axis=0)
        clustered_nodes[neighbors] = avg_point

    merged = []
    for i, s in enumerate(segments):
        p1 = clustered_nodes[2 * i]
        p2 = clustered_nodes[2 * i + 1]
        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        if length >= 15.0:  # Filter collapsed line segments
            merged.append({'x1': float(p1[0]), 'y1': float(p1[1]), 'x2': float(p2[0]), 'y2': float(p2[1])})

    return merged


def _merge_collinear_segments(segments: list[dict], max_dist: float = 20.0) -> list[dict]:
    """Merges collinear horizontal and vertical segments."""
    horiz = []
    vert = []
    diag = []

    for s in segments:
        if abs(s['y1'] - s['y2']) < 1e-3:
            x_min, x_max = min(s['x1'], s['x2']), max(s['x1'], s['x2'])
            horiz.append({'y': s['y1'], 'x1': x_min, 'x2': x_max})
        elif abs(s['x1'] - s['x2']) < 1e-3:
            y_min, y_max = min(s['y1'], s['y2']), max(s['y1'], s['y2'])
            vert.append({'x': s['x1'], 'y1': y_min, 'y2': y_max})
        else:
            diag.append(s)

    # Merge horizontal
    merged_horiz = []
    horiz.sort(key=lambda item: (item['y'], item['x1']))
    for h in horiz:
        merged = False
        for mh in merged_horiz:
            if abs(mh['y'] - h['y']) <= max_dist and not (h['x1'] > mh['x2'] + max_dist or h['x2'] < mh['x1'] - max_dist):
                mh['x1'] = min(mh['x1'], h['x1'])
                mh['x2'] = max(mh['x2'], h['x2'])
                mh['y'] = (mh['y'] + h['y']) / 2
                merged = True
                break
        if not merged:
            merged_horiz.append(dict(h))

    # Merge vertical
    merged_vert = []
    vert.sort(key=lambda item: (item['x'], item['y1']))
    for v in vert:
        merged = False
        for mv in merged_vert:
            if abs(mv['x'] - v['x']) <= max_dist and not (v['y1'] > mv['y2'] + max_dist or v['y2'] < mv['y1'] - max_dist):
                mv['y1'] = min(mv['y1'], v['y1'])
                mv['y2'] = max(mv['y2'], v['y2'])
                mv['x'] = (mv['x'] + v['x']) / 2
                merged = True
                break
        if not merged:
            merged_vert.append(dict(v))

    result = []
    for h in merged_horiz:
        result.append({'x1': h['x1'], 'y1': h['y'], 'x2': h['x2'], 'y2': h['y']})
    for v in merged_vert:
        result.append({'x1': v['x'], 'y1': v['y1'], 'x2': v['x'], 'y2': v['y2']})
    result.extend(diag)

    return result


def _estimate_wall_thickness(wall: dict, dist_transform: np.ndarray) -> float:
    h, w = dist_transform.shape[:2]
    mid_x = int(_clamp((wall['x1'] + wall['x2']) / 2, 0, w - 1))
    mid_y = int(_clamp((wall['y1'] + wall['y2']) / 2, 0, h - 1))

    dist_val = float(dist_transform[mid_y, mid_x])
    thickness = dist_val * 2.0
    return max(8.0, min(40.0, thickness if thickness > 2.0 else 12.0))


def _clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))
