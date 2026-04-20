# InsightClass Monitor 🎓

An **Emotion-Aware Online Learning Assistant** that detects student emotions in real-time
and provides teachers with live feedback and AI-powered recommendations.

---

## 📁 Project Structure

```
insightclass/
├── app.py              ← Main entry point (run this)
├── config.py           ← Settings, emotion maps, teacher suggestions
├── models.py           ← All shared global state (sessions, logs, etc.)
├── camera.py           ← VideoCamera class (webcam handling)
├── background.py       ← Background thread for recording class history
├── requirements.txt    ← Python dependencies
│
├── routes/
│   ├── auth.py         ← Login, logout, signup, forgot password
│   ├── teacher.py      ← Teacher dashboard, end class, attendance download
│   ├── student.py      ← Student dashboard
│   ├── api.py          ← All JSON API endpoints (/get_stats, /toggle_camera, etc.)
│   ├── poll.py         ← Poll creation, voting, closing
│   └── video.py        ← Live video feed streaming
│
└── templates/
    ├── base.html       ← Master layout (nav, CSS, shared JS)
    ├── login.html      ← Login page
    ├── signup.html     ← Sign up page
    ├── forgot.html     ← Forgot password page
    ├── teacher.html    ← Teacher dashboard
    ├── student.html    ← Student dashboard
    ├── poll_form.html  ← Create poll form
    └── report.html     ← End of class report
```

---

## ⚙️ Setup & Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** DeepFace will automatically download required models (VGG-Face etc.)
> on its first run. Make sure you have an internet connection for the first run.

### 2. Run the App

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 🔐 Default Login Credentials

| Role    | Username  | Password |
|---------|-----------|----------|
| Teacher | teacher   | 123      |
| Student | student   | 123      |
| Student | student2  | 123      |

---

## ✨ Features

- **Real-time emotion detection** via webcam (DeepFace)
- **Teacher dashboard** with live mood chart, engagement score, AI recommendations
- **Student dashboard** with "I'm Confused!" button
- **Live polls** — teacher creates, students vote in real-time
- **Attendance tracking** with CSV download
- **Audio rooms** via WebRTC (PeerJS)
- **Speech sentiment analysis** (TextBlob)
- **End-of-class report** with engagement highlights

---

## 🛠️ Troubleshooting

- **Camera not detected:** Make sure no other application is using your webcam.
- **DeepFace errors on first run:** Let it download the model weights (~500MB).
- **Port in use:** Change `port=5000` in `app.py` to another port like `5001`.
