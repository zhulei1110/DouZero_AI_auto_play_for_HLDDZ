import json
import os.path

class Config:
    window_width: int
    window_height: int
    window_class_name: str
    image_locate_logs: bool
    screenshot_areas: dict[str, str]
    bidder_thresholds: dict[str, str]
    redouble_thresholds: dict[str, str]
    mingpai_threshold: dict[str, str]
    
    def __init__(self, **kwargs) -> None:
        self.window_width = kwargs.get('window_width', 1600)
        self.window_height = kwargs.get('window_height', 900)
        self.window_class_name = kwargs.get('window_class_name', '')
        self.image_locate_logs = kwargs.get('image_locate_logs', False)
        self.screenshot_areas = kwargs.get('screenshot_areas', {})
        self.bidder_thresholds = kwargs.get('bidder_thresholds', {})
        self.redouble_thresholds = kwargs.get('redouble_thresholds', {})
        self.mingpai_threshold = kwargs.get('thresholds', 1.5)
    
    @classmethod
    def load(cls):
        if not os.path.exists('config.json'):
            return cls()
        with open('config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)