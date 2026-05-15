from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
from ultralytics import YOLO
import mysql.connector
import datetime
import time
from flask import session, flash
from flask import jsonify

app = Flask(__name__)
app.secret_key = "secret123"  # ✅ MUST be here

# ---------------- LOGIN ----------------
USERNAME = "admin"
PASSWORD = "1234"

# ---------------- DATABASE ----------------
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="root123",
#     database="crowd_management"
# )
cursor = db.cursor()

# ---------------- GLOBAL VARIABLES ----------------
line_y = 250
track_positions = {}
entered = 0
exited = 0
last_saved_time = 0
alert_triggered = False
current_count = 0
current_status = "Normal"
MAX_CAPACITY = 20   # default
CCTV_SOURCE = None
# ---------------- VIDEO FUNCTION ----------------
def generate_frames():
    global entered, exited, last_saved_time, alert_triggered
    global CCTV_SOURCE
    global current_count, current_status
    global last_alert_sound_time

    if CCTV_SOURCE:
        cap = cv2.VideoCapture(CCTV_SOURCE)
    else:
        cap = cv2.VideoCapture(0)

    model = YOLO("yolov8n.pt")

    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model.track(frame, persist=True, imgsz=416)
        ids = set()

        for r in results:
            boxes = r.boxes

            if boxes.id is not None:
                for box, track_id in zip(boxes, boxes.id):
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])

                    if cls == 0 and conf > 0.3:
                        track_id = int(track_id)
                        ids.add(track_id)

                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2

                        # Dynamic box color
                        if len(ids) < MAX_CAPACITY * 0.7:
                            box_color = (0,255,0)
                        elif len(ids) <= MAX_CAPACITY:
                            box_color = (0,255,255)
                        else:
                            box_color = (0,0,255)

                        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                        cv2.circle(frame, (cx, cy), 5, (0,0,255), -1)

                        # Entry/Exit tracking
                        if track_id in track_positions:
                            prev_y = track_positions[track_id]

                            if prev_y < line_y and cy >= line_y:
                                entered += 1
                            elif prev_y > line_y and cy <= line_y:
                                exited += 1

                        track_positions[track_id] = cy

        # Draw line
        cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (255,0,0), 2)

        count = len(ids)

        # Status logic
        if count < MAX_CAPACITY * 0.7:
            status = "Safe"
            color = (0,255,0)
        elif count <= MAX_CAPACITY:
            status = "Normal"
            color = (0,255,255)
        else:
            status = "Overcrowded"
            color = (0,0,255)

        current_count = count
        current_status = status

        # 🚨 ALERT SYSTEM (FIXED PROPERLY)
        if status == "Overcrowded":

             # blinking text
             if int(time.time() * 2) % 2 == 0:
                 cv2.putText(frame, "OVER LIMIT!", (200, 50),
                             cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

             # red border
             cv2.rectangle(frame, (0,0),
                          (frame.shape[1], frame.shape[0]), (0,0,255), 3)

             # save alert once
             if not alert_triggered:
                 now = datetime.datetime.now()
                 cursor.execute(
                     "INSERT INTO alerts (timestamp, message) VALUES (%s, %s)",
                     (now, "Overcrowding detected")
                 )
                 db.commit()
                 alert_triggered = True

        else:
            alert_triggered = False

        # 🎯 CENTER DISPLAY
        cv2.putText(frame, f"{count}/{MAX_CAPACITY}",
                    (frame.shape[1]//2 - 60, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 3)

        # 🎯 STATUS TEXT
        cv2.putText(frame, status,
                    (frame.shape[1]//2 - 80, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    color, 3)

        # 📊 SMALL CAPACITY BAR
        bar_width = int((count / MAX_CAPACITY) * 200)

        cv2.rectangle(frame, (20, frame.shape[0] - 30),
                      (220, frame.shape[0] - 15), (50,50,50), -1)

        cv2.rectangle(frame, (20, frame.shape[0] - 30),
                      (20 + bar_width, frame.shape[0] - 15),
                      color, -1)

        # 💾 SAVE TO DATABASE
        current_time = time.time()

        if current_time - last_saved_time > 10:
            now = datetime.datetime.now()
            cursor.execute(
                "INSERT INTO crowd_data (timestamp, people_count, status) VALUES (%s, %s, %s)",
                (now, count, status)
            )
            db.commit()
            last_saved_time = current_time

        # STREAM
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        print("DEBUG:", username, password)  # 👈 check terminal

        if username == USERNAME and password == PASSWORD:
            session['user_id'] = 1
            return redirect(url_for("select_mode"))
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route("/select")
def select_mode():
    return render_template("select.html")


@app.route("/webcam")
def webcam():
    return render_template("video.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/dashboard")
def dashboard():
    cursor = db.cursor()

    cursor.execute("SELECT * FROM crowd_data ORDER BY id DESC LIMIT 20")
    data = cursor.fetchall()

    # 👉 ADD THIS HERE
    if len(data) == 0:
        data = [(None, "No Data", 0, 0, 0, "N/A")]

    cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 10")
    alerts = cursor.fetchall()

    cursor.close()

    return render_template("dashboard.html", data=data, alerts=alerts)
@app.route('/cctv', methods=["GET", "POST"])
def cctv():
    if request.method == "POST":
        ip = request.form["ip"].strip()
        session['cctv_ip'] = ip   # store temporarily
        return redirect(url_for('capacity'))

    return render_template("cctv.html")

@app.route('/capacity', methods=["GET", "POST"])
def capacity():
    global MAX_CAPACITY, CCTV_SOURCE

    if request.method == "POST":
        MAX_CAPACITY = int(request.form["capacity"])

        # If CCTV was selected earlier
        if 'cctv_ip' in session:
            CCTV_SOURCE = session['cctv_ip']
            session.pop('cctv_ip')  # clear after use

        return redirect(url_for("webcam"))

    return render_template("capacity.html")

@app.route('/stats')
def stats():
    return jsonify({
        "count": current_count,
        "max": MAX_CAPACITY,
        "status": current_status
    })
# app.py
# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
