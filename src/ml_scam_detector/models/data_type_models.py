from typing import Union, Dict, List
from dataclasses import dataclass

from src.ml_scam_detector.utils.json_utils import is_json

@dataclass
class JSONObject:
    json_object: Union[Dict, List]

    def __post_init__(self):
        if not is_json(self.json_object):
            raise ValueError("Attempted to instantiate JSONObject with non-json value")

