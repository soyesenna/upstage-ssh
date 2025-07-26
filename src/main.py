import click
from commands.add import add
from commands.list import list
from commands.remove import remove

@click.group()
def cli():
    pass

cli.add_command(add)
cli.add_command(list)
cli.add_command(remove)
cli.add_command(remove, name='rm')

if __name__ == "__main__":
    cli()