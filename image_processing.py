import torch
from PIL import Image, ImageDraw, ImageFont

from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

# ---- Config ----
MODEL_ID = "IDEA-Research/grounding-dino-base"  # common baseline checkpoint :contentReference[oaicite:1]{index=1}

# Important: prompts are typically lowercase and end with a period.
# You can provide multiple separated by periods. :contentReference[oaicite:2]{index=2}
TEXT_PROMPT = "phone."

BOX_THRESHOLD = 0.25   # raise to reduce false positives
TEXT_THRESHOLD = 0.25  # raise to be stricter about matching words

device = "cuda" if torch.cuda.is_available() else "cpu"


def _get_text_size(draw, text, font):
    """Return (width, height) for the given text using multiple Pillow fallbacks."""
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        pass
    try:
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        pass
    try:
        return font.getsize(text)
    except Exception:
        pass
    try:
        mask = font.getmask(text)
        return mask.size
    except Exception:
        pass
    return (len(text) * 6, 11)



def get_object_bounding_box(images, text_prompt, processor, model):
    top_detections = []
    for image in images:
        inputs = processor(images=image, text=text_prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(**inputs)

        results = processor.post_process_grounded_object_detection(
            outputs=outputs,
            input_ids=inputs["input_ids"],
            threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD,
            target_sizes=[image.size[::-1]]  # (height, width)
        )

        detections = results[0]
        boxes = detections["boxes"]      # (N, 4) in xyxy
        scores = detections["scores"]    # (N,)
        labels = detections["labels"]    # list of strings

        # Return only the single detection with highest score (or None if no detections)
        if len(boxes) == 0:
            top_detections.append(None)
            continue

        scores_list = [float(s) for s in scores]
        max_idx = int(max(range(len(scores_list)), key=lambda i: scores_list[i]))
        top_detections.append({
            'label': labels[max_idx],
            'score': scores_list[max_idx],
            'box': boxes[max_idx].tolist()
        })

    return top_detections


# images_paths_in_order = ['images/1.jpeg', 'images/2.jpeg', 'images/3.jpeg']
# images_in_order = [Image.open(image_path).convert("RGB") for image_path in images_paths_in_order]

# ---- Load model + processor ----
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForZeroShotObjectDetection.from_pretrained(MODEL_ID).to(device)

# detections = get_object_bounding_box(images_in_order, TEXT_PROMPT, processor, model)
# for idx, det in enumerate(detections):
#     image = images_in_order[idx]
#     draw = ImageDraw.Draw(image)
#     font = ImageFont.load_default()

#     if det is None:
#         print(f"Image {idx + 1}: Found 0 candidate boxes")
#     else:
#         print(f"Image {idx + 1}: Found 1 candidate box")
#         print(det['label'], det['score'], det['box'])
#         x1, y1, x2, y2 = det['box']
#         draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
#         text = f"{det['label']} {det['score']:.2f}"
#         text_w, text_h = _get_text_size(draw, text, font)
#         draw.rectangle([x1, max(0, y1 - text_h - 4), x1 + text_w + 4, y1], fill="red")
#         draw.text((x1 + 2, max(0, y1 - text_h - 4) + 2), text, fill="white", font=font)

#     out_path = f"out_detected_{idx+1}.jpg"
#     image.save(out_path)
#     print("Saved:", out_path)
#     try:
#         image.show()
#     except Exception:
#         # `show()` may fail in headless environments; ignore silently
#         pass