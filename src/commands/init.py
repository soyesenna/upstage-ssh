
import click
import platform
import subprocess
import os
import sys

def get_os_type():
    """현재 운영체제 타입을 반환"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'mac'
    elif system == 'linux':
        return 'linux'
    elif system == 'windows':
        return 'windows'
    else:
        return None

def run_command(cmd, shell=False, check=True):
    """명령어 실행 및 결과 반환"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=check)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)

def install_uv(os_type):
    """OS별 uv 설치"""
    click.echo("Installing uv...")
    
    if os_type == 'mac':
        # Homebrew로 설치
        success, output = run_command(['brew', 'install', 'uv'])
        if not success:
            # Homebrew가 없으면 curl로 설치
            click.echo("Homebrew not found. Installing uv with curl...")
            success, output = run_command('curl -LsSf https://astral.sh/uv/install.sh | sh', shell=True)
    elif os_type == 'linux':
        # curl로 설치
        success, output = run_command('curl -LsSf https://astral.sh/uv/install.sh | sh', shell=True)
    elif os_type == 'windows':
        # PowerShell로 설치
        success, output = run_command(['powershell', '-c', 'irm https://astral.sh/uv/install.ps1 | iex'])
    else:
        return False, "Unsupported operating system"
    
    return success, output

def install_git_crypt(os_type):
    """OS별 git-crypt 설치"""
    click.echo("Installing git-crypt...")
    
    if os_type == 'mac':
        # Homebrew로 설치
        success, output = run_command(['brew', 'install', 'git-crypt'])
    elif os_type == 'linux':
        # 먼저 apt-get 시도
        success, output = run_command(['sudo', 'apt-get', 'update'], check=False)
        if success:
            success, output = run_command(['sudo', 'apt-get', 'install', '-y', 'git-crypt'])
        else:
            # yum/dnf 시도
            success, output = run_command(['sudo', 'yum', 'install', '-y', 'git-crypt'], check=False)
            if not success:
                success, output = run_command(['sudo', 'dnf', 'install', '-y', 'git-crypt'], check=False)
    elif os_type == 'windows':
        # Windows에서는 수동 설치 안내
        click.echo("Please install git-crypt manually on Windows:")
        click.echo("1. Download from: https://github.com/AGWA/git-crypt/releases")
        click.echo("2. Extract and add to PATH")
        return False, "Manual installation required on Windows"
    else:
        return False, "Unsupported operating system"
    
    return success, output

def check_or_create_venv():
    """가상환경 확인 및 생성"""
    # 가상환경이 활성화되어 있는지 확인
    virtual_env = os.environ.get('VIRTUAL_ENV')
    
    if virtual_env:
        click.echo(f"✓ Using virtual environment: {virtual_env}")
        return True, virtual_env
    
    # 프로젝트 루트 디렉토리
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    venv_path = os.path.join(project_root, '.venv')
    
    # .venv가 있는지 확인
    if os.path.exists(venv_path):
        click.echo(f"Found .venv at {venv_path}")
        click.echo("Please activate the virtual environment first:")
        
        os_type = get_os_type()
        if os_type in ['mac', 'linux']:
            click.echo(f"  source {venv_path}/bin/activate")
        elif os_type == 'windows':
            click.echo(f"  {venv_path}\\Scripts\\activate")
        
        return False, "Virtual environment not activated"
    
    # .venv가 없으면 생성
    click.echo("Creating virtual environment...")
    success, output = run_command(['uv', 'venv'])
    
    if success:
        click.echo("✓ Virtual environment created successfully")
        click.echo("Please activate the virtual environment and run init again:")
        
        os_type = get_os_type()
        if os_type in ['mac', 'linux']:
            click.echo(f"  source .venv/bin/activate")
            click.echo(f"  ussh init")
        elif os_type == 'windows':
            click.echo(f"  .venv\\Scripts\\activate")
            click.echo(f"  ussh init")
        
        return False, "Virtual environment created, please activate and run again"
    else:
        return False, f"Failed to create virtual environment: {output}"

def install_ussh_editable():
    """ussh를 editable 모드로 설치"""
    click.echo("Installing ussh in editable mode...")
    
    # 프로젝트 루트 디렉토리로 이동
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    
    # uv pip install -e . 실행
    success, output = run_command(['uv', 'pip', 'install', '-e', project_root])
    
    if success:
        click.echo("✓ ussh installed successfully in editable mode")
        return True, "Installed successfully"
    else:
        return False, output

def check_git_remote():
    """Git remote origin 확인"""
    success, output = run_command(['git', 'remote', 'get-url', 'origin'], check=False)
    if success and output.strip():
        return True, output.strip()
    return False, "No git remote origin found"

@click.command()
@click.option('--skip-install', is_flag=True, help='Skip package installation')
@click.option('--skip-git-crypt', is_flag=True, help='Skip git-crypt initialization')
@click.option('--skip-push', is_flag=True, help='Skip git push')
@click.option('--skip-ussh-install', is_flag=True, help='Skip ussh editable installation')
def init(skip_install, skip_git_crypt, skip_push, skip_ussh_install):
    """Initialize ussh environment with required dependencies and configurations."""
    
    os_type = get_os_type()
    if not os_type:
        click.echo("Error: Unsupported operating system")
        return
    
    click.echo(f"Detected OS: {os_type}")
    
    # 1. uv 및 git-crypt 설치
    if not skip_install:
        # uv 설치
        success, output = install_uv(os_type)
        if success:
            click.echo("✓ uv installed successfully")
        else:
            click.echo(f"✗ Failed to install uv: {output}")
            if not click.confirm("Continue anyway?"):
                return
        
        # git-crypt 설치
        success, output = install_git_crypt(os_type)
        if success:
            click.echo("✓ git-crypt installed successfully")
        else:
            click.echo(f"✗ Failed to install git-crypt: {output}")
            if os_type != 'windows' and not click.confirm("Continue anyway?"):
                return
    
    # 2. git-crypt 초기화
    if not skip_git_crypt:
        click.echo("Initializing git-crypt...")
        success, output = run_command(['git-crypt', 'init'], check=False)
        if success or "already initialized" in output:
            click.echo("✓ git-crypt initialized successfully")
        else:
            click.echo(f"✗ Failed to initialize git-crypt: {output}")
            if not click.confirm("Continue anyway?"):
                return
    
    # 3. git push
    if not skip_push:
        has_remote, remote_url = check_git_remote()
        if has_remote:
            click.echo(f"Git remote origin: {remote_url}")
            if click.confirm("Push to remote origin?"):
                # 먼저 현재 변경사항 커밋
                run_command(['git', 'add', '.gitattributes'], check=False)
                run_command(['git', 'commit', '-m', 'Add git-crypt configuration'], check=False)
                
                # push
                success, output = run_command(['git', 'push', 'origin', 'HEAD'], check=False)
                if success:
                    click.echo("✓ Pushed to remote successfully")
                else:
                    click.echo(f"✗ Failed to push: {output}")
        else:
            click.echo("No git remote origin found. Skipping push.")
    
    # 4. 가상환경 확인 및 ussh 설치 (editable mode)
    if not skip_ussh_install:
        # 가상환경 확인
        venv_active, venv_info = check_or_create_venv()
        
        if not venv_active:
            click.echo(f"\n{venv_info}")
            return
        
        # ussh 설치
        success, output = install_ussh_editable()
        if success:
            click.echo("\n✅ ussh is now available as a command!")
            click.echo("You can now use: ussh --help")
        else:
            click.echo(f"✗ Failed to install ussh: {output}")
            if not click.confirm("Continue anyway?"):
                return
    
    click.echo("\n✅ Initialization completed!")