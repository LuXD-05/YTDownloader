import json
from pathlib import Path

class Settings:
    
    DEFAULT_SETTINGS = {
        "YT_API_KEY": "",
        "DEFAULT_DOWNLOAD_PATH": "",
        "FORMAT": "mp3",
        "QUALITY": "5",
        "SPLIT_CHAPTERS": "False",
        "FILTER": "video"
    }
    
    def __init__(self):
        self.settings = {}
        self.data_dir = Path.cwd() / "data"
        self.settings_path = self.data_dir / "settings.json"
        # Create data dir if not exists
        self.data_dir.mkdir(exist_ok=True)
        # Create json if not exists
        if not self.settings_path.exists():
            self.save()
        # Load settings
        self.load()
    
    def save(self):
        # Writes CURRENT settings into json
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    def load(self):
        # If json exists --> open & load settings || load default on error
        if self.settings_path.exists():
            with open(self.settings_path, "r", encoding="utf-8") as f:
                try:
                    #! DONT WORK IF NOT SEPARATED
                    _ = f.read()
                    __ = json.loads(_)
                    self.settings = __
                except json.JSONDecodeError as e:
                    self.settings = self.DEFAULT_SETTINGS
                    #TODO: alert default settings?
        # Json not exists --> save default settings
        else:
            self.settings = self.DEFAULT_SETTINGS
            self.save()

    # Returns a single variable || default value
    def get(self, key, default=None):
        return self.settings.get(key, default)

    # Sets a single variable & saves to json
    def set(self, key, value):
        self[key] = value
        self.save()