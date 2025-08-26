## Tomato Disease Detection Web App

### Quickstart

1) Create a virtual environment and install deps
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Create a `.env` file (see `example.env` values)
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

#### Preprocessing Pipeline
The app uses the following preprocessing for inference:
- **Resize**: 128x128 pixels
- **Color**: Convert to RGB
- **Normalization**: Scale pixels to [0, 1] range (divide by 255.0)
- **Shape**: Expand to batch dimension (1, 128, 128, 3)

#### Class Labels Management
- The app automatically loads `class_names.json` if present in the project root
- Falls back to default labels if file is missing or invalid
- Label order must match your model's final Dense layer output order

#### Exporting Labels After Training
```bash
# Use default labels
python export_labels.py

# Specify custom labels
python export_labels.py --labels Tomato___Bacterial_spot Tomato___Early_blight Tomato___healthy

# Custom output path
python export_labels.py --output my_labels.json
```

#### Deployment Checklist
- [ ] Save trained model as `tomato_disease_cnn_model.h5`
- [ ] Generate `class_names.json` using `export_labels.py`
- [ ] Verify preprocessing matches training pipeline
- [ ] Test prediction with sample images

### Development Workflow

#### Branch Strategy
- `main`: Production (protected)
- `develop`: Staging/Integration
- `feature/*`: Feature development
- `hotfix/*`: Urgent production fixes

#### Testing Checklist
- [ ] App starts without errors
- [ ] All routes respond (200, not 502/504)
- [ ] Image upload and prediction works
- [ ] Non-tomato detection works
- [ ] Docker build succeeds
- [ ] Docker containers start and are healthy

