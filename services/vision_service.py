import cv2

class VisionService:
    def __init__(self, camera_index=0):
        # Default camera index (0 = built-in webcam)
        self.camera_index = camera_index

    def capture_image(self, output_file="captured_image.jpg"):
        """Capture image from camera"""
        cap = cv2.VideoCapture(self.camera_index)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(output_file, frame)
            cap.release()
            return output_file
        else:
            cap.release()
            return None

    def detect_faces(self, image_file: str):
        """Detect faces in an image"""
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        img = cv2.imread(image_file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        results = []
        for (x, y, w, h) in faces:
            results.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})
        return results
