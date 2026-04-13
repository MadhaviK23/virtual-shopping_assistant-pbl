import streamlit as st
from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

st.title("🛒 Virtual Shopping Assistant")

run = st.checkbox("Start Camera")

if run:
    cap = cv2.VideoCapture(0)

    frame_placeholder = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated = results[0].plot()

        frame_placeholder.image(annotated, channels="BGR")

    cap.release()
