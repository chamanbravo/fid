from dataclasses import dataclass, field
from pathlib import Path

import yaml

default_config_str = """\
# Default model ('openai:chatgpt-4o-latest', 'openai:gpt-3.5-turbo',...)
default-model: google-gla:gemini-2.0-flash
# List of predefined system messages that can be used as roles
roles:
  "default": []
  # Example, a role called `shell`:
  shell:
    - you are a shell expert
    - you do not explain anything
    - you simply output one liners to solve the problems you're asked
    - you do not provide any explanation whatsoever, ONLY the command
# System role to use
role: "default"
"""


@dataclass
class Configs:
    default_model: str = "google-gla:gemini-2.0-flash"
    roles: dict[str, list[str]] = field(default_factory=lambda: {"default": []})
    role: str = "default"


class Config:
    def __init__(self):
        from . import console

        self.console = console
        self.config_dir = Path.home() / ".config" / "fid"
        self.config_file = self.config_dir / "config.yaml"

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> Configs:
        default_config = Configs()

        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data: dict[str, str] = yaml.safe_load(f) or {}

                for key, value in data.items():
                    if hasattr(default_config, key):
                        setattr(default_config, key, value)
            except Exception as e:
                self.console.print(f"Warning: Could not load config: {e}")
        else:
            self.reset_config()

        return default_config

    def reset_config(self):
        try:
            with open(self.config_file, "w") as f:
                f.write(default_config_str)
        except Exception as e:
            self.console.print(f"Warning: Could not save config: {e}")
