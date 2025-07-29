import click
import os
import subprocess
from src.util.config_util import SECRETS_DIR, load_config


def get_component_value(config, component_type, alias):
    components = config.get(f"{component_type}s", [])
    for comp in components:
        if comp.get('alias') == alias:
            if component_type == 'host':
                return comp.get('address')
            elif component_type == 'keypair':
                return comp.get('path')
            else:
                return comp.get('value')
    return None

def build_proxy_command(proxy_env, config):
    """Build the ProxyCommand string for SSH."""
    proxy_host = get_component_value(config, 'host', proxy_env['host_alias'])
    if not proxy_host:
        raise ValueError(f"Proxy host with alias '{proxy_env['host_alias']}' not found.")
    
    proxy_port = 22
    if proxy_env.get('port_alias'):
        port_value = get_component_value(config, 'port', proxy_env['port_alias'])
        if port_value:
            proxy_port = port_value
    
    proxy_username = ""
    if proxy_env.get('username_alias'):
        proxy_username = get_component_value(config, 'username', proxy_env['username_alias'])
        if not proxy_username:
            raise ValueError(f"Proxy username with alias '{proxy_env['username_alias']}' not found.")
    
    proxy_cmd_parts = ['ssh', '-W', '%h:%p']
    if proxy_port != 22:
        proxy_cmd_parts.extend(['-p', str(proxy_port)])
    
    if proxy_env.get('keypair_alias'):
        keypair_path = get_component_value(config, 'keypair', proxy_env['keypair_alias'])
        if keypair_path:
            if keypair_path.startswith('src/secrets/'):
                uuid_part = keypair_path.replace('src/secrets/', '')
                actual_keypair_path = os.path.join(SECRETS_DIR, uuid_part)
            else:
                actual_keypair_path = keypair_path
            
            if os.path.exists(actual_keypair_path):
                proxy_cmd_parts.extend(['-i', actual_keypair_path])
    
    if proxy_username:
        proxy_cmd_parts.append(f"{proxy_username}@{proxy_host}")
    else:
        proxy_cmd_parts.append(proxy_host)
    
    return ' '.join(proxy_cmd_parts)

@click.command()
@click.argument('alias', required=True)
@click.option('--dry-run', is_flag=True, help='Show the SSH command without executing it.')
def connect(alias, dry_run):
    """Connect to SSH using a stored environment configuration."""
    config = load_config()
    
    environments = config.get('environments', [])
    env_found = None
    for env in environments:
        if env['alias'] == alias:
            env_found = env
            break
    
    if not env_found:
        click.echo(f"Error: Environment with alias '{alias}' not found.")
        click.echo("\nAvailable environments:")
        for env in environments:
            click.echo(f"  - {env['alias']}")
        return
    
    host = get_component_value(config, 'host', env_found['host_alias'])
    if not host:
        click.echo(f"Error: Host with alias '{env_found['host_alias']}' not found.")
        return
    
    port = 22
    if env_found.get('port_alias'):
        port_value = get_component_value(config, 'port', env_found['port_alias'])
        if port_value:
            port = port_value
    
    ssh_command = ['ssh']
    
    if env_found.get('keypair_alias'):
        keypair_path = get_component_value(config, 'keypair', env_found['keypair_alias'])
        if not keypair_path:
            click.echo(f"Error: Keypair with alias '{env_found['keypair_alias']}' not found.")
            return
        
        if keypair_path.startswith('src/secrets/'):
            uuid_part = keypair_path.replace('src/secrets/', '')
            actual_keypair_path = os.path.join(SECRETS_DIR, uuid_part)
        else:
            actual_keypair_path = keypair_path
        
        if not os.path.exists(actual_keypair_path):
            click.echo(f"Error: Keypair file not found at '{actual_keypair_path}'.")
            return
        
        ssh_command.extend(['-i', actual_keypair_path])
    
    if env_found.get('proxy_alias'):
        proxy_env = None
        for env in environments:
            if env['alias'] == env_found['proxy_alias']:
                proxy_env = env
                break
        
        if not proxy_env:
            click.echo(f"Error: Proxy environment with alias '{env_found['proxy_alias']}' not found.")
            return
        
        if proxy_env.get('password_alias') and not proxy_env.get('keypair_alias'):
            click.echo("Error: Password authentication is not supported for proxy jump.")
            click.echo("Proxy jump requires key-based authentication.")
            return
        
        try:
            proxy_command = build_proxy_command(proxy_env, config)
            ssh_command.extend(['-o', f'ProxyCommand={proxy_command}'])
        except ValueError as e:
            click.echo(f"Error: {e}")
            return
    
    ssh_command.extend(['-p', str(port)])
    
    username = ""
    if env_found.get('username_alias'):
        username = get_component_value(config, 'username', env_found['username_alias'])
        if not username:
            click.echo(f"Error: Username with alias '{env_found['username_alias']}' not found.")
            return
    
    if username:
        connection_string = f"{username}@{host}"
    else:
        connection_string = host
    
    ssh_command.append(connection_string)
    
    if env_found.get('password_alias'):
        password = get_component_value(config, 'password', env_found['password_alias'])
        if not password:
            click.echo(f"Error: Password with alias '{env_found['password_alias']}' not found.")
            return
        
        if not env_found.get('keypair_alias'):
            click.echo("Warning: Password authentication is less secure than key-based authentication.")
            click.echo("Consider using keypair authentication instead.")
            
            try:
                subprocess.run(['which', 'sshpass'], capture_output=True, check=True)
                ssh_command = ['sshpass', '-p', password] + ssh_command
            except subprocess.CalledProcessError:
                click.echo("\nError: sshpass is not installed. Password authentication requires sshpass.")
                click.echo("Install it with: brew install hudochenkov/sshpass/sshpass (macOS) or apt-get install sshpass (Linux)")
                return
    
    if dry_run:
        display_command = ssh_command.copy()
        if 'sshpass' in display_command:
            pwd_index = display_command.index('-p') + 1
            display_command[pwd_index] = '****'
        
        click.echo("SSH command that would be executed:")
        click.echo(" ".join(display_command))
        return
    
    click.echo(f"Connecting to '{alias}' environment...")
    click.echo(f"Host: {host}:{port}")
    if username:
        click.echo(f"User: {username}")
    
    if env_found.get('proxy_alias'):
        click.echo(f"Via proxy: {env_found['proxy_alias']}")
    
    try:
        subprocess.run(ssh_command)
    except KeyboardInterrupt:
        click.echo("\nConnection terminated by user.")
    except Exception as e:
        click.echo(f"Error: Failed to connect: {e}")