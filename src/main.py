import click
from src.commands.add import add
from src.commands.list import list
from src.commands.remove import remove
from src.commands.connect import connect
from src.commands.find import find
from src.commands.change import change
from src.commands.init import init

@click.group()
def cli():
    pass

cli.add_command(init)
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