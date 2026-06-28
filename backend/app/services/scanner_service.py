import os
import json
from typing import Dict, List, Any

IGNORED_DIRS = {
    'node_modules', '.git', 'build', 'dist', '.gradle', 
    '__pycache__', '.next', 'venv', '.venv', 'vendor', 
    'target', '.idea', '.vscode', 'coverage', '.nyc_output'
}

IGNORED_FILES = {
    '.DS_Store', 'Thumbs.db', 'package-lock.json', 'yarn.lock', 
    'pnpm-lock.yaml', 'poetry.lock'
}

IGNORED_EXTENSIONS = {
    '.pyc', '.pyo', '.class', '.png', '.jpg', '.jpeg', '.gif', 
    '.ico', '.svg', '.mp4', '.mp3', '.wav', '.pdf', '.zip', '.tar', '.gz'
}

def categorize_file(filename: str, ext: str) -> str:
    """Categorize file based on name and extension."""
    if ext in ('.py', '.js', '.ts', '.java', '.kt', '.go', '.rs', '.cpp', '.c', '.cs', '.rb', '.php'):
        if 'test' in filename.lower() or 'spec' in filename.lower():
            return 'test'
        return 'source'
    if ext in ('.html', '.jsx', '.tsx', '.vue', '.svelte', '.css', '.scss'):
        return 'frontend'
    if ext in ('.json', '.yaml', '.yml', '.toml', '.xml', '.ini', '.env', '.gradle'):
        return 'config'
    if ext in ('.md', '.txt', '.rst'):
        return 'doc'
    if ext in ('.sql', '.prisma'):
        return 'database'
    return 'other'

async def scan_project(repo_path: str) -> Dict[str, Any]:
    """Scan the repository and return structure, file list, and detected tech."""
    file_tree = {}
    files_list = []
    total_size = 0
    
    for root, dirs, files in os.walk(repo_path):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith('.')]
        
        rel_path = os.path.relpath(root, repo_path)
        if rel_path == '.':
            current_level = file_tree
        else:
            parts = rel_path.split(os.sep)
            current_level = file_tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
                
        for file in files:
            if file in IGNORED_FILES or file.startswith('.'):
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext in IGNORED_EXTENSIONS:
                continue
                
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, repo_path)
            
            try:
                size = os.path.getsize(file_path)
                total_size += size
                category = categorize_file(file, ext)
                
                current_level[file] = {"type": "file", "size": size, "category": category}
                
                files_list.append({
                    "path": rel_file_path,
                    "name": file,
                    "extension": ext,
                    "size": size,
                    "category": category
                })
            except Exception:
                pass # skip unreadable files
                
    technologies = await detect_technologies(repo_path, files_list)
                
    return {
        "file_tree": file_tree,
        "files": files_list,
        "technologies": technologies,
        "total_files": len(files_list),
        "total_size": total_size
    }

async def detect_technologies(repo_path: str, files_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect technologies used in the project by scanning configuration files."""
    tech = {
        "languages": [],
        "frameworks": [],
        "database": [],
        "tools": []
    }
    
    file_names = {f["name"] for f in files_list}
    extensions = {f["extension"] for f in files_list}
    
    # Simple heuristic tech detection
    if '.py' in extensions: tech["languages"].append("Python")
    if '.js' in extensions: tech["languages"].append("JavaScript")
    if '.ts' in extensions: tech["languages"].append("TypeScript")
    if '.java' in extensions: tech["languages"].append("Java")
    if '.kt' in extensions: tech["languages"].append("Kotlin")
    if '.go' in extensions: tech["languages"].append("Go")
    
    # JS Ecosystem
    if 'package.json' in file_names:
        try:
            with open(os.path.join(repo_path, 'package.json'), 'r') as f:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                if "next" in deps: tech["frameworks"].append("Next.js")
                if "react" in deps: tech["frameworks"].append("React")
                if "vue" in deps: tech["frameworks"].append("Vue")
                if "express" in deps: tech["frameworks"].append("Express")
                if "nest" in deps or "@nestjs/core" in deps: tech["frameworks"].append("NestJS")
                if "prisma" in deps: tech["database"].append("Prisma ORM")
                if "pg" in deps: tech["database"].append("PostgreSQL")
        except Exception:
            pass
            
    # Python Ecosystem
    if 'requirements.txt' in file_names:
        try:
            with open(os.path.join(repo_path, 'requirements.txt'), 'r') as f:
                content = f.read().lower()
                if 'fastapi' in content: tech["frameworks"].append("FastAPI")
                if 'django' in content: tech["frameworks"].append("Django")
                if 'flask' in content: tech["frameworks"].append("Flask")
                if 'sqlalchemy' in content: tech["database"].append("SQLAlchemy")
                if 'psycopg2' in content or 'asyncpg' in content: tech["database"].append("PostgreSQL")
        except Exception:
            pass
            
    return tech

async def read_file_safe(repo_path: str, file_path: str, max_size_bytes: int = 50000) -> str:
    """Read a file safely, truncating if it's too large."""
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return ""
        
    size = os.path.getsize(full_path)
    if size > max_size_bytes:
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read(max_size_bytes) + "\n\n... [FILE TRUNCATED DUE TO SIZE] ..."
        except Exception:
            return "[UNREADABLE FILE]"
            
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "[UNREADABLE BINARY OR INVALID ENCODING FILE]"
