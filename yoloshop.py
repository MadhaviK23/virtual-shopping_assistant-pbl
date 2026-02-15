from ultralytics import YOLO
import cv2
import sqlite3

# ---------- LOAD MODEL ----------
model = YOLO("yolov8n.pt")

# ---------- CONNECT DATABASE ----------
conn = sqlite3.connect("shopping.db")
cursor = conn.cursor()

# ---------- START WEBCAM ----------
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO detection
    results = model(frame)

    # get annotated frame
    annotated_frame = results[0].plot()

    # get detected classes
    boxes = results[0].boxes

    if boxes is not None:
        for box in boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id].lower()

            # search price in database
            cursor.execute("SELECT price FROM products WHERE name=?", (label,))
            result = cursor.fetchone()

            if result:
                price = result[0]
                text = f"{label} - ₹{price}"
            else:
                text = f"{label} - not in db"

            # show text on screen
            cv2.putText(
                annotated_frame,
                text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

    cv2.imshow("Virtual Shopping Assistant", annotated_frame)

    # press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
conn.close()
cv2.destroyAllWindows()
