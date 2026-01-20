import os
from core.settings import KNOWN_FACES_DIR

def add_known_face(employee_id: str, file):
    # Create the employee folder if it doesn't exist
    employee_dir = os.path.join(KNOWN_FACES_DIR, employee_id)
    os.makedirs(employee_dir, exist_ok=True)

    # Save the file
    file_path = os.path.join(employee_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return f"Image added for employee {employee_id}"
