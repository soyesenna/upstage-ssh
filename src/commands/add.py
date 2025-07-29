import click
import os
import uuid
import shutil
import tempfile
import subprocess
from src.util.config_util import SECRETS_DIR, load_config, save_config

@click.group()
def add():
    """Add a new component to the configuration."""
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
    
@click.command()
@click.option('--host-alias', '-h', required=True, help='Host alias to use for the connection.')
@click.option('--port-alias', '-p', required=False, default='22', help='Port alias to use (default: 22).')
@click.option('--username-alias', '-u', required=False, help='Username alias to use.')
@click.option('--password-alias', '-w', required=False, help='Password alias to use.')
@click.option('--keypair-alias', '-k', required=False, help='Keypair alias to use.')
@click.option('--proxy-alias', '-j', required=False, help='Environment alias to use as proxy jump (bastion host).')
@click.option('--alias', '-l', required=True, help='Environment alias for this SSH connection configuration.')
def environment(host_alias, port_alias, username_alias, password_alias, keypair_alias, proxy_alias, alias):
    """Create an SSH environment by combining registered components."""
    config = load_config()
    
    environments = config.get('environments', [])
    for env in environments:
        if env['alias'] == alias:
            click.echo(f"Error: Environment with alias '{alias}' already exists.")
            return
    
    host_found = None
    for h in config.get('hosts', []):
        if h['alias'] == host_alias:
            host_found = h
            break
    
    if not host_found:
        click.echo(f"Error: Host with alias '{host_alias}' not found.")
        return
    
    port_found = None
    if port_alias:
        try:
            port_value = int(port_alias)
            port_found = {'value': port_value, 'alias': port_alias}
        except ValueError:
            for p in config.get('ports', []):
                if p['alias'] == port_alias:
                    port_found = p
                    break
            
            if not port_found:
                click.echo(f"Error: Port with alias '{port_alias}' not found.")
                return
    else:
        port_found = {'value': 22, 'alias': '22'}
    
    username_found = None
    if username_alias:
        for u in config.get('usernames', []):
            if u['alias'] == username_alias:
                username_found = u
                break
        
        if not username_found:
            click.echo(f"Error: Username with alias '{username_alias}' not found.")
            return
    
    password_found = None
    if password_alias:
        for p in config.get('passwords', []):
            if p['alias'] == password_alias:
                password_found = p
                break
        
        if not password_found:
            click.echo(f"Error: Password with alias '{password_alias}' not found.")
            return
    
    keypair_found = None
    if keypair_alias:
        for k in config.get('keypairs', []):
            if k['alias'] == keypair_alias:
                keypair_found = k
                break
        
        if not keypair_found:
            click.echo(f"Error: Keypair with alias '{keypair_alias}' not found.")
            return
    
    proxy_found = None
    if proxy_alias:
        for e in config.get('environments', []):
            if e['alias'] == proxy_alias:
                proxy_found = e
                break
        
        if not proxy_found:
            click.echo(f"Error: Proxy environment with alias '{proxy_alias}' not found.")
            return
        
        if proxy_alias == alias:
            click.echo("Error: Environment cannot use itself as proxy jump.")
            return
    
    if not password_found and not keypair_found:
        click.echo("Error: Either password or keypair must be provided for authentication.")
        return
    
    new_env = {
        "alias": alias,
        "host_alias": host_alias,
        "port_alias": port_alias if port_alias else "22",
        "username_alias": username_alias if username_alias else None,
        "password_alias": password_alias if password_alias else None,
        "keypair_alias": keypair_alias if keypair_alias else None,
        "proxy_alias": proxy_alias if proxy_alias else None
    }
    
    if 'environments' not in config:
        config['environments'] = []
    
    config['environments'].append(new_env)
    
    save_config(config)
    
    click.echo(f"Environment '{alias}' created successfully.")
    click.echo(f"  Host: {host_found['address']} (alias: {host_alias})")
    click.echo(f"  Port: {port_found['value']} (alias: {port_found['alias']})")
    
    if username_found:
        click.echo(f"  Username: {username_found['value']} (alias: {username_alias})")
    
    if password_found:
        click.echo(f"  Password: **** (alias: {password_alias})")
    
    if keypair_found:
        click.echo(f"  Keypair: {keypair_found['path']} (alias: {keypair_alias})")
    
    if proxy_found:
        click.echo(f"  Proxy Jump: {proxy_alias}")

add.add_command(host)

add.add_command(port)

add.add_command(username)
add.add_command(username, name='user')

add.add_command(password)
add.add_command(password, name='pwd')

add.add_command(keypair)
add.add_command(keypair, name='kp')

add.add_command(environment)
add.add_command(environment, name='env')
