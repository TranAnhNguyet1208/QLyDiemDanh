"""
Module for capturing face images using OpenCV
Handles camera interaction and image storage
"""
import cv2
import os
import time
import numpy as np
from pathlib import Path


class FaceCapture:
    """Class for capturing face images from webcam"""
    
    def __init__(self):
        """Initialize face capture with Haar Cascade classifier for face detection"""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def create_user_folder(self, name: str, student_id: str, base_dir: str = "face_data") -> str:
        """
        Create folder for storing user face images
        Uses simple student_id for folder name to ensure consistency
        
        Args:
            name: User's full name
            student_id: User's student ID
            base_dir: Base directory for storing face data
            
        Returns:
            Path to created folder (e.g., "face_data/SV001")
        """
        # Create folder name: MaSV (Simple and unique)
        folder_name = student_id
        folder_path = os.path.join(base_dir, folder_name)
        
        # Create directory recursively if needed
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        
        return folder_path
    
    def capture_faces(self, name: str, student_id: str, num_images: int = 30, 
                     delay: float = 0.5, base_dir: str = "face_data") -> tuple[bool, str, str]:
        """
        Capture face images from camera with visual guides
        Matches logic from Backup: 30 images, whole frame
        """
        # Create folder for user
        folder_path = self.create_user_folder(name, student_id, base_dir)
        
        # Initialize camera
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not cap.isOpened():
            # Try default backend if DSHOW fails
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Không thể mở camera", ""
            
        captured_count = 0
        last_capture_time = 0
        
        # Create fullscreen window
        window_name = f'Dang ky khuon mat - {name} ({student_id})'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        # cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        print(f"Bắt đầu chụp {num_images} ảnh cho {name} - {student_id}")
        
        while captured_count < num_images:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Mirror frame
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.3, minNeighbors=5
            )
            
            # Draw faces
            for (x, y, fw, fh) in faces:
                cv2.rectangle(frame, (x, y), (x + fw, y + fh), (0, 255, 0), 2)
            
            # Status info
            status_color = (0, 255, 0) if len(faces) > 0 else (0, 0, 255)
            status_text = "Phat hien khuon mat" if len(faces) > 0 else "Khong tim thay khuon mat"
            
            cv2.putText(frame, f"Da chup: {captured_count}/{num_images}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, status_text, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.putText(frame, "ESC: Huy", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Capture logic
            current_time = time.time()
            if len(faces) > 0 and (current_time - last_capture_time) >= delay:

                img_name = f"{student_id}_{captured_count+1}.jpg"
                img_path = os.path.join(folder_path, img_name)
                
                cv2.imwrite(img_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                captured_count += 1
                last_capture_time = current_time
                print(f"Đã chụp: {captured_count}/{num_images}")
                

                cv2.rectangle(frame, (0, 0), (w, h), (255, 255, 255), 10)
            
            cv2.imshow(window_name, frame)
            
            if cv2.waitKey(1) == 27: # ESC
                cap.release()
                cv2.destroyAllWindows()

                return False, "Đã hủy bỏ", ""
                
        cap.release()
        cv2.destroyAllWindows()
        return True, f"Đã chụp xong {num_images} ảnh", folder_path
    
    def detect_face_in_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(100, 100)
        )
        return faces
