import torch
from PIL import Image, ImageDraw, ImageFont

from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

# ---- Config ----
MODEL_ID = "IDEA-Research/grounding-dino-base"  # common baseline checkpoint :contentReference[oaicite:1]{index=1}
IMAGE_PATH = "first_center.jpeg"

# Important: prompts are typically lowercase and end with a period.
# You can provide multiple separated by periods. :contentReference[oaicite:2]{index=2}
TEXT_PROMPT = "pen cap. cap of a pen. plastic pen cap."

BOX_THRESHOLD = 0.25   # raise to reduce false positives
TEXT_THRESHOLD = 0.25  # raise to be stricter about matching words

device = "cuda" if torch.cuda.is_available() else "cpu"

# ---- Load model + processor ----
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForZeroShotObjectDetection.from_pretrained(MODEL_ID).to(device)

# ---- Load image ----
image = Image.open(IMAGE_PATH).convert("RGB")

# ---- Prepare inputs ----
inputs = processor(images=image, text=TEXT_PROMPT, return_tensors="pt").to(device)

# ---- Inference ----
with torch.no_grad():
    outputs = model(**inputs)

# ---- Post-process to boxes in image coordinates ----
# GroundingDinoProcessor has a helper for grounded object detection post-processing. :contentReference[oaicite:3]{index=3}
results = processor.post_process_grounded_object_detection(
    outputs=outputs,
    inputs=inputs,
    box_threshold=BOX_THRESHOLD,
    text_threshold=TEXT_THRESHOLD,
    target_sizes=[image.size[::-1]]  # (height, width)
)

detections = results[0]
boxes = detections["boxes"]      # (N, 4) in xyxy
scores = detections["scores"]    # (N,)
labels = detections["labels"]    # list of strings

print(f"Found {len(boxes)} candidate boxes")
for i in range(len(boxes)):
    print(i, labels[i], float(scores[i]), boxes[i].tolist())

# ---- Draw boxes ----
draw = ImageDraw.Draw(image)
for box, score, label in zip(boxes, scores, labels):
    x1, y1, x2, y2 = box.tolist()
    draw.rectangle([x1, y1, x2, y2], width=3)
    draw.text((x1, max(0, y1 - 12)), f"{label} {float(score):.2f}")

out_path = "out_detected.jpg"
image.save(out_path)
print("Saved:", out_path)
