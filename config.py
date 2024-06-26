import json
import os.path

class Config:
    window_width: int
    window_height: int
    window_class_name: str
    screenshot_image_logs: bool
    template_match_image_logs: bool
    animation_image_compare_logs: bool
    king_color_compare_image_logs: bool
    screenshot_areas: dict[str, str]
    bid_threshold: float
    redouble_threshold: float
    super_redouble_threshold: float
    mingpai_threshold: float
    
    def __init__(self, **kwargs) -> None:
        self.window_width = kwargs.get('window_width', 1600)
        self.window_height = kwargs.get('window_height', 900)
        self.window_class_name = kwargs.get('window_class_name', '')
        self.screenshot_image_logs = kwargs.get('screenshot_image_logs', False)
        self.template_match_image_logs = kwargs.get('template_match_image_logs', False)
        self.animation_image_compare_logs = kwargs.get('animation_image_compare_logs', False)
        self.king_color_compare_image_logs = kwargs.get('king_color_compare_image_logs', False)
        self.screenshot_areas = kwargs.get('screenshot_areas', {})
        self.bid_threshold = kwargs.get('bid_threshold', 0.4)
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