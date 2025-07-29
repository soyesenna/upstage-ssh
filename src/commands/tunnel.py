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
    host = next(h for h in config['hosts'] if h['alias'] == env_config['host_alias'])['address']
    port = next((p for p in config.get('ports', []) if p['alias'] == env_config['port_alias']), {'value': 22})['value']
    username = next((u['value'] for u in config.get('usernames', []) if u['alias'] == env_config['username_alias']), None)
    password_alias = env_config.get('password_alias')
    keypair_alias = env_config.get('keypair_alias')
    proxy_alias = env_config.get('proxy_alias')

    ssh_cmd = ['ssh']

    if forwarding:
        ssh_cmd.extend(['-N', '-f'])
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
        proxy_cmd = build_ssh_command(proxy_env, config)[1:]
        proxy_str = ' '.join(proxy_cmd[:-1]) + proxy_cmd[-1]
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

@click.command()
def manage():
    """List current tunnels and allow killing them."""
    import re
    
    config = load_config()
    
    try:
        ps_output = subprocess.check_output(['ps', 'aux']).decode('utf-8')
    except subprocess.CalledProcessError as e:
        click.echo(f"Error getting process list: {e}")
        return

    tunnel_lines = [line for line in ps_output.splitlines() if 'ssh' in line.lower() and ('-L' in line or '-R' in line) and '-N' in line]

    if not tunnel_lines:
        click.echo("No active SSH tunnels found.")
        return

    tunnels = []
    for line in tunnel_lines:
        parts = re.split(r'\s+', line)
        pid = parts[1]
        cmd_parts = ' '.join(parts[10:])
        
        tunnel_type = "Local" if "-L" in cmd_parts else "Remote" if "-R" in cmd_parts else "Unknown"
        
        forwarding_match = re.search(r'-[LR]\s+(\S+)', cmd_parts)
        forwarding = forwarding_match.group(1) if forwarding_match else "N/A"
        
        local_port = "N/A"
        remote_port = "N/A" 
        host_address = "N/A"
        host_alias = "N/A"
        
        if forwarding != "N/A":
            if tunnel_type == "Local":
                parts = forwarding.split(':')
                if len(parts) == 3:
                    local_port = parts[0]
                    host_address = parts[1]
                    remote_port = parts[2]
            elif tunnel_type == "Remote":
                parts = forwarding.split(':')
                if len(parts) == 3:
                    remote_port = parts[0]
                    host_address = parts[1]
                    local_port = parts[2]
        
        for h in config.get('hosts', []):
            if h['address'] == host_address:
                host_alias = h['alias']
                break
        
        host_match = re.search(r'(\S+)$', cmd_parts)
        target = host_match.group(1) if host_match else "N/A"
        
        tunnels.append({
            'pid': pid,
            'type': tunnel_type,
            'local_port': local_port,
            'remote_port': remote_port,
            'host': f"{host_alias}" if host_alias != "N/A" else host_address,
            'target': target,
            'command': cmd_parts
        })

    click.echo("\n┌────────┬──────────┬─────────┬────────────┬─────────────┬──────────────────────────────────┬────────────────────┐")
    click.echo("│ Number │   PID    │  Type   │ Local Port │ Remote Port │         Host (alias)             │      Target        │")
    click.echo("├────────┼──────────┼─────────┼────────────┼─────────────┼──────────────────────────────────┼────────────────────┤")
    
    for idx, tunnel in enumerate(tunnels, 1):
        click.echo(f"│ {idx:^6} │ {tunnel['pid']:^8} │ {tunnel['type']:^7} │ {tunnel['local_port']:^10} │ {tunnel['remote_port']:^11} │ {tunnel['host']:^32} │ {tunnel['target']:^18} │")
    
    click.echo("└────────┴──────────┴─────────┴────────────┴─────────────┴──────────────────────────────────┴────────────────────┘")
    
    click.echo(f"\nTotal active tunnels: {len(tunnels)}\n")

    selection = click.prompt("Enter the number(s) of the tunnel(s) to kill (comma-separated, or 'all' or 'none')", default='none')
    if selection.lower() == 'none':
        click.echo("No tunnels killed.")
        return
    elif selection.lower() == 'all':
        to_kill = [t['pid'] for t in tunnels]
    else:
        try:
            indices = [int(i.strip()) for i in selection.split(',')]
            to_kill = [tunnels[idx-1]['pid'] for idx in indices if 1 <= idx <= len(tunnels)]
        except (ValueError, IndexError):
            click.echo("Invalid selection.")
            return

    for pid in to_kill:
        try:
            subprocess.run(['kill', pid], check=True)
            click.echo(f"✓ Killed tunnel with PID {pid}")
        except subprocess.CalledProcessError as e:
            click.echo(f"✗ Error killing PID {pid}: {e}")

tunnel.add_command(local)
tunnel.add_command(remote)
tunnel.add_command(manage)