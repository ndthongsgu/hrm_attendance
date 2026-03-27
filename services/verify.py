from deepface import DeepFace
import os
from core.settings import KNOWN_FACES_DIR
import numpy as np
import cv2
import tempfile

def load_known_faces():
    # DeepFace handles loading from folder, no need for global lists
    pass

def verify_face(image, employee_id):
    try:
        # Ensure image is numpy array
        if not isinstance(image, np.ndarray):
            image = np.array(image)
        
        # Use the employee_id as subfolder
        db_path = os.path.join(KNOWN_FACES_DIR, employee_id)
        if not os.path.exists(db_path):
            print(f"No database folder found for employee {employee_id}")
            return None
        
        # Save numpy array to temp file to ensure enforce_detection works properly
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            temp_path = tmp_file.name
            cv2.imwrite(temp_path, image)
        
        try:
            # Find face in database with enforce_detection=False for more lenient detection
            result = DeepFace.find(img_path=temp_path, db_path=db_path, enforce_detection=False)
            
            print(f"Find result type: {type(result)}, length: {len(result) if result else 0}")
            
            # Check if we have results
            if result and len(result) > 0 and not result[0].empty:
                best_match = result[0].iloc[0]
                distance = best_match['distance']
                print(f"Face match for {employee_id}: distance={distance}")
                if distance < 0.6:  # threshold
                    return employee_id
                else:
                    print(f"Distance {distance} exceeds threshold 0.6")
            else:
                print(f"No matches found for employee {employee_id}")
            return None
        except Exception as e:
            print(f"Error in face verification for {employee_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
    except Exception as e:
        print(f"Error in face verification for {employee_id}: {e}")
        return None

# No need to load on startup, DeepFace handles it
load_known_faces()
