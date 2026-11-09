"""
Module for face recognition using OpenCV LBPH (Local Binary Patterns Histograms)
Completely offline - no external API required
"""
import os
import cv2
import numpy as np
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class FaceRecognitionService:
    def __init__(self, model_file="face_model.yml", metadata_file="face_metadata.json"):
        self.model_file = model_file
        self.metadata_file = metadata_file
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(radius=2, neighbors=8, grid_x=8, grid_y=8, threshold=80.0)
        
        self.metadata = {}
        self.label_to_id = {}
        self.id_to_label = {}
        self.is_trained = False
        self.use_api = False # Standalone mode
        
        self.load_data()

    def load_data(self):
        """Load model and metadata"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metadata = data.get('metadata', {})
                    self.label_to_id = data.get('label_to_id', {})
                    # Convert string keys back to int for id_to_label
                    self.id_to_label = {int(k): v for k, v in data.get('id_to_label', {}).items()}
            
            if os.path.exists(self.model_file):
                self.recognizer.read(self.model_file)
                self.is_trained = True
                logger.info("Loaded face model and metadata")
            else:
                logger.warning("Model file not found, starting fresh")
                
        except Exception as e:
            logger.error(f"Error loading face data: {e}")

    def _save_data(self):
        """Save metadata"""
        try:
            data = {
                'metadata': self.metadata,
                'label_to_id': self.label_to_id,
                'id_to_label': self.id_to_label
            }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if self.is_trained:
                self.recognizer.write(self.model_file)
                
        except Exception as e:
            logger.error(f"Error saving face data: {e}")

    def recognize_face(self, frame):
        """
        Recognize face in a frame
        Returns: (success, result_dict)
        """
        if not self.is_trained:
            return False, {"message": "Model chưa được train"}
            
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
            )
            
            if len(faces) == 0:
                return False, {"message": "Không tìm thấy khuôn mặt"}
            
            # Process the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            (x, y, w, h) = largest_face
            
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (250, 250)) # Standardize size
            
            label, confidence = self.recognizer.predict(face_roi)
            
            # Confidence: 0 is perfect match, higher is worse. 
            # LBPH threshold is usually around 50-80.
            # Convert to a 0-1 score where 1 is best.
            # Example: if conf=0 -> score=1.0. if conf=100 -> score=0.0
            score = max(0, 100 - confidence) / 100.0
            
            if confidence < 80: # Threshold
                student_code = self.id_to_label.get(label)
                if student_code:
                    info = self.metadata.get(student_code, {})
                    return True, {
                        "student_id": student_code,
                        "name": info.get('name', 'Unknown'),
                        "confidence": score,
                        "box": (x, y, w, h)
                    }
            
            return False, {"message": "Không nhận diện được", "confidence": score}
            
        except Exception as e:
            logger.error(f"Error recognizing face: {e}")
            return False, {"message": str(e)}

    def add_student_faces(self, student_code, name, image_folder):
        """
        Add a new student's face data and retrain the model.
        Args:
            student_code: Student ID
            name: Student Name
            image_folder: Path to folder containing face images
        Returns:
            Tuple (success, message)
        """
        logger.info(f"Adding student faces: {student_code}, {name}, {image_folder}")
        try:
            # Update metadata
            self.metadata[student_code] = {
                'name': name,
                'image_folder': image_folder,
                'image_count': 0, # Will be updated in retrain
                'label': None # Will be assigned in retrain
            }
            
            # Retrain model to include new student
            logger.info("Starting model retraining...")
            self._retrain_model()
            logger.info("Model retraining completed.")
            
            # Save updated data
            logger.info(f"Saving data to {self.metadata_file}...")
            self._save_data()
            logger.info("Data saved.")
            
            return True, f"Đã thêm dữ liệu khuôn mặt cho sinh viên {name} ({student_code})"
        except Exception as e:
            logger.error(f"Lỗi thêm dữ liệu khuôn mặt: {e}", exc_info=True)
            return False, f"Lỗi: {str(e)}"

    def delete_person(self, student_code):
        """
        Delete a student's face data and retrain model
        Args:
            student_code: Student code to remove
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Remove from in-memory metadata and mappings
            if student_code in self.metadata:
                label = self.metadata[student_code].get('label')
                del self.metadata[student_code]
                
                if student_code in self.label_to_id:
                    del self.label_to_id[student_code]
                
                if label is not None and label in self.id_to_label:
                    del self.id_to_label[label]
            else:
                return False, f"Sinh viên {student_code} không có trong metadata"
            
            # Retrain model with remaining students
            self._retrain_model()
            
            # Save updated model and metadata
            self._save_data()
            
            logger.info(f"Đã xóa hoàn toàn dữ liệu khuôn mặt cho sinh viên {student_code}")
            return True, "Đã xóa dữ liệu khuôn mặt thành công"
            
        except Exception as e:
            logger.error(f"Lỗi khi xóa person: {e}")
            return False, f"Lỗi: {str(e)}"
    
    def _retrain_model(self):
        """
        Retrain the LBPH model from scratch using all remaining registered students.
        Rebuilds label mappings and trains a fresh model.
        """
        try:
            # New mappings and training data
            new_label_to_id = {}
            new_id_to_label = {}
            new_metadata = {}
            faces = []
            labels = []
            new_label = 0
            
            logger.info(f"Retraining with {len(self.metadata)} students in metadata")

            # Process each remaining student
            for student_code, info in list(self.metadata.items()):
                # Get image folder
                image_folder = info.get('image_folder')
                if not image_folder:
                    # Try to guess folder
                    image_folder = os.path.join("face_data", student_code)
                
                logger.info(f"Processing student {student_code}, folder: {image_folder}")

                if not os.path.exists(image_folder):
                    logger.warning(f"Không tìm thấy thư mục ảnh cho {student_code}: {image_folder}")
                    continue
                
                # Collect all image files
                image_files = []
                for ext in ['*.jpg', '*.jpeg', '*.png']:
                    image_files.extend(Path(image_folder).glob(ext))
                
                logger.info(f"Found {len(image_files)} images for {student_code}")

                if len(image_files) == 0:
                    continue
                    
                # Process images
                student_faces = []
                for image_path in image_files:
                    try:
                        # Read image
                        with open(str(image_path), 'rb') as f:
                            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
                            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                        
                        if img is None:
                            logger.warning(f"Failed to decode image: {image_path}")
                            continue
                        
                        # Convert to grayscale
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        gray = cv2.equalizeHist(gray)
                        
                        # Detect face
                        detected_faces = self.face_cascade.detectMultiScale(
                            gray, scaleFactor=1.1, minNeighbors=6,
                            minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE
                        )
                        
                        if len(detected_faces) > 0:
                            (x, y, w, h) = detected_faces[0]
                            face_roi = gray[y:y+h, x:x+w]
                            face_roi = cv2.resize(face_roi, (250, 250))
                            face_roi = cv2.GaussianBlur(face_roi, (5, 5), 0)
                            student_faces.append(face_roi)
                        else:
                            # logger.debug(f"No face detected in {image_path}")
                            pass
                            
                    except Exception as e:
                        logger.error(f"Error processing image {image_path}: {e}")
                        continue
                
                logger.info(f"Extracted {len(student_faces)} faces for {student_code}")

                if len(student_faces) > 0:
                    # Add to training set
                    for face in student_faces:
                        faces.append(face)
                        labels.append(new_label)
                    
                    # Update mappings
                    new_label_to_id[student_code] = new_label
                    new_id_to_label[new_label] = student_code
                    
                    # Update metadata
                    new_metadata[student_code] = {
                        'name': info['name'],
                        'image_folder': image_folder,
                        'image_count': len(student_faces),
                        'label': new_label
                    }
                    
                    new_label += 1
            
            # Update class attributes
            self.metadata = new_metadata
            self.label_to_id = new_label_to_id
            self.id_to_label = new_id_to_label
            
            # Recreate recognizer
            self.recognizer = cv2.face.LBPHFaceRecognizer_create(
                radius=2, neighbors=8, grid_x=8, grid_y=8, threshold=80.0
            )
            
            if len(faces) > 0:
                logger.info(f"Training model with {len(faces)} faces...")
                self.recognizer.train(faces, np.array(labels))
                self.is_trained = True
                logger.info(f"Đã retrain model với {len(new_metadata)} sinh viên")
            else:
                # No students left, clear model
                self.is_trained = False
                if os.path.exists(self.model_file):
                    try:
                        os.remove(self.model_file)
                        logger.info("Đã xóa model file (không còn sinh viên)")
                    except Exception:
                        pass
                logger.info("Không còn sinh viên để train model")
                
        except Exception as e:
            logger.error(f"Lỗi khi retrain model: {e}", exc_info=True)
