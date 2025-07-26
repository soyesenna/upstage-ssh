import click
import json
import os

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

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

@click.group()
def add():
    pass

@click.command()
@click.option('--value', '-v', required=True, help='Host value. Can be an IP address or a domain name.')
@click.option('--alias', '-l', required=False, help='Host alias. If not provided, the address will be used as the alias.')
def host(value, alias):
    if alias is None:
        alias = value
    
    config = load_config()
    
    for host in config['hosts']:
        if host['alias'] == alias:
            click.echo(f"Error: Host with alias '{alias}' already exists.")
            return
    
    config['hosts'].append({
        "address": value,
        "alias": alias
    })
    
    save_config(config)
    click.echo(f"Host '{value}' added with alias '{alias}'.")

@click.command()
@click.option('--value', '-v', required=True, help='Port value.')
@click.option('--alias', '-l', required=False, help='Port alias. If not provided, the value will be used as the alias.')
def port(value, alias):
    if alias is None:
        alias = value
    
    config = load_config()
    
    for port in config['ports']:
        if port['alias'] == alias:
            click.echo(f"Error: Port with alias '{alias}' already exists.")
            return
    
    try:
        port_value = int(value)
    except ValueError:
        click.echo(f"Error: Port value must be a number.")
        return
    
    config['ports'].append({
        "value": port_value,
        "alias": alias
    })
    
    save_config(config)
    click.echo(f"Port '{value}' added with alias '{alias}'.")
        
@click.command()
@click.option('--value', '-v', required=True, help='Username value.')
@click.option('--alias', '-l', required=False, help='Username alias. If not provided, the value will be used as the alias.')
def username(value, alias):
    if alias is None:
        alias = value
    
    config = load_config()
    
    for user in config['usernames']:
        if user['alias'] == alias:
            click.echo(f"Error: Username with alias '{alias}' already exists.")
            return
    
    config['usernames'].append({
        "value": value,
        "alias": alias
    })
    
    save_config(config)
    click.echo(f"Username '{value}' added with alias '{alias}'.")

@click.command()
@click.option('--value', '-v', required=True, help='Password value.')
@click.option('--alias', '-l', required=False, help='Password alias. If not provided, the value will be used as the alias.')
def password(value, alias):
    if alias is None:
        alias = value
    
    config = load_config()
    
    for pwd in config['passwords']:
        if pwd['alias'] == alias:
            click.echo(f"Error: Password with alias '{alias}' already exists.")
            return
    
    config['passwords'].append({
        "value": value,
        "alias": alias
    })
    
    save_config(config)
    click.echo(f"Password added with alias '{alias}'.")
        
@click.command()
@click.option('--path', '-p', required=True, help='Keypair path.')
@click.option('--alias', '-l', required=True, help='Keypair alias. Must be provided.')
def keypair(path, alias):
    config = load_config()
    
    for kp in config['keypairs']:
        if kp['alias'] == alias:
            click.echo(f"Error: Keypair with alias '{alias}' already exists.")
            return
    
    config['keypairs'].append({
        "path": path,
        "alias": alias
    })
    
    save_config(config)
    click.echo(f"Keypair at '{path}' added with alias '{alias}'.")

add.add_command(host)
add.add_command(port)
add.add_command(username)
add.add_command(password)
add.add_command(keypair)
