
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

def setup_alias(os_type):
    """OS별 ussh alias 설정"""
    click.echo("Setting up ussh alias...")
    
    # 현재 파일의 절대 경로 찾기
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    main_py_path = os.path.join(project_root, 'src', 'main.py')
    
    alias_command = f'alias ussh="uvx --from {project_root} ussh"'
    
    if os_type in ['mac', 'linux']:
        # 사용 중인 쉘 확인
        shell = os.environ.get('SHELL', '/bin/bash')
        
        if 'zsh' in shell:
            rc_file = os.path.expanduser('~/.zshrc')
        elif 'bash' in shell:
            rc_file = os.path.expanduser('~/.bashrc')
        else:
            rc_file = os.path.expanduser('~/.profile')
        
        # alias가 이미 존재하는지 확인
        if os.path.exists(rc_file):
            with open(rc_file, 'r') as f:
                content = f.read()
                if 'alias ussh=' in content:
                    click.echo(f"ussh alias already exists in {rc_file}")
                    return True, "Alias already exists"
        
        # alias 추가
        with open(rc_file, 'a') as f:
            f.write(f'\n# ussh alias\n{alias_command}\n')
        
        click.echo(f"Added ussh alias to {rc_file}")
        click.echo("Please run 'source " + rc_file + "' or restart your terminal to use the alias.")
        return True, "Alias added successfully"
    
    elif os_type == 'windows':
        # Windows PowerShell 프로필에 함수 추가
        profile_path = os.path.expanduser('~/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1')
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        
        function_content = f'''
# ussh function
function ussh {{
    uvx --from {project_root} ussh $args
}}
'''
        
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                content = f.read()
                if 'function ussh' in content:
                    click.echo(f"ussh function already exists in {profile_path}")
                    return True, "Function already exists"
        
        with open(profile_path, 'a') as f:
            f.write(function_content)
        
        click.echo(f"Added ussh function to {profile_path}")
        click.echo("Please restart PowerShell to use the ussh command.")
        return True, "Function added successfully"
    
    return False, "Unsupported operating system"

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
@click.option('--skip-alias', is_flag=True, help='Skip alias setup')
def init(skip_install, skip_git_crypt, skip_push, skip_alias):
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
    
    # 4. ussh alias 설정
    if not skip_alias:
        success, output = setup_alias(os_type)
        if success:
            click.echo("✓ ussh alias configured successfully")
            
            # macOS/Linux에서 실행 가능한 ussh 스크립트 생성
            if os_type in ['mac', 'linux']:
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                # /usr/local/bin에 ussh 실행 파일 생성 (sudo 권한 필요)
                ussh_script_content = f'''#!/bin/sh
# ussh launcher script
exec uvx --from {project_root} ussh "$@"
'''
                
                # 먼저 ~/.local/bin에 시도 (사용자 권한으로 가능)
                local_bin = os.path.expanduser('~/.local/bin')
                os.makedirs(local_bin, exist_ok=True)
                local_ussh_path = os.path.join(local_bin, 'ussh')
                
                try:
                    with open(local_ussh_path, 'w') as f:
                        f.write(ussh_script_content)
                    os.chmod(local_ussh_path, 0o755)
                    
                    # PATH에 ~/.local/bin이 있는지 확인
                    path_env = os.environ.get('PATH', '')
                    if local_bin not in path_env:
                        shell = os.environ.get('SHELL', '/bin/bash')
                        if 'zsh' in shell:
                            rc_file = os.path.expanduser('~/.zshrc')
                        elif 'bash' in shell:
                            rc_file = os.path.expanduser('~/.bashrc')
                        else:
                            rc_file = os.path.expanduser('~/.profile')
                        
                        # PATH에 추가
                        with open(rc_file, 'r') as f:
                            content = f.read()
                        
                        if f'export PATH="$HOME/.local/bin:$PATH"' not in content:
                            with open(rc_file, 'a') as f:
                                f.write(f'\n# Add ~/.local/bin to PATH\nexport PATH="$HOME/.local/bin:$PATH"\n')
                            
                            click.echo(f"✓ Added ~/.local/bin to PATH in {rc_file}")
                            click.echo(f"\n✅ ussh is now installed!")
                            click.echo(f"\nTo use ussh immediately, run:")
                            click.echo(f"  export PATH=\"$HOME/.local/bin:$PATH\"")
                            click.echo(f"  ussh --help")
                        else:
                            click.echo(f"\n✅ ussh is now available as a command!")
                            click.echo(f"You can now use: ussh --help")
                    else:
                        click.echo(f"\n✅ ussh is now available as a command!")
                        click.echo(f"You can now use: ussh --help")
                    
                except Exception as e:
                    click.echo(f"Failed to create ussh script: {e}")
                    click.echo(f"\nYou can still use: uvx --from {project_root} ussh")
                
            elif os_type == 'windows':
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                # Windows에서는 .cmd 파일 생성
                local_bin = os.path.expanduser('~/AppData/Local/Microsoft/WindowsApps')
                os.makedirs(local_bin, exist_ok=True)
                
                ussh_cmd_path = os.path.join(local_bin, 'ussh.cmd')
                ussh_cmd_content = f'''@echo off
uvx --from "{project_root}" ussh %*
'''
                
                try:
                    with open(ussh_cmd_path, 'w') as f:
                        f.write(ussh_cmd_content)
                    
                    click.echo(f"\n✅ ussh.cmd created in {local_bin}")
                    click.echo("\nussh is now available as a command!")
                    click.echo("You can now use: ussh --help")
                    
                except Exception as e:
                    click.echo(f"Failed to create ussh.cmd: {e}")
                    click.echo("\n✅ ussh function is available after restarting PowerShell.")
        else:
            click.echo(f"✗ Failed to setup alias: {output}")
    
    click.echo("\n✅ Initialization completed!")