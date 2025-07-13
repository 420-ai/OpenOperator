import os
import requests
import shutil
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional

def download_file(url: str, local_path: str, timeout: int = 30) -> Dict[str, Any]:
    """Download files from remote servers to specified local paths."""
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(local_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        file_size = local_path.stat().st_size
        
        return {
            "success": True,
            "url": url,
            "local_path": str(local_path),
            "file_size_bytes": file_size,
            "content_type": response.headers.get('content-type', 'unknown')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_files(directory_path: str, pattern: str = "*", include_hidden: bool = False) -> Dict[str, Any]:
    """Get directory contents and file listings from specified paths."""
    try:
        path = Path(directory_path)
        
        if not path.exists():
            return {"success": False, "error": f"Directory does not exist: {directory_path}"}
        
        if not path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {directory_path}"}
        
        files = []
        directories = []
        
        search_pattern = pattern if include_hidden else pattern
        
        for item in path.glob(search_pattern):
            if not include_hidden and item.name.startswith('.'):
                continue
                
            item_info = {
                "name": item.name,
                "path": str(item),
                "size": item.stat().st_size if item.is_file() else None,
                "modified": item.stat().st_mtime,
                "is_file": item.is_file(),
                "is_directory": item.is_dir()
            }
            
            if item.is_file():
                files.append(item_info)
            elif item.is_dir():
                directories.append(item_info)
        
        return {
            "success": True,
            "directory": str(path),
            "pattern": pattern,
            "files": files,
            "directories": directories,
            "total_files": len(files),
            "total_directories": len(directories)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_files(directory_path: str, filename_pattern: str, recursive: bool = True, max_results: int = 100) -> Dict[str, Any]:
    """Search for files by name/pattern within directory trees."""
    try:
        path = Path(directory_path)
        
        if not path.exists():
            return {"success": False, "error": f"Directory does not exist: {directory_path}"}
        
        if not path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {directory_path}"}
        
        found_files = []
        search_pattern = f"**/{filename_pattern}" if recursive else filename_pattern
        
        for item in path.glob(search_pattern):
            if item.is_file():
                found_files.append({
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime,
                    "directory": str(item.parent)
                })
                
                if len(found_files) >= max_results:
                    break
        
        return {
            "success": True,
            "search_directory": str(path),
            "pattern": filename_pattern,
            "recursive": recursive,
            "found_files": found_files,
            "count": len(found_files),
            "max_results_reached": len(found_files) >= max_results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_directory(directory_path: str) -> Dict[str, Any]:
    """Create a new directory."""
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "directory": str(path),
            "exists": path.exists(),
            "is_directory": path.is_dir()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_file(file_path: str) -> Dict[str, Any]:
    """Delete a file or directory."""
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {"success": False, "error": f"Path does not exist: {file_path}"}
        
        if path.is_file():
            path.unlink()
            action = "file_deleted"
        elif path.is_dir():
            shutil.rmtree(path)
            action = "directory_deleted"
        else:
            return {"success": False, "error": f"Unknown path type: {file_path}"}
        
        return {
            "success": True,
            "path": str(path),
            "action": action
        }
    except Exception as e:
        return {"success": False, "error": str(e)}