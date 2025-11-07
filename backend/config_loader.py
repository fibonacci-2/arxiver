import yaml
import os

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r') as f:
            self.data = yaml.safe_load(f)
    
    def get(self, *keys):
        value = self.data
        for key in keys:
            value = value[key]
        return value
    
    def update(self, updates):
        self._update_nested(self.data, updates)
        self._save_config()
    
    def _update_nested(self, d, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and key in d:
                self._update_nested(d[key], value)
            else:
                d[key] = value
    
    def _save_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False)

config = Config()
