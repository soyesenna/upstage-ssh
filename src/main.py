import click
from commands.add import add
from commands.list import list
from commands.remove import remove
from commands.connect import connect
from commands.find import find
from commands.change import change

@click.group()
def cli():
    pass

cli.add_command(add)
cli.add_command(list)
cli.add_command(remove)
cli.add_command(remove, name='rm')
cli.add_command(connect)
cli.add_command(connect, name='con')
cli.add_command(find)
cli.add_command(change)

if __name__ == "__main__":
    cli()