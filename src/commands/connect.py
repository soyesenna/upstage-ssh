import click
import json
import os
import subprocess
import sys

# info.json 파일 경로
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'info.json')
SECRETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'secrets')

def load_config():
    """info.json 파일을 로드합니다."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_component_value(config, component_type, alias):
    """주어진 alias로 컴포넌트의 실제 값을 가져옵니다."""
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

@click.command()
@click.argument('alias', required=True)
@click.option('--dry-run', is_flag=True, help='Show the SSH command without executing it.')
def connect(alias, dry_run):
    """Connect to SSH using a stored environment configuration."""
    config = load_config()
    
    # 환경 찾기
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
    
    # 호스트 정보 가져오기
    host = get_component_value(config, 'host', env_found['host_alias'])
    if not host:
        click.echo(f"Error: Host with alias '{env_found['host_alias']}' not found.")
        return
    
    # 포트 정보 가져오기
    port = 22  # 기본값
    if env_found.get('port_alias'):
        port_value = get_component_value(config, 'port', env_found['port_alias'])
        if port_value:
            port = port_value
    
    # SSH 명령어 구성
    ssh_command = ['ssh']
    
    # 포트 옵션
    ssh_command.extend(['-p', str(port)])
    
    # 사용자명 처리
    username = ""
    if env_found.get('username_alias'):
        username = get_component_value(config, 'username', env_found['username_alias'])
        if not username:
            click.echo(f"Error: Username with alias '{env_found['username_alias']}' not found.")
            return
    
    # 키페어 인증 처리
    if env_found.get('keypair_alias'):
        keypair_path = get_component_value(config, 'keypair', env_found['keypair_alias'])
        if not keypair_path:
            click.echo(f"Error: Keypair with alias '{env_found['keypair_alias']}' not found.")
            return
        
        # 상대 경로를 절대 경로로 변환
        if keypair_path.startswith('src/secrets/'):
            # UUID 추출
            uuid_part = keypair_path.replace('src/secrets/', '')
            actual_keypair_path = os.path.join(SECRETS_DIR, uuid_part)
        else:
            # 이전 형식의 경로 처리
            actual_keypair_path = keypair_path
        
        if not os.path.exists(actual_keypair_path):
            click.echo(f"Error: Keypair file not found at '{actual_keypair_path}'.")
            return
        
        ssh_command.extend(['-i', actual_keypair_path])
    
    # 호스트 연결 문자열 구성
    if username:
        connection_string = f"{username}@{host}"
    else:
        connection_string = host
    
    ssh_command.append(connection_string)
    
    # 비밀번호 인증 처리
    if env_found.get('password_alias'):
        password = get_component_value(config, 'password', env_found['password_alias'])
        if not password:
            click.echo(f"Error: Password with alias '{env_found['password_alias']}' not found.")
            return
        
        if not env_found.get('keypair_alias'):
            # 키페어가 없고 비밀번호만 있는 경우
            click.echo("Warning: Password authentication is less secure than key-based authentication.")
            click.echo("Consider using keypair authentication instead.")
            
            # sshpass 확인
            try:
                subprocess.run(['which', 'sshpass'], capture_output=True, check=True)
                # sshpass가 있으면 사용
                ssh_command = ['sshpass', '-p', password] + ssh_command
            except subprocess.CalledProcessError:
                click.echo("\nError: sshpass is not installed. Password authentication requires sshpass.")
                click.echo("Install it with: brew install hudochenkov/sshpass/sshpass (macOS) or apt-get install sshpass (Linux)")
                return
    
    # dry-run 모드
    if dry_run:
        # 비밀번호는 보안상 표시하지 않음
        display_command = ssh_command.copy()
        if 'sshpass' in display_command:
            pwd_index = display_command.index('-p') + 1
            display_command[pwd_index] = '****'
        
        click.echo("SSH command that would be executed:")
        click.echo(" ".join(display_command))
        return
    
    # SSH 연결 실행
    click.echo(f"Connecting to '{alias}' environment...")
    click.echo(f"Host: {host}:{port}")
    if username:
        click.echo(f"User: {username}")
    
    try:
        # SSH 명령 실행 (인터랙티브 모드)
        subprocess.run(ssh_command)
    except KeyboardInterrupt:
        click.echo("\nConnection terminated by user.")
    except Exception as e:
        click.echo(f"Error: Failed to connect: {e}")
