import click
from tabulate import tabulate
from src.util.config_util import load_config

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
    
    # Environments
    env_rows = []
    for e in config.get('environments', []):
        components = []
        if e.get('host_alias'):
            components.append(f"host:{e['host_alias']}")
        if e.get('port_alias'):
            components.append(f"port:{e['port_alias']}")
        if e.get('username_alias'):
            components.append(f"user:{e['username_alias']}")
        if e.get('password_alias'):
            components.append(f"pwd:****")
        if e.get('keypair_alias'):
            components.append(f"key:{e['keypair_alias']}")
        if e.get('proxy_alias'):
            components.append(f"proxy:{e['proxy_alias']}")
        
        env_rows.append([e['alias'], ', '.join(components)])
    
    print_table("ENVIRONMENTS", ["Alias", "Components"], env_rows)

@click.group(invoke_without_command=True)
@click.pass_context
def list(ctx):
    """List stored SSH connection information."""
    if ctx.invoked_subcommand is None:
        show_all_info()

@click.command()
def host():
    """List all stored hosts."""
    config = load_config()
    host_rows = [[h['alias'], h['address']] for h in config.get('hosts', [])]
    print_table("HOSTS", ["Alias", "Address"], host_rows)

@click.command()
def port():
    """List all stored ports."""
    config = load_config()
    port_rows = [[p['alias'], p['value']] for p in config.get('ports', [])]
    print_table("PORTS", ["Alias", "Value"], port_rows)

@click.command()
def username():
    """List all stored usernames."""
    config = load_config()
    username_rows = [[u['alias'], u['value']] for u in config.get('usernames', [])]
    print_table("USERNAMES", ["Alias", "Value"], username_rows)

@click.command()
def password():
    """List all stored passwords (masked for security)."""
    config = load_config()
    # masking passwords for security
    password_rows = [[p['alias'], '****'] for p in config.get('passwords', [])]
    print_table("PASSWORDS", ["Alias", "Value (masked)"], password_rows)

@click.command()
def keypair():
    """List all stored keypairs."""
    config = load_config()
    keypair_rows = [[k['alias'], k['path']] for k in config.get('keypairs', [])]
    print_table("KEYPAIRS", ["Alias", "Path"], keypair_rows)

@click.command()
def environment():
    config = load_config()
    env_rows = []
    
    for e in config.get('environments', []):
        components = []
        if e.get('host_alias'):
            components.append(f"host:{e['host_alias']}")
        if e.get('port_alias'):
            components.append(f"port:{e['port_alias']}")
        if e.get('username_alias'):
            components.append(f"user:{e['username_alias']}")
        if e.get('password_alias'):
            components.append(f"pwd:****")
        if e.get('keypair_alias'):
            components.append(f"key:{e['keypair_alias']}")
        if e.get('proxy_alias'):
            components.append(f"proxy:{e['proxy_alias']}")
        
        env_rows.append([e['alias'], ', '.join(components)])
    
    print_table("ENVIRONMENTS", ["Alias", "Components"], env_rows)

list.add_command(host)

list.add_command(port)

list.add_command(username)
list.add_command(username, name='user')

list.add_command(password)
list.add_command(password, name='pwd')

list.add_command(keypair)
list.add_command(keypair, name='kp')

list.add_command(environment)
list.add_command(environment, name='env')