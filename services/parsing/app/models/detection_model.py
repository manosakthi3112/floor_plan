DEFAULT_MODEL_ID = 'Yytsi/floorplan-to-3d-walls'
FALLBACK_MODEL_ID = 'rikhoffbauer2/floorplan-parser'
DETECTION_MODEL = None
MODEL_PROCESSOR = None



def load_model(model_path_or_id: str = DEFAULT_MODEL_ID):
    global DETECTION_MODEL, MODEL_PROCESSOR
    if DETECTION_MODEL is not None:
        return DETECTION_MODEL
    
    # 1. Try Ultralytics YOLO
    try:
        from ultralytics import YOLO
        DETECTION_MODEL = YOLO(model_path_or_id)
        return DETECTION_MODEL
    except Exception:
        pass

    # 2. Try Hugging Face Transformers object detection model
    try:
        from transformers import AutoImageProcessor, AutoModelForObjectDetection
        MODEL_PROCESSOR = AutoImageProcessor.from_pretrained(model_path_or_id)
        DETECTION_MODEL = AutoModelForObjectDetection.from_pretrained(model_path_or_id)
        return DETECTION_MODEL
    except Exception:
        DETECTION_MODEL = None
        return None


def detect_elements(image, confidence: float = 0.5) -> list[dict]:
    global DETECTION_MODEL, MODEL_PROCESSOR
    if DETECTION_MODEL is None:
        load_model()
    if DETECTION_MODEL is None:
        return []

    detections = []
    try:
        # If Ultralytics model
        if hasattr(DETECTION_MODEL, '__call__'):
            results = DETECTION_MODEL(image, conf=confidence)
            for r in results:
                if hasattr(r, 'boxes') and r.boxes is not None:
                    for box, cls, conf in zip(r.boxes.xyxy, r.boxes.cls, r.boxes.conf):
                        detections.append({
                            'bbox': box.tolist(),
                            'class_id': int(cls),
                            'confidence': float(conf),
                        })
        # If Hugging Face transformers model
        elif MODEL_PROCESSOR is not None:
            import torch
            inputs = MODEL_PROCESSOR(images=image, return_tensors="pt")
            outputs = DETECTION_MODEL(**inputs)
            target_sizes = torch.tensor([image.size[::-1]])
            results = MODEL_PROCESSOR.post_process_object_detection(outputs, threshold=confidence, target_sizes=target_sizes)[0]
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                detections.append({
                    'bbox': box.tolist(),
                    'class_id': int(label),
                    'confidence': float(score),
                })
    except Exception as e:
        print(f"Inference note: {e}")

    return detections
