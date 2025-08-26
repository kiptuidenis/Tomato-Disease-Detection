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

### Endpoints

- `/predict` (GET/POST): upload an image and get disease prediction.
- `/healthz`: health status JSON.

### Notes
- Non-tomato detection: if model confidence < `NON_TOMATO_THRESHOLD` or class `non_tomato` is predicted (when available), user is prompted to upload a tomato leaf image.
- For Gmail SMTP, use an app password.

