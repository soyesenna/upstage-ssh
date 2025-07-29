import click
import os
from src.util.config_util import SECRETS_DIR, load_config, save_config

@click.group()
def remove():
    """Remove a stored component by alias."""
    pass

@click.command()
@click.option('--alias', '-l', required=True, help='Host alias to remove.')
def host(alias):
    config = load_config()
    
    hosts = config.get('hosts', [])
    original_length = len(hosts)
    config['hosts'] = [h for h in hosts if h['alias'] != alias]
    
    if len(config['hosts']) < original_length:
        save_config(config)
        click.echo(f"Host with alias '{alias}' has been removed.")
    else:
        click.echo(f"Error: Host with alias '{alias}' not found.")

@click.command()
@click.option('--alias', '-l', required=True, help='Port alias to remove.')
def port(alias):
    config = load_config()
    
    ports = config.get('ports', [])
    original_length = len(ports)
    config['ports'] = [p for p in ports if p['alias'] != alias]
    
    if len(config['ports']) < original_length:
        save_config(config)
        click.echo(f"Port with alias '{alias}' has been removed.")
    else:
        click.echo(f"Error: Port with alias '{alias}' not found.")

@click.command()
@click.option('--alias', '-l', required=True, help='Username alias to remove.')
def username(alias):
    config = load_config()
    
    usernames = config.get('usernames', [])
    original_length = len(usernames)
    config['usernames'] = [u for u in usernames if u['alias'] != alias]
    
    if len(config['usernames']) < original_length:
        save_config(config)
        click.echo(f"Username with alias '{alias}' has been removed.")
    else:
        click.echo(f"Error: Username with alias '{alias}' not found.")

@click.command()
@click.option('--alias', '-l', required=True, help='Password alias to remove.')
def password(alias):
    config = load_config()
    
    passwords = config.get('passwords', [])
    original_length = len(passwords)
    config['passwords'] = [p for p in passwords if p['alias'] != alias]
    
    if len(config['passwords']) < original_length:
        save_config(config)
        click.echo(f"Password with alias '{alias}' has been removed.")
    else:
        click.echo(f"Error: Password with alias '{alias}' not found.")

@click.command()
@click.option('--alias', '-l', required=True, help='Keypair alias to remove.')
def keypair(alias):
    config = load_config()
    
    keypairs = config.get('keypairs', [])
    keypair_to_remove = None
    
    for kp in keypairs:
        if kp['alias'] == alias:
            keypair_to_remove = kp
            break
    
    if keypair_to_remove:
        keypair_path = keypair_to_remove['path']
        
        if keypair_path.startswith('src/secrets/'): 
            uuid_part = keypair_path.replace('src/secrets/', '')
            actual_file_path = os.path.join(SECRETS_DIR, uuid_part)
            
            if os.path.exists(actual_file_path):
                try:
                    os.remove(actual_file_path)
                    click.echo(f"Keypair file removed from secrets directory.")
                except Exception as e:
                    click.echo(f"Warning: Could not remove keypair file: {e}")
        
        config['keypairs'] = [kp for kp in keypairs if kp['alias'] != alias]
        save_config(config)
        click.echo(f"Keypair with alias '{alias}' has been removed.")
    else:
        click.echo(f"Error: Keypair with alias '{alias}' not found.")

@click.command()
@click.option('--alias', '-l', required=True, help='Environment alias to remove.')
def environment(alias):
    config = load_config()
    
    environments = config.get('environments', [])
    original_length = len(environments)
    config['environments'] = [e for e in environments if e['alias'] != alias]
    
    if len(config.get('environments', [])) < original_length:
        save_config(config)
        click.echo(f"Environment with alias '{alias}' has been removed.")
    else:
        click.echo(f"Error: Environment with alias '{alias}' not found.")

remove.add_command(host)

remove.add_command(port)

remove.add_command(username)
remove.add_command(username, name='user')

remove.add_command(password)
remove.add_command(password, name='pwd')

remove.add_command(keypair)
remove.add_command(keypair, name='kp')

remove.add_command(environment)
remove.add_command(environment, name='env')