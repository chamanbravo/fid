import random

import typer
from rich.live import Live
from rich.markdown import Markdown
from rich.spinner import Spinner

from . import console
from .utils import LOADING_MESSAGES


class Fid:
    def __init__(self, model: str, system_prompt: list[str] = []):
        self.model = model
        self.system_prompt = system_prompt
        self.agent = self._create_agent()

    def _create_agent(self):
        from pydantic_ai import Agent, UserError

        try:
            return Agent(model=self.model, system_prompt=self.system_prompt)
        except UserError as e:
            console.print(f"[red reverse]ERROR:[/red reverse] {e}")
            raise typer.Exit(1)

    async def run(self, prompt: str):
        with Live(
            Spinner(
                "dots2",
                text=f"[magenta]{random.choice(LOADING_MESSAGES)}[/magenta]",
                style="cyan",
            ),
            console=console,
            vertical_overflow="ellipsis",
            refresh_per_second=10,
        ) as live:
            async with self.agent.run_stream(prompt) as result:
                async for message in result.stream():
                    live.update(Markdown(message, code_theme="nord"), refresh=True)
