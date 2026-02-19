import sqlite3
import cv2
from ultralytics import YOLO
import os
print("Database path:", os.path.abspath("shopping.db"))


model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

conn = sqlite3.connect("shop.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    name TEXT PRIMARY KEY,
    price REAL
)
""")

cursor.execute("INSERT OR IGNORE INTO products VALUES ('apple', 40)")
cursor.execute("INSERT OR IGNORE INTO products VALUES ('banana', 20)")
cursor.execute("INSERT OR IGNORE INTO products VALUES ('bottle', 30)")
cursor.execute("INSERT OR IGNORE INTO products VALUES ('cup', 15)")

conn.commit()


while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            # Query database for price
            cursor.execute("SELECT price FROM products WHERE name=?", (label,))
            result = cursor.fetchone()

            if result:
                price = result[0]

                # Display bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Special case for bottle
                if label.lower() == "bottle":
                    cv2.putText(frame, f"Bottle - Rs {price}",
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 0), 2)

                    cv2.putText(frame, "Added to Cart",
                                (x1, y1 - 40),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 0), 2)

                else:
                    cv2.putText(frame, f"{label} - Rs {price}",
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 255, 0), 2)

    cv2.imshow("YOLO Shop", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
conn.close()
cv2.destroyAllWindows()
