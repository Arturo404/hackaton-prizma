# Pen-cap detection prototype

Purpose
- Small prototype that runs zero-shot object detection using the Grounding DINO checkpoint via Hugging Face `transformers`.

Quick start
- Create/activate a Python environment (Windows examples):

```powershell
.venv\Scripts\Activate.ps1
```

```cmd
.venv\Scripts\activate.bat
```

- Install dependencies and run:

```powershell
python -m pip install -r requirements.txt
python image_processing.py
```

What runs
- `image_processing.py` loads the model `IDEA-Research/grounding-dino-base`, runs inference for prompts in `TEXT_PROMPT`, and saves annotated outputs as `out_detected_1.jpg`, `out_detected_2.jpg`, ...
- The helper `get_object_bounding_box(images, text_prompt)` returns one item per input image: either `None` (no detection) or a dict `{ 'label', 'score', 'box' }` representing the single highest-scoring detection.

Notes
- The first run will download model weights — expect network and disk usage.
- `image.show()` may fail in headless environments; annotated images are still saved to disk.

Additional scripts
- `location_computing.py`: Functions for computing distances, displacements, etc., from bounding boxes.
- `video_sampler.py`: Sample frames from a video at a specified rate.

  Usage: `python video_sampler.py <video_path> <output_folder> [--sample_rate 1.0] [--frame_skip 30]`

Next steps
- I can add a small script to run a single image or produce a combined CSV report of detections if you want.
