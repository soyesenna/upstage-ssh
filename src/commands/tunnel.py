import click
import subprocess
from typing import Optional
from src.util.config_util import load_config, SECRETS_DIR
import os

@click.group()
def tunnel():
    """SSH tunnel commands for local and remote port forwarding."""
    pass

def build_ssh_command(env_config: dict, config: dict, forwarding: Optional[str] = None) -> list:
    """Build the SSH command list based on environment config."""
    # Find components
    host = next(h for h in config['hosts'] if h['alias'] == env_config['host_alias'])['address']
    port = next((p for p in config.get('ports', []) if p['alias'] == env_config['port_alias']), {'value': 22})['value']
    username = next((u['value'] for u in config.get('usernames', []) if u['alias'] == env_config['username_alias']), None)
    password_alias = env_config.get('password_alias')
    keypair_alias = env_config.get('keypair_alias')
    proxy_alias = env_config.get('proxy_alias')

    ssh_cmd = ['ssh']

    if forwarding:
        ssh_cmd.extend(['-N', '-f'])  # Background and no remote command for tunneling
        ssh_cmd.append(forwarding)

    if username:
        ssh_cmd.extend(['-l', username])

    ssh_cmd.extend(['-p', str(port)])

    if keypair_alias:
        keypair = next(k for k in config['keypairs'] if k['alias'] == keypair_alias)
        key_path = os.path.join(SECRETS_DIR, os.path.basename(keypair['path']))
        ssh_cmd.extend(['-i', key_path])
    elif password_alias:
        password = next(p['value'] for p in config['passwords'] if p['alias'] == password_alias)
        ssh_cmd = ['sshpass', '-p', password] + ssh_cmd

    if proxy_alias:
        proxy_env = next(e for e in config['environments'] if e['alias'] == proxy_alias)
        proxy_cmd = build_ssh_command(proxy_env, config)[1:]  # Exclude 'ssh' for -J
        proxy_str = ' '.join(proxy_cmd[:-1]) + proxy_cmd[-1]  # Rough approximation for -J
        ssh_cmd.extend(['-J', proxy_str])

    ssh_cmd.append(host)
    return ssh_cmd

@click.command()
@click.option('--env', '-e', required=True, help='Environment alias to use for the tunnel.')
@click.option('--local-port', '-L', type=int, required=True, help='Local port to forward.')
@click.option('--remote-host', '-H', required=True, help='Remote host alias to forward to.')
@click.option('--remote-port', '-R', type=int, required=True, help='Remote port to forward to.')
def local(env, local_port, remote_host, remote_port):
    """Create a local port forwarding tunnel."""
    config = load_config()
    env_config = next((e for e in config.get('environments', []) if e['alias'] == env), None)
    if not env_config:
        click.echo(f"Error: Environment '{env}' not found.")
        return
    
    remote_address = next((h['address'] for h in config.get('hosts', []) if h['alias'] == remote_host), None)
    if not remote_address:
        click.echo(f"Error: Host alias '{remote_host}' not found.")
        return
    
    forwarding = f'-L {local_port}:{remote_address}:{remote_port}'
    ssh_cmd = build_ssh_command(env_config, config, forwarding)
    click.echo(f"Executing: {' '.join(ssh_cmd)}")
    try:
        subprocess.run(ssh_cmd, check=True)
        click.echo("Local tunnel established.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error establishing tunnel: {e}")

@click.command()
@click.option('--env', '-e', required=True, help='Environment alias to use for the tunnel.')
@click.option('--remote-port', '-R', type=int, required=True, help='Remote port to forward.')
@click.option('--local-host', '-H', default='localhost', help='Local host to forward from.')
@click.option('--local-port', '-L', type=int, required=True, help='Local port to forward from.')
def remote(env, remote_port, local_host, local_port):
    """Create a remote port forwarding tunnel."""
    config = load_config()
    env_config = next((e for e in config.get('environments', []) if e['alias'] == env), None)
    if not env_config:
        click.echo(f"Error: Environment '{env}' not found.")
        return

    forwarding = f'-R {remote_port}:{local_host}:{local_port}'
    ssh_cmd = build_ssh_command(env_config, config, forwarding)
    click.echo(f"Executing: {' '.join(ssh_cmd)}")
    try:
        subprocess.run(ssh_cmd, check=True)
        click.echo("Remote tunnel established.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error establishing tunnel: {e}")

tunnel.add_command(local)
tunnel.add_command(remote)