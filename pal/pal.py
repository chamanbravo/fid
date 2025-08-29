import typer
from pydantic_ai import Agent, UserError
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.spinner import Spinner

console = Console()


class Pal:
    def __init__(self, model: str, system_prompt: list[str] = []):
        self.model = model
        self.system_prompt = system_prompt

    def agent(self):
        try:
            return Agent(model=self.model, system_prompt=self.system_prompt)
        except UserError as e:
            console.print(f"[red reverse]ERROR:[/red reverse] {e}")
            raise typer.Exit(1)


async def run(prompt: str, agent: Agent):
    with Live(
        Spinner("dots2", text="[magenta]Thinking...[/magenta]", style="cyan"),
        console=console,
        vertical_overflow="ellipsis",
        refresh_per_second=10,
    ) as live:
        async with agent.run_stream(prompt) as result:
            async for message in result.stream():
                live.update(Markdown(message, code_theme="nord"), refresh=True)
