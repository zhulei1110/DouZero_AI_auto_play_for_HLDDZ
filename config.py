import json
import os.path

class Config:
    window_width: int
    window_height: int
    window_class_name: str
    image_locate_logs: bool
    dx_color_compare_logs: bool
    screenshot_logs: bool
    screenshot_areas: dict[str, str]
    bidder_threshold: float
    redouble_threshold: float
    super_redouble_threshold: float
    mingpai_threshold: float
    
    def __init__(self, **kwargs) -> None:
        self.window_width = kwargs.get('window_width', 1600)
        self.window_height = kwargs.get('window_height', 900)
        self.window_class_name = kwargs.get('window_class_name', '')
        self.image_locate_logs = kwargs.get('image_locate_logs', False)
        self.dx_color_compare_logs = kwargs.get('dx_color_compare_logs', False)
        self.screenshot_logs = kwargs.get('screenshot_logs', False)
        self.screenshot_areas = kwargs.get('screenshot_areas', {})
        self.bidder_threshold = kwargs.get('bidder_threshold', 0.4)
        self.redouble_threshold = kwargs.get('redouble_threshold', 0.7)
        self.super_redouble_threshold = kwargs.get('super_redouble_threshold', 0.8)
        self.mingpai_threshold = kwargs.get('mingpai_threshold', 1.2)
    
    @classmethod
    def load(cls):
        if not os.path.exists('config.json'):
            return cls()
        with open('config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)