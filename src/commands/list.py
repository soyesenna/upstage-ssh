import click
import json
import os
from tabulate import tabulate

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'info.json')

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "hosts": [],
        "ports": [],
        "usernames": [],
        "passwords": [],
        "keypairs": []
    }

def print_table(title, headers, rows):
    if rows:
        click.echo(f"\n{title}:")
        click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        click.echo(f"\n{title}: No data available")

def show_all_info():
    config = load_config()
    
    host_rows = [[h['alias'], h['address']] for h in config.get('hosts', [])]
    print_table("HOSTS", ["Alias", "Address"], host_rows)
    
    port_rows = [[p['alias'], p['value']] for p in config.get('ports', [])]
    print_table("PORTS", ["Alias", "Value"], port_rows)
    
    username_rows = [[u['alias'], u['value']] for u in config.get('usernames', [])]
    print_table("USERNAMES", ["Alias", "Value"], username_rows)
    
    password_rows = [[p['alias'], '****'] for p in config.get('passwords', [])]
    print_table("PASSWORDS", ["Alias", "Value (masked)"], password_rows)
    
    keypair_rows = [[k['alias'], k['path']] for k in config.get('keypairs', [])]
    print_table("KEYPAIRS", ["Alias", "Path"], keypair_rows)

@click.group(invoke_without_command=True)
@click.pass_context
def list(ctx):
    """List stored SSH connection information."""
    if ctx.invoked_subcommand is None:
        show_all_info()

@click.command()
def hosts():
    """List all stored hosts."""
    config = load_config()
    host_rows = [[h['alias'], h['address']] for h in config.get('hosts', [])]
    print_table("HOSTS", ["Alias", "Address"], host_rows)

@click.command()
def ports():
    """List all stored ports."""
    config = load_config()
    port_rows = [[p['alias'], p['value']] for p in config.get('ports', [])]
    print_table("PORTS", ["Alias", "Value"], port_rows)

@click.command()
def usernames():
    """List all stored usernames."""
    config = load_config()
    username_rows = [[u['alias'], u['value']] for u in config.get('usernames', [])]
    print_table("USERNAMES", ["Alias", "Value"], username_rows)

@click.command()
def passwords():
    """List all stored passwords (masked for security)."""
    config = load_config()
    # masking passwords for security
    password_rows = [[p['alias'], '****'] for p in config.get('passwords', [])]
    print_table("PASSWORDS", ["Alias", "Value (masked)"], password_rows)

@click.command()
def keypairs():
    """List all stored keypairs."""
    config = load_config()
    keypair_rows = [[k['alias'], k['path']] for k in config.get('keypairs', [])]
    print_table("KEYPAIRS", ["Alias", "Path"], keypair_rows)

list.add_command(hosts)
list.add_command(ports)
list.add_command(usernames)
list.add_command(passwords)
list.add_command(keypairs)