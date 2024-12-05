import cv2
import subprocess
import mediapipe as mp
import time

# Initialize MediaPipe Hand tracking model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Zoom in using ADB command
def zoom_in():
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_VOLUME_UP"])
    print("Zooming In")

# Zoom out using ADB command
def zoom_out():
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_VOLUME_DOWN"])
    print("Zooming Out")

# Turn flashlight on using ADB command
def flash_on():
    subprocess.run(["adb", "shell", "cmd", "flashlight", "on"]) 
    print("Flashlight On")

# Turn flashlight off using ADB command
def flash_off():
    subprocess.run(["adb", "shell", "cmd", "flashlight", "off"])
    print("Flashlight Off")

# Capture screenshot using ADB command
def take_screenshot():
    # Simulate pressing power and volume down buttons simultaneously
    subprocess.run(["adb", "shell", "input", "keyevent",  "KEYCODE_VOLUME_DOWN", "KEYCODE_POWER",])
    time.sleep(0.1)  # Short delay to simulate simultaneous press
    subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_VOLUME_DOWN"])
    print("Screenshot Taken")

# Detect hand gesture and identify if thumb is visible for flashlight action
def detect_gesture(hand_landmarks):
    if hand_landmarks:
        thumb_tip = hand_landmarks[mp_hands.HandLandmark.THUMB_TIP].y
        wrist = hand_landmarks[mp_hands.HandLandmark.WRIST].y
        index_finger_tip = hand_landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        middle_finger_tip = hand_landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y

        # Gesture for Zoom In: "Fist" (index finger close to wrist)
        if index_finger_tip < wrist:
            return "fist"

        # Gesture for Zoom Out: "Palm" (index finger above wrist and thumb close to it)
        if index_finger_tip > wrist and thumb_tip < wrist:
            return "palm"

        # Gesture for Screenshot: "Two fingers together" (index and middle finger close to each other)
        if abs(index_finger_tip - middle_finger_tip) < 0.05:
            return "screenshot"

        # Gesture for Flashlight: "Thumb" (thumb extended above wrist)
        if thumb_tip < wrist:
            return "flash"
        
    return None

# Initialize webcam (or any video input)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame to avoid mirror view
    frame = cv2.flip(frame, 1)

    # Convert the image from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Draw hand landmarks on the frame
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Detect gesture
            gesture = detect_gesture(hand_landmarks.landmark)

            # Trigger appropriate action based on gesture
            if gesture == "fist":
                zoom_in()
            elif gesture == "palm":
                zoom_out()
            elif gesture == "screenshot":
                take_screenshot()
            elif gesture == "flash":
                flash_on()

    # Display the image
    cv2.imshow("Hand Gesture Recognition", frame)

    # Exit the loop when 'q' is pressed
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
