SECRET_KEY = 'major_project_secret_key'

EMOTION_MAP = {
    "happy": "Engaged",
    "neutral": "Thinking",
    "sad": "Bored",
    "angry": "Frustrated",
    "fear": "Confused",
    "surprise": "Confused",
    "disgust": "Frustrated"
}

TEACHER_SUGGESTIONS = {
    "Confused": "<div style='color:#c0392b;font-weight:bold;'>⚠️ ALERT: High Confusion</div><ul><li>Pause Immediately.</li><li>Ask: 'Which part is unclear?'</li></ul>",
    "Bored": "<div style='color:#f39c12;font-weight:bold;'>⚡ ENERGY DIP</div><ul><li>Run a quick poll.</li><li>Ask a student to summarize.</li></ul>",
    "Frustrated": "<div style='color:#d35400;font-weight:bold;'>🛑 STOP: Frustration</div><ul><li>Validate the difficulty.</li><li>Review the last step.</li></ul>",
    "Thinking": "<div style='color:#2980b9;font-weight:bold;'>🧠 PROCESSING</div><ul><li>Give them space to think.</li><li>Wait 10s before speaking.</li></ul>",
    "Engaged": "<div style='color:#27ae60;font-weight:bold;'>🌟 FLOW STATE</div><ul><li>Keep momentum.</li><li>Challenge them.</li></ul>",
    "Distracted": "<div style='color:#7f8c8d;font-weight:bold;'>👀 DISTRACTION ALERT</div><ul><li>Call on a student.</li><li>Ask everyone to type in chat.</li></ul>",
    "Waiting...": "<div style='color:#7f8c8d;'>Waiting for student data...</div>",
    "Camera Off": "<div style='color:#7f8c8d;'>Camera is turned off.</div>"
}
