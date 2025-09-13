from importlib.metadata import PackageNotFoundError, version

from rich.console import Console

from .config import Config

try:
    __version__ = version("fid")
except PackageNotFoundError:
    __version__ = "0.0.0"


console = Console()
config = Config()
