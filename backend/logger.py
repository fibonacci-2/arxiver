import logging
from rich.logging import RichHandler
from rich.console import Console

console = Console()

def setup_logger(name='paper-producer'):
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
    )
    return logging.getLogger(name)

logger = setup_logger()

def log_step(step_name):
    console.print(f"\n[bold cyan]→[/bold cyan] [bold]{step_name}[/bold]")

def log_info(message):
    console.print(f"  [green]✓[/green] {message}")

def log_warning(message):
    console.print(f"  [yellow]⚠[/yellow] {message}")

def log_error(message):
    console.print(f"  [red]✗[/red] {message}")

def log_config(config_dict):
    console.print("\n[bold]Configuration:[/bold]")
    for key, value in config_dict.items():
        if isinstance(value, dict):
            console.print(f"  [cyan]{key}:[/cyan]")
            for k, v in value.items():
                console.print(f"    {k}: [yellow]{v}[/yellow]")
        else:
            console.print(f"  [cyan]{key}:[/cyan] [yellow]{value}[/yellow]")
