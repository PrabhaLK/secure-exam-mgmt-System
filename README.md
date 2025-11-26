# MyProctorAI Secure Examination Management System

Important: the YOLOv3 weights file is large and is not stored in the repository. You must download it and place it in the `models/` directory before running the app.

Recommended steps (from the repository root):

```bash
# create models directory (if missing)
mkdir -p models

# download the official YOLOv3 weights (approx 200+ MB)
curl -L -o models/yolov3.weights https://pjreddie.com/media/files/yolov3.weights

# verify file is present
ls -lh models/yolov3.weights
```

Alternative: if you have a project-provided Google Drive link, you can use that instead of the official link; just save the downloaded file as `models/yolov3.weights`.

Notes:
- `models/yolov3.weights` is intentionally ignored by git (large binary). Do not add it to the repository.
- If you need to distribute weights to other developers, use a release asset, cloud storage, or Git LFS instead of committing the file.
