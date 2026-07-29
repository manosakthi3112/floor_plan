import math
import cv2
import numpy as np


def extract_rooms(
    image: np.ndarray,
    walls: list[dict],
    min_area: float = 1500.0,
) -> list[dict]:
    """
    Extract closed room polygons.

    The previous implementation ran a 7x7 morphological OPENING (erode-then-
    dilate) that erased every thin interior partition wall, leaving only the
    outer shell. With only the shell present, the whole interior was a single
    blob bigger than the 70% area cap, so it returned ZERO rooms.

    New strategy — flood-fill segmentation on the sealed wall mask:
      1. Re-threshold to a clean inverted binary (walls = white).
      2. Seal door/window gaps with an adaptive morphological closing whose
         kernel scales with the image (~6% of the short edge). A fixed 55x55
         kernel bridged some gaps but over-merged on small plans and failed
         on large ones.
      3. Add an image border so rooms touching the edge are enclosed.
      4. Flood-fill from a border seed to label the EXTERIOR.
      5. Interior = NOT(walls) AND NOT(exterior) -> one component per room.
      6. approxPolyDP for clean >=3-point polygons.
    """
    h, w = image.shape[:2]

    # _extract_via_flood_fill returns (polygon, component_area) tuples.
    # We filter on the connected-component pixel area — NOT on the polygon's
    # shoelace area — because a room that touches the image border has its
    # contour traced along the border we drew, which inflates the polygon area
    # to ~the whole image and would wrongly drop a perfectly good room.
    rooms_polygons = _extract_via_flood_fill(image, w, h)

    total_image_area = float(w * h)

    valid_rooms = []
    for polygon, comp_area in rooms_polygons:
        # Drop tiny fragments and obvious failures (a single component
        # occupying >85% of the plan means the wall seal failed and the whole
        # interior leaked together).
        if min_area <= comp_area <= (total_image_area * 0.85):
            valid_rooms.append((polygon, comp_area))

    valid_rooms.sort(key=lambda item: item[1], reverse=True)

    result = []
    for i, (polygon, area) in enumerate(valid_rooms):
        # Geometric heuristic as a default label; OCR (if available) overwrites
        # this later in the orchestrator. We intentionally do NOT assign
        # "Living Room / Bedroom / ..." purely by area rank anymore — that was
        # arbitrary and ignored the actual room shapes.
        label = _guess_room_type(polygon, area, total_image_area) or f'Room {i + 1}'
        result.append({
            'id': f'r{i + 1}',
            'label': label,
            'polygon': [{'x': float(round(p[0], 1)), 'y': float(round(p[1], 1))} for p in polygon],
            'level': 0,
            'area': round(area / 10000.0, 2),  # Scale estimated area
        })

    return result


def _extract_via_flood_fill(
    image: np.ndarray, w: int, h: int
) -> list[tuple[list[tuple[float, float]], int]]:
    """Seal walls, flood-fill the exterior, and return interior room polygons.

    Returns a list of (polygon, component_area) tuples. `component_area` is the
    connected-component pixel count, which is the reliable measure of room size
    (the polygon's shoelace area is unreliable when a room touches the border).
    """
    # 1. Clean inverted binary (walls = white). The input is already inverted
    # from the preprocessor, but guard against a non-inverted input.
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    if np.mean(gray) > 127:
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        binary = gray.copy()

    # 2. Adaptive closing kernel. The kernel must be large enough to bridge a
    # door-width gap but not so large it merges neighbouring rooms. 9% of
    # the short edge bridges typical doors (~35px on a 414px image) while
    # preserving the Living-Kitchen partition wall.
    short_edge = min(w, h)
    close_size = int(np.clip(round(short_edge * 0.09), 19, 55))
    # Must be odd for a symmetric structuring element.
    if close_size % 2 == 0:
        close_size += 1
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (close_size, close_size))

    # Thicken walls before closing so thin partition lines survive the close.
    kernel_thicken = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thick = cv2.dilate(binary, kernel_thicken, iterations=2)
    sealed = cv2.morphologyEx(thick, cv2.MORPH_CLOSE, kernel_close)

    # 3. Enclose the image border so edge rooms are closed regions.
    border_thickness = max(6, int(short_edge * 0.01))
    cv2.rectangle(sealed, (0, 0), (w - 1, h - 1), 255, border_thickness)

    # 4. Flood-fill from the border to mark the EXTERIOR.
    flood = sealed.copy()
    flood_mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(flood, flood_mask, (0, 0), 0)

    # 5. Interior = NOT wall AND NOT exterior.
    not_wall = cv2.bitwise_not(sealed)
    not_exterior = cv2.bitwise_not(flood)
    interior = cv2.bitwise_and(not_wall, not_exterior)

    # Light open to split rooms that are only touching by a 1px thread
    # (happens when two rooms share a wall that was thinned by erosion).
    interior = cv2.morphologyEx(
        interior, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    )

    # 6. Connected components -> individual rooms.
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(interior)

    total_area = float(w * h)
    rooms: list[tuple[list[tuple[float, float]], int]] = []

    for i in range(1, num_labels):  # skip background (0)
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 800 or area > (total_area * 0.85):
            continue

        comp_mask = np.uint8(labels == i) * 255
        contours, _ = cv2.findContours(comp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue

        cnt = max(contours, key=cv2.contourArea)
        # Douglas-Peucker simplification for a clean orthogonal-ish polygon.
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        pts = [(float(p[0][0]), float(p[0][1])) for p in approx]

        if len(pts) >= 3:
            # --- Convexity & bounding-rect filter ---
            # Real rooms have a convexity ratio > 0.5 (polygon area /
            # convex hull area). Jagged furniture-outline polygons fail this.
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            cnt_area = cv2.contourArea(cnt)
            convexity = cnt_area / hull_area if hull_area > 0 else 0
            if convexity < 0.45:
                continue

            # Both bounding-rect dimensions must be >= 40px to be a real room
            bx, by, bw, bh = cv2.boundingRect(cnt)
            if bw < 40 or bh < 40:
                continue

            rooms.append((pts, int(area)))

    return rooms


def _polygon_area(polygon: list[tuple[float, float]]) -> float:
    if len(polygon) < 3:
        return 0.0
    area = 0.0
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def _guess_room_type(polygon: list[tuple[float, float]], area_px: float, total_area: float = 0.0) -> str:
    """Coarse geometric label used only as a fallback before OCR runs."""
    if len(polygon) < 3 or total_area <= 0:
        return 'Room'

    pts = np.array(polygon, dtype=np.float32)
    rect = cv2.minAreaRect(pts)
    width, height = rect[1]
    if min(width, height) == 0:
        return 'Room'
    ratio = max(width, height) / min(width, height)

    if ratio > 3.0:
        return 'Hall'

    pct = (area_px / total_area) * 100.0

    if pct > 22.0:
        return 'Living Room'
    if pct > 12.0:
        return 'Bedroom'
    if pct > 6.0:
        return 'Kitchen'
    if pct > 2.5:
        return 'Bathroom'
    return 'Room'
