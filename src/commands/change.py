import click
import json
import os
import uuid
import shutil
import tempfile
import subprocess
from src.util.config_util import SECRETS_DIR, load_config, save_config

@click.group()
def change():
    """Change a stored component by alias."""
    pass

@click.command()
@click.option('--alias', '-l', required=True, help='Host alias to change.')
@click.option('--new-address', '-a', help='New host address.')
@click.option('--new-alias', '-n', help='New alias for the host.')
def host(alias, new_address, new_alias):
    if not new_address and not new_alias:
        click.echo("Error: Provide either --new-address or --new-alias option.")
        return
    
    config = load_config()
    hosts = config.get('hosts', [])
    
    host_found = None
    for i, h in enumerate(hosts):
        if h['alias'] == alias:
            host_found = i
            break
    
    if host_found is None:
        click.echo(f"Error: Host with alias '{alias}' not found.")
        return
    
    if new_alias and new_alias != alias:
        for h in hosts:
            if h['alias'] == new_alias:
                click.echo(f"Error: Host with alias '{new_alias}' already exists.")
                return
    
    click.echo(f"Changing host '{alias}':")
    if new_address:
        click.echo(f"  Address: {hosts[host_found]['address']} → {new_address}")
        hosts[host_found]['address'] = new_address
    if new_alias:
        click.echo(f"  Alias: {alias} → {new_alias}")
        hosts[host_found]['alias'] = new_alias
    
    save_config(config)
    click.echo("Host updated successfully.")

@click.command()
@click.option('--alias', '-l', required=True, help='Port alias to change.')
@click.option('--new-value', '-v', type=int, help='New port value.')
@click.option('--new-alias', '-n', help='New alias for the port.')
def port(alias, new_value, new_alias):
    if not new_value and not new_alias:
        click.echo("Error: Provide either --new-value or --new-alias option.")
        return
    
    config = load_config()
    ports = config.get('ports', [])
    
    port_found = None
    for i, p in enumerate(ports):
        if p['alias'] == alias:
            port_found = i
            break
    
    if port_found is None:
        click.echo(f"Error: Port with alias '{alias}' not found.")
        return
    
    if new_alias and new_alias != alias:
        for p in ports:
            if p['alias'] == new_alias:
                click.echo(f"Error: Port with alias '{new_alias}' already exists.")
                return
    
    click.echo(f"Changing port '{alias}':")
    if new_value:
        click.echo(f"  Value: {ports[port_found]['value']} → {new_value}")
        ports[port_found]['value'] = new_value
    if new_alias:
        click.echo(f"  Alias: {alias} → {new_alias}")
        ports[port_found]['alias'] = new_alias
    
    save_config(config)
    click.echo("Port updated successfully.")

@click.command()
@click.option('--alias', '-l', required=True, help='Username alias to change.')
@click.option('--new-value', '-v', help='New username value.')
@click.option('--new-alias', '-n', help='New alias for the username.')
def username(alias, new_value, new_alias):
    if not new_value and not new_alias:
        click.echo("Error: Provide either --new-value or --new-alias option.")
        return
    
    config = load_config()
    usernames = config.get('usernames', [])
    
    username_found = None
    for i, u in enumerate(usernames):
        if u['alias'] == alias:
            username_found = i
            break
    
    if username_found is None:
        click.echo(f"Error: Username with alias '{alias}' not found.")
        return
    
    if new_alias and new_alias != alias:
        for u in usernames:
            if u['alias'] == new_alias:
                click.echo(f"Error: Username with alias '{new_alias}' already exists.")
                return
    
    click.echo(f"Changing username '{alias}':")
    if new_value:
        click.echo(f"  Value: {usernames[username_found]['value']} → {new_value}")
        usernames[username_found]['value'] = new_value
    if new_alias:
        click.echo(f"  Alias: {alias} → {new_alias}")
        usernames[username_found]['alias'] = new_alias
    
    save_config(config)
    click.echo("Username updated successfully.")

@click.command()
@click.option('--alias', '-l', required=True, help='Password alias to change.')
@click.option('--new-value', '-v', help='New password value.')
@click.option('--new-alias', '-n', help='New alias for the password.')
def password(alias, new_value, new_alias):
    if not new_value and not new_alias:
        click.echo("Error: Provide either --new-value or --new-alias option.")
        return
    
    config = load_config()
    passwords = config.get('passwords', [])
    
    password_found = None
    for i, p in enumerate(passwords):
        if p['alias'] == alias:
            password_found = i
            break
    
    if password_found is None:
        click.echo(f"Error: Password with alias '{alias}' not found.")
        return
    
    if new_alias and new_alias != alias:
        for p in passwords:
            if p['alias'] == new_alias:
                click.echo(f"Error: Password with alias '{new_alias}' already exists.")
                return
    
    click.echo(f"Changing password '{alias}':")
    if new_value:
        click.echo(f"  Value: **** → ****")
        passwords[password_found]['value'] = new_value
    if new_alias:
        click.echo(f"  Alias: {alias} → {new_alias}")
        passwords[password_found]['alias'] = new_alias
    
    save_config(config)
    click.echo("Password updated successfully.")

@click.command()
@click.option('--alias', '-l', required=True, help='Keypair alias to change.')
@click.option('--new-path', '-p', help='New keypair file path.')
@click.option('--new-alias', '-n', help='New alias for the keypair.')
def keypair(alias, new_path, new_alias):
    if not new_path and not new_alias:
        click.echo("Error: Provide either --new-path or --new-alias option.")
        return
    
    config = load_config()
    keypairs = config.get('keypairs', [])
    
    keypair_found = None
    for i, k in enumerate(keypairs):
        if k['alias'] == alias:
            keypair_found = i
            break
    
    if keypair_found is None:
        click.echo(f"Error: Keypair with alias '{alias}' not found.")
        return
    
    if new_alias and new_alias != alias:
        for k in keypairs:
            if k['alias'] == new_alias:
                click.echo(f"Error: Keypair with alias '{new_alias}' already exists.")
                return
    
    if new_path:
        os.makedirs(SECRETS_DIR, exist_ok=True)
        
        keypair_uuid = str(uuid.uuid4())
        new_keypair_path = os.path.join(SECRETS_DIR, keypair_uuid)
        
        if new_path == '-':
            click.echo("Opening vi editor. Paste your new keypair content and save.")
            
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
                
                click.echo("New keypair content saved to secrets directory.")
            except Exception as e:
                click.echo(f"Error during vi editor operation: {e}")
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                return
        else:
            if not os.path.exists(new_path):
                click.echo(f"Error: Keypair file '{new_path}' does not exist.")
                return
            
            try:
                shutil.copy2(new_path, new_keypair_path)
                os.chmod(new_keypair_path, 0o600)
                click.echo(f"New keypair file copied from '{new_path}' to secrets directory.")
            except Exception as e:
                click.echo(f"Error copying keypair file: {e}")
                return
        
        old_path = keypairs[keypair_found]['path']
        if old_path.startswith('src/secrets/'):
            old_uuid = old_path.replace('src/secrets/', '')
            old_file_path = os.path.join(SECRETS_DIR, old_uuid)
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                    click.echo("Old keypair file removed.")
                except Exception as e:
                    click.echo(f"Warning: Could not remove old keypair file: {e}")
        
        relative_path = os.path.join('src', 'secrets', keypair_uuid)
        click.echo(f"  Path: {old_path} → {relative_path}")
        keypairs[keypair_found]['path'] = relative_path
    
    if new_alias:
        click.echo(f"  Alias: {alias} → {new_alias}")
        keypairs[keypair_found]['alias'] = new_alias
    
    save_config(config)
    click.echo("Keypair updated successfully.")

@click.command()
@click.option('--alias', '-l', required=True, help='Environment alias to change.')
@click.option('--new-alias', '-n', help='New alias for the environment.')
@click.option('--host-alias', '-h', help='New host alias.')
@click.option('--port-alias', '-p', help='New port alias.')
@click.option('--username-alias', '-u', help='New username alias.')
@click.option('--password-alias', '-w', help='New password alias.')
@click.option('--keypair-alias', '-k', help='New keypair alias.')
@click.option('--proxy-alias', '-j', help='New proxy environment alias.')
def environment(alias, new_alias, host_alias, port_alias, username_alias, password_alias, keypair_alias, proxy_alias):
    if not any([new_alias, host_alias, port_alias, username_alias, password_alias, keypair_alias, proxy_alias]):
        click.echo("Error: Provide at least one option to change.")
        return
    
    config = load_config()
    environments = config.get('environments', [])
    
    env_found = None
    for i, e in enumerate(environments):
        if e['alias'] == alias:
            env_found = i
            break
    
    if env_found is None:
        click.echo(f"Error: Environment with alias '{alias}' not found.")
        return
    
    if new_alias and new_alias != alias:
        for e in environments:
            if e['alias'] == new_alias:
                click.echo(f"Error: Environment with alias '{new_alias}' already exists.")
                return
    
    if host_alias:
        hosts = [h['alias'] for h in config.get('hosts', [])]
        if host_alias not in hosts:
            click.echo(f"Error: Host with alias '{host_alias}' not found.")
            return
    
    if port_alias and port_alias != '22':
        try:
            int(port_alias)
        except ValueError:
            ports = [p['alias'] for p in config.get('ports', [])]
            if port_alias not in ports:
                click.echo(f"Error: Port with alias '{port_alias}' not found.")
                return
    
    if username_alias:
        usernames = [u['alias'] for u in config.get('usernames', [])]
        if username_alias not in usernames:
            click.echo(f"Error: Username with alias '{username_alias}' not found.")
            return
    
    if password_alias:
        passwords = [p['alias'] for p in config.get('passwords', [])]
        if password_alias not in passwords:
            click.echo(f"Error: Password with alias '{password_alias}' not found.")
            return
    
    if keypair_alias:
        keypairs = [k['alias'] for k in config.get('keypairs', [])]
        if keypair_alias not in keypairs:
            click.echo(f"Error: Keypair with alias '{keypair_alias}' not found.")
            return
    
    if proxy_alias:
        if proxy_alias == alias:
            click.echo("Error: Environment cannot use itself as proxy jump.")
            return
        
        proxy_envs = [e['alias'] for e in config.get('environments', [])]
        if proxy_alias not in proxy_envs:
            click.echo(f"Error: Proxy environment with alias '{proxy_alias}' not found.")
            return
    
    click.echo(f"Changing environment '{alias}':")
    
    if new_alias:
        click.echo(f"  Alias: {alias} → {new_alias}")
        environments[env_found]['alias'] = new_alias
    
    if host_alias:
        click.echo(f"  Host: {environments[env_found]['host_alias']} → {host_alias}")
        environments[env_found]['host_alias'] = host_alias
    
    if port_alias:
        click.echo(f"  Port: {environments[env_found].get('port_alias', '22')} → {port_alias}")
        environments[env_found]['port_alias'] = port_alias
    
    if username_alias:
        click.echo(f"  Username: {environments[env_found].get('username_alias', 'None')} → {username_alias}")
        environments[env_found]['username_alias'] = username_alias
    
    if password_alias:
        old_pwd = environments[env_found].get('password_alias')
        click.echo(f"  Password: {old_pwd if old_pwd else 'None'} → {password_alias}")
        environments[env_found]['password_alias'] = password_alias
    
    if keypair_alias:
        old_key = environments[env_found].get('keypair_alias')
        click.echo(f"  Keypair: {old_key if old_key else 'None'} → {keypair_alias}")
        environments[env_found]['keypair_alias'] = keypair_alias
    
    if proxy_alias:
        old_proxy = environments[env_found].get('proxy_alias')
        click.echo(f"  Proxy: {old_proxy if old_proxy else 'None'} → {proxy_alias}")
        environments[env_found]['proxy_alias'] = proxy_alias
    
    save_config(config)
    click.echo("Environment updated successfully.")

change.add_command(host)

change.add_command(port)

change.add_command(username)
change.add_command(username, name='user')

change.add_command(password)
change.add_command(password, name='pwd')

change.add_command(keypair)
change.add_command(keypair, name='kp')

change.add_command(environment)
change.add_command(environment, name='env')