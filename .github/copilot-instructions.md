# Copilot instructions for this repository

Purpose
- Help AI code assistants understand and make safe, focused changes to this small image-detection prototype.

Big picture
- This repo is a single-script prototype that runs zero-shot object detection using Hugging Face Transformers and the Grounding DINO checkpoint. Key code is in `image_processing.py` and an exploratory notebook [pen_cap_detection.ipynb](pen_cap_detection.ipynb).
- Data: example images live in the `images/` directory (four JPEGs: `1.jpeg`..`4.jpeg`).

Key integration points
- Model & processor: `AutoProcessor.from_pretrained(MODEL_ID)` and `AutoModelForZeroShotObjectDetection.from_pretrained(MODEL_ID)` (see `image_processing.py`).
- Post-processing: uses `processor.post_process_grounded_object_detection(...)` (notebook shows a working example). Adjust `box_threshold` and `text_threshold` to tune precision/recall.

Project-specific conventions
- Prompts: keep prompts lowercase and end them with a period. Multiple concepts may be separated by periods (e.g. in `TEXT_PROMPT`).
- Device selection: code uses `device = "cuda" if torch.cuda.is_available() else "cpu"` — preserve this pattern when adding inference code.
- Image size ordering: `post_process_grounded_object_detection` expects `target_sizes=[image.size[::-1]]` (height, width).

Files to inspect when changing behavior
- `image_processing.py` — main script; contains a commented end-to-end example and partial helper `get_object_bounding_box(...)` to complete.
- `pen_cap_detection.ipynb` — runnable notebook with the same end-to-end sequence (prepare inputs → inference → post-process → draw boxes). Use it as canonical example for correct API usage.

Developer workflow notes (discoverable)
- There is no `requirements.txt` in the repo. To run locally, install at minimum: `torch`, `transformers`, and `Pillow`.
- The repo appears to use a local virtual environment named `.venv`. On Windows use one of:
  - PowerShell: `.venv\\Scripts\\Activate.ps1`
  - CMD: `.venv\\Scripts\\activate.bat`
- Example quick start (if you have an env):
```powershell
python -m pip install torch transformers Pillow
python image_processing.py
```

What to change or review carefully
- The repository is a prototype: `image_processing.py` contains an incomplete function signature `get_object_bounding_box(image_path, text_prompt)` — implement carefully following the notebook pattern.
- Avoid changing the model checkpoint constant `MODEL_ID` unless replacing the full pipeline; tests and example comments assume `IDEA-Research/grounding-dino-base`.

Quick examples to follow
- Use the notebook's exact sequence: load image → `processor(images=image, text=TEXT_PROMPT, return_tensors='pt')` → `model(**inputs)` → `processor.post_process_grounded_object_detection(...)` → draw boxes.

When uncertain
- If behavior differs between the script and notebook, trust the notebook sequence as the intended canonical flow.
- Ask the maintainer before adding heavy infra (CI, packaging) — this repo is a minimal prototype.

If you modify this file
- Merge or keep any high-value content from an existing `.github/copilot-instructions.md` if present; this repo currently had none.

End of instructions — please ask for clarifications or examples to iterate further.
