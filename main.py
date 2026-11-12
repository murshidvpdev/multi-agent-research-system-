from src.pipeline.pipeline import run_research_system
from rich import print

topic = "The impact of artificial intelligence on healthcare"
state = run_research_system(topic, on_step=lambda step, _: print(f"[green]✓[/green] {step} done"))

print("\n[bold green]Generated Report:[/bold green]")
print(state["report"])
print("\n[bold blue]Critique of the Report:[/bold blue]")
print(state["critique"])
