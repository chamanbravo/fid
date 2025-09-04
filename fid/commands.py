import asyncio
import os
import subprocess
import sys
from abc import ABC, abstractmethod

import typer

from . import __version__, config, console
from .fid import Fid
from .models import select_model
from .tui import FidTui


class Command(ABC):
    def __init__(self, prompt: list[str] = [], role: str = "default"):
        self.prompt = prompt
        self.role = role

    def prompt_builder(self):
        stdin_data = None
        prompt_str = " ".join(self.prompt) if self.prompt else ""
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read().strip()

        if stdin_data:
            prompt_str = stdin_data + "\n" + prompt_str

        return prompt_str

    @abstractmethod
    def execute(self) -> None:
        """Command execution"""


class ShowVersion(Command):
    def __init__(self): ...

    def execute(self):
        console.print(f"Version: {__version__}")


class Dirs(Command):
    def execute(self):
        console.print(f"[magenta]Configuration:[/magenta] {config.config_dir}")


class SelectModel(Command):
    def execute(self):
        select_model()


class ResetConfig(Command):
    def execute(self):
        config.reset_config()
        console.print("[green]Config reset successfully.[/green]")


class Settings(Command):
    def execute(self):
        editor = os.environ.get("EDITOR", "vim")
        try:
            subprocess.run([editor, str(config.config_file)])
        except FileNotFoundError:
            console.print("[red reverse]ERROR:[/red reverse] Missing $EDITOR")
            console.print(
                f'[dim]exec: "{editor}": executable file not found in %PATH%[/dim]'
            )
            raise typer.Exit(1)


class ListRoles(Command):
    def execute(self):
        roles = config.config.roles.keys()
        console.print("\n".join(roles))


class Role(Command):
    def execute(self):
        prompt = self.prompt_builder()
        fid_config = config.config
        system_prompt = fid_config.roles.get(self.role, [])
        fid = Fid(model=fid_config.default_model, system_prompt=system_prompt)
        asyncio.run(fid.run(prompt))


class FidPrompt(Command):
    def execute(self):
        prompt = self.prompt_builder()
        fid_config = config.config
        fid = Fid(model=fid_config.default_model)
        asyncio.run(fid.run(prompt))


class InteractiveMode(Command):
    def execute(self):
        fid_config = config.config
        app = FidTui(fid_config)
        app.run()
