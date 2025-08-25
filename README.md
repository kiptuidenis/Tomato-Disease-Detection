## Tomato Disease Detection Web App

### Quickstart

1) Create a virtual environment and install deps
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Create a `.env` file (see `.env.example` values)
```
SECRET_KEY=change-me
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
MAIL_SUPPRESS_SEND=true
NON_TOMATO_THRESHOLD=0.6
LOG_LEVEL=INFO
```

3) Place the trained model file
```
tomato_disease_cnn_model.h5
class_names.json   # optional, list of labels
```

4) Run the app
```
python app.py
```

Open http://127.0.0.1:5000

### Docker

```
docker compose up --build
```
App available at http://localhost:8000

Environment variables can be supplied via your shell or an `.env` file (see `example.env`).

### Endpoints

- `/predict` (GET/POST): upload an image and get disease prediction.
- `/healthz`: health status JSON.

### Notes
- Non-tomato detection: if model confidence < `NON_TOMATO_THRESHOLD` or class `non_tomato` is predicted (when available), user is prompted to upload a tomato leaf image.
- For Gmail SMTP, use an app password.

### Model and Labels Handoff (Phase 4)

- Preprocessing used in inference:
  - Resize to 128x128, RGB
  - Convert to array, expand dims to (1, 128, 128, 3)
  - Scale pixels to [0, 1] by dividing by 255.0

- Class labels:
  - The app looks for `class_names.json` in the project root. If not found, it falls back to default labels.
  - To export labels after training, generate a JSON list in the same order as your model's final Dense outputs. You can use:
  ```
  python export_labels.py --output class_names.json
  ```
  - Or specify your own list:
  ```
  python export_labels.py --output class_names.json --labels Tomato___Bacterial_spot Tomato___Early_blight ... Tomato___healthy
  ```

- Saving the model:
  - Save your trained Keras model as `tomato_disease_cnn_model.h5` in the project root alongside `class_names.json` before running the app or building Docker.

