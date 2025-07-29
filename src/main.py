import click
from src.commands.add import add
from src.commands.list import list
from src.commands.remove import remove
from src.commands.connect import connect
from src.commands.find import find
from src.commands.change import change
from src.commands.update import update
from src.commands.tunnel import tunnel

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
cli.add_command(update)
cli.add_command(tunnel)

if __name__ == "__main__":
    cli()