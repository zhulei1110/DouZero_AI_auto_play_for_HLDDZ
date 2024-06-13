import json
import os.path

class Config:
    window_width: int
    window_height: int
    window_class_name: str

    def __init__(self, **kwargs) -> None:
        self.window_width = kwargs.get('window_width', 1440)
        self.window_height = kwargs.get('window_height', 810)
        self.window_class_name = kwargs.get('window_class_name', '')
    
    @classmethod
    def load(cls):
        if not os.path.exists('config.json'):
            return cls()
        with open('config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)