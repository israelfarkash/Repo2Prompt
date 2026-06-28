import asyncio
import os
import shutil
import urllib.parse
from typing import Dict, Optional
import uuid

from app.config import settings

class GitHubServiceError(Exception):
    pass

async def validate_github_url(url: str) -> bool:
    """Validate that the URL is a legitimate GitHub repository URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc not in ("github.com", "www.github.com"):
            return False
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) < 2:
            return False
        return True
    except Exception:
        return False

async def extract_repo_info(url: str) -> Dict[str, str]:
    """Extract owner and repository name from a GitHub URL."""
    parsed = urllib.parse.urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    owner = parts[0]
    repo_name = parts[1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return {"owner": owner, "name": repo_name}

async def clone_repository(url: str, project_id: uuid.UUID) -> str:
    """Clone the repository to a local directory."""
    if not await validate_github_url(url):
        raise GitHubServiceError("Invalid GitHub repository URL")

    # Create safe clone directory
    os.makedirs(settings.CLONE_DIR, exist_ok=True)
    target_dir = os.path.join(settings.CLONE_DIR, str(project_id))
    
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    # For private repos, we would inject the GITHUB_TOKEN here.
    # For MVP, assuming public repos.
    clone_url = url
    if settings.GITHUB_TOKEN:
        parsed = urllib.parse.urlparse(url)
        clone_url = f"https://oauth2:{settings.GITHUB_TOKEN}@{parsed.netloc}{parsed.path}"

    process = await asyncio.create_subprocess_exec(
        "git", "clone", "--depth", "1", clone_url, target_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        err_msg = stderr.decode().strip()
        # Clean token from error message for security
        if settings.GITHUB_TOKEN:
            err_msg = err_msg.replace(settings.GITHUB_TOKEN, "***")
        raise GitHubServiceError(f"Failed to clone repository: {err_msg}")
    
    # Check repository size
    size_mb = get_dir_size_mb(target_dir)
    if size_mb > settings.MAX_REPO_SIZE_MB:
        await cleanup_repository(target_dir)
        raise GitHubServiceError(f"Repository exceeds maximum size limit of {settings.MAX_REPO_SIZE_MB}MB")

    return target_dir

def get_dir_size_mb(path: str) -> float:
    """Calculate the total size of a directory in megabytes."""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

async def cleanup_repository(path: str) -> None:
    """Remove the cloned repository directory."""
    if os.path.exists(path) and path.startswith(settings.CLONE_DIR):
        shutil.rmtree(path, ignore_errors=True)
