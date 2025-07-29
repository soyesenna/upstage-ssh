import click
import subprocess
import sys

@click.command()
def update():
    """Update ussh to the latest version"""
    click.echo("Update ussh to the latest version...")

    try:
        result = subprocess.run(
            ["uv", "tool", "install", "ussh", "--upgrade"],
            check=True,
            capture_output=True,
            text=True,
        )
        click.echo(result.stdout)
        click.secho("\nussh update completed successfully.", fg="green")

    except FileNotFoundError:
        click.secho("\nError: 'uv' command not found.", fg="red")
        click.echo("Please check if uv is installed and registered in PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        click.secho("\nError: ussh installation failed.", fg="red")
        click.echo(e.stderr)
        sys.exit(1)
