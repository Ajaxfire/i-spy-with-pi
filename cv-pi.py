import cv2
import RPi.GPIO as GPIO
import os
import time

# Setup GPIO pins for LEDs
GREEN_LED = 18  # GPIO pin for green LED
RED_LED = 23    # GPIO pin for red LED

# Setup GPIO mode and pin output
GPIO.setmode(GPIO.BCM)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)

# Path to save captured images
SAVE_PATH = "/home/pi/Pictures/"  # Change this to your desired directory

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

# Turn on Green LED to indicate system is active
GPIO.output(GREEN_LED, GPIO.HIGH)

# Load hand cascade for gesture detection (using Haar cascade for simplicity)
#hand_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'aGest.xml')  # Replace with actual cascade file for hand detection

# Initialize USB camera
camera = cv2.VideoCapture(0,cv2.CAP_V4L)

#Set lower resolution for the camera
camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
camera.set(cv2.CAP_PROP_BUFFERSIZE,2)

def capture_photo(frame):
    """Capture and save a photo to the SAVE_PATH."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{SAVE_PATH}/photo_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Photo saved at {filename}")

try:
    while True:
        # Capture frame-by-frame
        ret, frame = camera.read()

        if not ret:
            print("Failed to capture video frame")
            break

        # Convert frame to grayscale for gesture detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect hands in the frame
#        hands = hand_cascade.detectMultiScale(gray_frame, 1.1, 4)

        # If a hand is detected, process the gesture
#        if len(hands) > 0:
#            print("Gesture detected!")
        time.sleep(5)
        print("Capture imminent!")

	    # Turn off Green LED and turn on Red LED to indicate processing
        GPIO.output(GREEN_LED, GPIO.LOW)
        GPIO.output(RED_LED, GPIO.HIGH)

	    # Wait for 2 seconds (just to simulate some processing time)
        time.sleep(1)

	    # Capture and save the photo
        capture_photo(frame)

	    # Turn off Red LED and turn back on Green LED
        GPIO.output(RED_LED, GPIO.LOW)
        GPIO.output(GREEN_LED, GPIO.HIGH)
#        else:
            # Display the frame with a message
#            cv2.putText(frame, "Show Gesture to Capture Photo", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('USB Camera Feed', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Release the camera and close all OpenCV windows
    camera.release()
    cv2.destroyAllWindows()

    # Cleanup GPIO
    GPIO.cleanup()
