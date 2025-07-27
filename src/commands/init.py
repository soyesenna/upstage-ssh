import click
import platform
import subprocess
import os

def run_command(cmd, shell=False, check=True):
    """명령어 실행 및 결과 반환"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=check)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except Exception as e:
        return False, str(e)

def check_git_remote():
    """Git remote origin 확인"""
    success, output = run_command(['git', 'remote', 'get-url', 'origin'], check=False)
    if success and output.strip():
        return True, output.strip()
    return False, "No git remote origin found"

@click.command()
@click.option('--skip-git-crypt', is_flag=True, help='Skip git-crypt initialization')
@click.option('--skip-push', is_flag=True, help='Skip git push')
def init(skip_git_crypt, skip_push):
    """Initialize git-crypt and push to remote."""
    
    # 1. git-crypt 초기화
    if not skip_git_crypt:
        click.echo("Initializing git-crypt...")
        success, output = run_command(['git-crypt', 'init'], check=False)
        if success or "already initialized" in output:
            click.echo("✓ git-crypt initialized successfully")
        else:
            click.echo(f"✗ Failed to initialize git-crypt: {output}")
            if not click.confirm("Continue anyway?"):
                return
    
    # 2. git push
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
    
    click.echo("\n✅ Initialization completed!")
    click.echo("\nNote: Make sure you have run the setup script first:")
    click.echo("  - macOS/Linux: ./setup.sh")
    click.echo("  - Windows: .\\setup-windows.ps1")