import os
import sys

import click
from rich.console import Console
from rich.table import Table

from mcp_accelerator.parser import SpringBootParser
from mcp_accelerator.domain_classifier import DomainClassifier
from mcp_accelerator.generator import MCPServerGenerator

console = Console()

@click.group()
def cli():
    """MCP Accelerator — Auto-discover Java Spring Boot microservices & generate domain-scoped MCP servers."""
    pass

@cli.command()
@click.argument("target_dir", default=".")
def scan(target_dir: str):
    """Scan directory for Java Spring Boot microservices and display discovered domain tools."""
    target = os.path.abspath(target_dir)
    console.print(f"[bold cyan]Scanning target directory:[/] {target}")

    parser = SpringBootParser(target)
    services = parser.scan_workspace()

    if not services:
        console.print("[yellow]No Spring Boot microservices with controllers or OpenAPI specs found.[/]")
        return

    classifier = DomainClassifier()
    domains = classifier.categorize(services)

    console.print(f"\n[bold green]Found {len(services)} Spring Boot Microservice(s) across {len(domains)} Domain(s):[/]\n")

    for domain in domains:
        table = Table(title=f"Domain: {domain.name.upper()} ({len(domain.tools)} tools)", header_style="bold magenta")
        table.add_column("Tool Name", style="cyan")
        table.add_column("HTTP Method", style="green")
        table.add_column("Path", style="white")
        table.add_column("Service (Port)", style="yellow")
        table.add_column("Description", style="dim")

        for tool in domain.tools:
            table.add_row(
                tool.name,
                tool.http_method,
                tool.path,
                f"{tool.service_name} ({tool.service_port})",
                tool.description[:60]
            )

        console.print(table)
        console.print("")

@cli.command()
@click.argument("target_dir", default=".")
@click.option("--output", "-o", default=None, help="Directory to generate domain MCP servers in.")
@click.option("--base-port", "-p", default=8100, help="Base port offset for generated domain servers.")
def generate(target_dir: str, output: str, base_port: int):
    """Scan Spring Boot projects and generate executable MCP domain servers."""
    target = os.path.abspath(target_dir)
    output_dir = os.path.abspath(output) if output else os.path.join(target, "generated_mcp_servers")

    console.print(f"[bold cyan]Scanning Spring Boot projects in:[/] {target}")
    parser = SpringBootParser(target)
    services = parser.scan_workspace()

    if not services:
        console.print("[red]Error: No microservices detected to generate MCP servers.[/]")
        return

    classifier = DomainClassifier()
    domains = classifier.categorize(services)

    console.print(f"[bold green]Categorized into {len(domains)} domain server(s). Generating code in:[/] {output_dir}\n")

    generator = MCPServerGenerator(output_dir)
    generated_paths = generator.generate_domain_servers(domains, base_port=base_port)

    for path in generated_paths:
        console.print(f" [bold green]✓[/] Generated MCP Server: [bold white]{path}[/]")

    console.print("\n[bold cyan]Success! All Domain MCP Servers generated successfully.[/]")

def main():
    cli()

if __name__ == "__main__":
    main()
