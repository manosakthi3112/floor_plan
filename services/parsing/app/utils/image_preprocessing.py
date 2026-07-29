import cv2
import numpy as np
from pdf2image import convert_from_bytes


# Canonical processing size: every downstream threshold (Hough, closing kernel,
# snap radius, min-area filter) is tuned to this resolution, so normalising the
# long edge here makes the whole pipeline resolution-independent.
CANONICAL_LONG_EDGE = 1000


def load_image(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError('Could not decode image')
    return img


def load_pdf(pdf_bytes: bytes, dpi: int = 200) -> np.ndarray:
    images = convert_from_bytes(pdf_bytes, dpi=dpi)
    if not images:
        raise ValueError('PDF has no pages')
    return cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)


def to_grayscale(img: np.ndarray) -> np.ndarray:
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def deskew(img: np.ndarray) -> np.ndarray:
    """Deskew image using dominant horizontal/vertical Hough lines angle."""
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    if lines is None:
        return img

    angles = []
    for line in lines:
        rho, theta = line[0]
        angle = theta * 180 / np.pi
        # Normalize angle to [-45, 45]
        if angle > 45 and angle <= 135:
            angle = angle - 90
        elif angle > 135:
            angle = angle - 180
        if abs(angle) < 15:  # Only minor skew angles
            angles.append(angle)

    if not angles:
        return img

    median_angle = np.median(angles)
    if abs(median_angle) < 0.2:  # Ignore negligible skew
        return img

    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    return cv2.warpAffine(img, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def _canonical_resize(img: np.ndarray, long_edge: int = CANONICAL_LONG_EDGE) -> tuple[np.ndarray, float]:
    """Resize so the long edge == long_edge. Returns (resized, scale) where
    scale = original / resized. Multiply canonical-space coords by `scale` to
    get back to original-pixel space."""
    h, w = img.shape[:2]
    current_long = max(h, w)
    if current_long <= long_edge:
        return img, 1.0
    scale = current_long / long_edge
    new_w = max(1, int(round(w / scale)))
    new_h = max(1, int(round(h / scale)))
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, float(scale)


def preprocess_floorplan(img: np.ndarray) -> dict:
    """
    Returns a dictionary of preprocessed image stages. All masks are in
    *canonical* (resized) pixel space; use `scale` to map back to the original.
      - 'gray':       grayscale (original size)
      - 'deskewed':   deskewed grayscale (canonical size)
      - 'binary':     inverted binary, walls = 255 (canonical size)
      - 'wall_mask':  cleaned structural wall mask retaining ALL walls
                      (outer shell AND interior partitions) = 255 (canonical)
      - 'scale':      float — multiply canonical coords by this for original px
      - 'orig_shape': (h, w) of the original input image

    IMPORTANT — fidelity first: we deliberately do NOT denoise (bilateral /
    median) and do NOT run a speckle-removal component filter here. On real
    floor plans the interior partition walls are thin and faint, and every
    smoothing step tested erased enough of their pixels to collapse room
    segmentation from 7 rooms down to 2. Otsu on the raw deskewed grayscale
    preserves the full wall network; downstream stages handle furniture.
    """
    orig_h, orig_w = img.shape[:2]

    gray_full = to_grayscale(img)
    deskewed_full = deskew(gray_full)

    # Normalise resolution so thresholds are resolution-independent.
    deskewed, scale = _canonical_resize(deskewed_full, CANONICAL_LONG_EDGE)

    # Single source of truth: global Otsu threshold (walls = white).
    # adaptiveThreshold produced per-region thresholds that fragmented walls
    # on unevenly-lit scans; Otsu is far more stable for line drawings.
    _, binary = cv2.threshold(
        deskewed, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # The wall mask IS the cleaned binary: it retains the full wall network
    # (exterior shell + every internal partition). Furniture filtering and
    # short-fragment removal happen later, in the wall detector, where we can
    # reason about line geometry rather than blindly eroding pixels.
    wall_mask = binary.copy()

    return {
        'gray': gray_full,
        'deskewed': deskewed,
        'binary': binary,
        'wall_mask': wall_mask,
        'scale': scale,
        'orig_shape': (orig_h, orig_w),
    }


def threshold(img: np.ndarray) -> np.ndarray:
    return preprocess_floorplan(img)['binary']
