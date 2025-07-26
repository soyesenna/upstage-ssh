import click
import json
import os
import uuid
import shutil
import tempfile
import subprocess

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'info.json')
SECRETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'secrets')

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
@click.option('--path', '-p', required=False, help='Keypair file path. If not provided, opens vi editor to input keypair content.')
@click.option('--alias', '-l', required=True, help='Keypair alias. Must be provided.')
def keypair(path, alias):
    config = load_config()
    
    for kp in config['keypairs']:
        if kp['alias'] == alias:
            click.echo(f"Error: Keypair with alias '{alias}' already exists.")
            return
    
    os.makedirs(SECRETS_DIR, exist_ok=True)
    
    keypair_uuid = str(uuid.uuid4())
    new_keypair_path = os.path.join(SECRETS_DIR, keypair_uuid)
    
    if path:
        if not os.path.exists(path):
            click.echo(f"Error: Keypair file '{path}' does not exist.")
            return
        
        try:
            shutil.copy2(path, new_keypair_path)
            os.chmod(new_keypair_path, 0o600)
            click.echo(f"Keypair file copied from '{path}' to secrets directory.")
        except Exception as e:
            click.echo(f"Error copying keypair file: {e}")
            return
    else:
        click.echo("Opening vi editor. Paste your keypair content and save.")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem') as tmp_file:
            tmp_file_path = tmp_file.name
        
        try:
            subprocess.call(['vi', tmp_file_path])
            
            with open(tmp_file_path, 'r') as f:
                content = f.read().strip()
            
            if not content:
                click.echo("Error: No keypair content provided.")
                os.unlink(tmp_file_path)
                return
            
            with open(new_keypair_path, 'w') as f:
                f.write(content)
            
            os.chmod(new_keypair_path, 0o600)
            
            os.unlink(tmp_file_path)
            
            click.echo("Keypair content saved to secrets directory.")
        except Exception as e:
            click.echo(f"Error during vi editor operation: {e}")
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            return
    
    relative_path = os.path.join('src', 'secrets', keypair_uuid)
    
    config['keypairs'].append({
        "path": relative_path,
        "alias": alias
    })
    
    save_config(config)
    click.echo(f"Keypair added with alias '{alias}'.")

add.add_command(host)
add.add_command(port)
add.add_command(username)
add.add_command(password)
add.add_command(keypair)
