import json
from typing import List

from core.session import Session


def save_project(session: Session, filepath: str) -> bool:
    data = {}
    fc_paths: List[str] = []

    for fc in session.loaded_feature_collections:
        fc_paths.append(fc.path)
    
    data["version"] = 1
    data["feature_collections"] = fc_paths
    data["rotation_model"] = session._rotationModel_path

    try:
        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)
            return True
    except:
        return False

def load_project(session: Session, filepath: str) -> bool:
    data = {}

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except:
        return False
    
    # TODO: Actually schema verification
    
    if data["version"] != 1:
        # TODO: set error to indicate invalid version
        return False
    
    fc_paths: List[str] = data["feature_collections"]
    rotation_model: str = data["rotation_model"]
    
    session.load_feature_collections(fc_paths)
    session.load_rotation_model(rotation_model)

    return True

    