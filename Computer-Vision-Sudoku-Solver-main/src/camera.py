import cv2


def take_picture():
    # Open the default camera (usually the built-in webcam)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return
    
    print("Press 'q' to stop capturing.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
                
        # Display the frame
        cv2.imshow("Camera Feed", frame)

        # Wait for 50 milliseconds (20 frames per second)
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

    # Release the camera and video writer
    cap.release()
    cv2.destroyAllWindows()

    return frame

if __name__ == "__main__":
    take_picture()
