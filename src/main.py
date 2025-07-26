import click
from commands.add import add
from commands.list import list

@click.group()
def cli():
    pass

cli.add_command(add)
cli.add_command(list)

if __name__ == "__main__":
    cli()