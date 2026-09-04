import os, random, time
from datetime import timedelta
from functools import wraps
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__) 
app.config.update(SECRET_KEY=os.getenv("SECRET_KEY", "local-dev-key-change-before-deploy"), PERMANENT_SESSION_LIFETIME=timedelta(hours=4))

COLORS = ("#f7a8b8", "#a9d6ca", "#b9b7ef", "#f5c889", "#a9c6ea", "#e6b6d4")
EMOJIS = ("✦", "⚗", "π", "⌛", "☀", "✿")
GIFTS = ("The Golden Quill", "The Curiosity Jar", "The Puzzle Compass", "The Timekeeper's Medal", "The Kindness Lantern", "The Sparkle Badge")
TEACHERS = {f"Teacher {number}": {"pin": str(1000 + number), "subject": "Teacher's Day", "emoji": EMOJIS[(number - 1) % 6], "color": COLORS[(number - 1) % 6], "gift": GIFTS[(number - 1) % 6], "line": "For making every school day brighter."} for number in range(1, 35)}
NOTES = {teacher: [("Student 1", "Thank you for believing in us every day."), ("Student 2", "Your patience makes learning feel possible."), ("Student 3", "Thank you for turning lessons into lovely memories."), ("Student 4", "We are grateful for every little encouragement.")] for teacher in TEACHERS}

def current_teacher(): return session.get("teacher")
def protected(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        if not current_teacher(): return jsonify(error="Please unlock your memory space."), 401
        return fn(*args, **kwargs)
    return inner

@app.get("/")
def home():
    teacher = current_teacher()
    return render_template("index.html", teacher=teacher, data=TEACHERS[teacher]) if teacher else render_template("login.html")

@app.post("/api/login")
def login():
    now, attempts, locked_until = time.time(), session.get("attempts", 0), session.get("locked_until", 0)
    if now < locked_until: return jsonify(error="Please wait one minute before trying again."), 429
    pin = str((request.get_json(silent=True) or {}).get("pin", ""))
    teacher = next((name for name, data in TEACHERS.items() if data["pin"] == pin), None)
    if not teacher:
        attempts += 1; session["attempts"] = attempts
        if attempts >= 5: session["locked_until"] = now + 60; session["attempts"] = 0
        return jsonify(error="That key does not match a memory space."), 401
    session.clear(); session["teacher"] = teacher; session.permanent = True
    return jsonify(ok=True)

@app.post("/api/logout")
def logout(): session.clear(); return jsonify(ok=True)

@app.post("/api/message")
@protected
def message():
    teacher, seen = current_teacher(), session.setdefault("seen", {})
    used = seen.get(teacher, []); available = [i for i in range(len(NOTES[teacher])) if i not in used]
    if not available: used, available = [], list(range(len(NOTES[teacher])))
    picked = random.choice(available); used.append(picked); seen[teacher] = used; session["seen"] = seen
    student, text = NOTES[teacher][picked]
    return jsonify(student=student, text=text, remaining=len(NOTES[teacher]) - len(used), total=len(NOTES[teacher]))

@app.post("/api/reset")
@protected
def reset():
    session.setdefault("seen", {}).pop(current_teacher(), None); session.modified = True
    return jsonify(ok=True)

if __name__ == "__main__": app.run(debug=True)
