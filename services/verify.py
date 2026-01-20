from deepface import DeepFace
import os
from core.settings import KNOWN_FACES_DIR
import numpy as np

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
            return None
        # Find the face in the database
        result = DeepFace.find(img_path=image, db_path=db_path, enforce_detection=False, silent=True)
        if result and not result[0].empty:
            # Get the best match
            best_match = result[0].iloc[0]
            distance = best_match['distance']
            if distance < 0.6:  # threshold
                return employee_id
    except Exception as e:
        print(f"Error in face verification: {e}")
    return None

# No need to load on startup, DeepFace handles it
load_known_faces()
