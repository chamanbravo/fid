import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml


@dataclass
class Configs:
    default_model: str = "google-gla:gemini-2.0-flash"
    roles: dict[str, list[str]] = field(default_factory=lambda: {"default": []})
    role: str = "default"


class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "pal"
        self.config_file = self.config_dir / "config.yaml"

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> Configs:
        default_config = Configs()

        if self.config_file.exists() and yaml:
            try:
                with open(self.config_file, "r") as f:
                    data: dict[str, str] = yaml.safe_load(f) or {}

                for key, value in data.items():
                    if hasattr(default_config, key):
                        setattr(default_config, key, value)
            except Exception as e:
                print(f"Warning: Could not load config: {e}", file=sys.stderr)
        else:
            self.save_settings(default_config)

        return default_config

    def save_settings(self, config: Configs):
        if yaml:
            try:
                with open(self.config_file, "w") as f:
                    yaml.dump(asdict(config), f, default_flow_style=False)
            except Exception as e:
                print(f"Warning: Could not save config: {e}", file=sys.stderr)

    def reset_settings(self):
        default_config = Configs()
        if yaml:
            try:
                with open(self.config_file, "w") as f:
                    yaml.dump(asdict(default_config), f, default_flow_style=False)
            except Exception as e:
                print(f"Warning: Could not save config: {e}", file=sys.stderr)
