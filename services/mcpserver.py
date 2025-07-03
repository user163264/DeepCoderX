# services/mcpserver.py

import json
import os
import sys
import shutil
import stat
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from config import SANDBOX_PATH, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, MCP_API_KEY
from utils.logging import logger
from utils.security import SecurityError  # Import custom exception

def create_mcp_request_handler(sandbox_path):
    class MCPRequestHandler(BaseHTTPRequestHandler):
        def _validate_api_key(self):
            """Check API key in headers"""
            api_key = self.headers.get("X-API-Key")
            if api_key != MCP_API_KEY:
                raise SecurityError("Invalid API key")
        
        def do_GET(self):
            try:
                self._validate_api_key()
                parsed = urlparse(self.path)
                if parsed.path == "/discover-tools":
                    self.send_tools_list()
                elif parsed.path == "/read":
                    params = parse_qs(parsed.query)
                    self.handle_read(params.get('file', [''])[0])
                elif parsed.path == "/fs/stat":
                    params = parse_qs(parsed.query)
                    self.handle_stat(params.get('path', [''])[0])
                else:
                    self.send_error(404, "Endpoint not found")
            except SecurityError as e:
                self.send_error(401, str(e))
            except Exception as e:
                self.send_error(500, str(e))

        def do_POST(self):
            try:
                self._validate_api_key()
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                if self.path == "/write":
                    self.handle_write(data)
                elif self.path == "/delete":
                    self.handle_delete(data)
                elif self.path == "/list":
                    self.handle_list(data)
                elif self.path == "/fs/move":
                    self.handle_move(data)
                elif self.path == "/fs/mkdir":
                    self.handle_mkdir(data)
                elif self.path == "/fs/stat":
                    self.handle_stat_post(data)
                else:
                    self.send_error(404, "Endpoint not found")
            except SecurityError as e:
                self.send_error(401, str(e))
            except Exception as e:
                self.send_error(500, str(e))

        def handle_read(self, file_path):
            try:
                safe_path = self.validate_path(file_path)
                if safe_path.stat().st_size > MAX_FILE_SIZE:
                    return self.send_error(413, "File too large")
                
                with open(safe_path, 'r') as f:
                    content = f.read()
                self.send_json({"status": "success", "content": content})
            except FileNotFoundError:
                logger.warning(f"DEBUG WARNING: File not found at path: {file_path}")
                self.send_error(404, "File not found")

        def handle_write(self, data):
            safe_path = self.validate_path(data['file'])
            # Ensure directory exists
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(safe_path, 'w') as f:
                f.write(data['content'])
            self.send_json({"status": "success"})

        def handle_delete(self, data):
            safe_path = self.validate_path(data['path'])
            recursive = data.get('recursive', False)
            
            if safe_path.is_dir():
                if recursive:
                    shutil.rmtree(safe_path)
                else:
                    safe_path.rmdir()
            else:
                safe_path.unlink()
                
            self.send_json({"status": "success"})

        def handle_list(self, data):
            safe_path = self.validate_path(data.get('path', '.'))
            if not safe_path.is_dir():
                raise ValueError("Path is not a directory")
                
            items = {
                "files": [],
                "directories": []
            }
            
            for entry in safe_path.iterdir():
                if entry.is_file():
                    items["files"].append(entry.name)
                elif entry.is_dir():
                    items["directories"].append(entry.name)
                    
            self.send_json({"status": "success", "result": items})

        def handle_move(self, data):
            """Handle file/directory move/rename operations"""
            try:
                source_path = self.validate_path(data['source'])
                destination_path = self.validate_path(data['destination'])
                
                if not source_path.exists():
                    raise FileNotFoundError(f"Source path does not exist: {data['source']}")
                
                # Ensure destination directory exists
                destination_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if destination already exists
                if destination_path.exists():
                    overwrite = data.get('overwrite', False)
                    if not overwrite:
                        raise FileExistsError(f"Destination already exists: {data['destination']}")
                    # If overwriting, remove destination first
                    if destination_path.is_dir():
                        shutil.rmtree(destination_path)
                    else:
                        destination_path.unlink()
                
                # Perform the move
                shutil.move(str(source_path), str(destination_path))
                
                self.send_json({
                    "status": "success", 
                    "message": f"Successfully moved {data['source']} to {data['destination']}"
                })
                
            except FileNotFoundError as e:
                self.send_error(404, str(e))
            except FileExistsError as e:
                self.send_error(409, str(e))
            except Exception as e:
                self.send_error(500, f"Move operation failed: {str(e)}")

        def handle_mkdir(self, data):
            """Handle directory creation operations"""
            try:
                dir_path = self.validate_path(data['path'])
                parents = data.get('parents', True)  # Default to True for convenience
                exist_ok = data.get('exist_ok', True)  # Default to True to avoid errors
                
                if dir_path.exists() and not exist_ok:
                    raise FileExistsError(f"Directory already exists: {data['path']}")
                
                # Create directory
                dir_path.mkdir(parents=parents, exist_ok=exist_ok)
                
                self.send_json({
                    "status": "success",
                    "message": f"Successfully created directory: {data['path']}"
                })
                
            except FileExistsError as e:
                self.send_error(409, str(e))
            except Exception as e:
                self.send_error(500, f"Directory creation failed: {str(e)}")

        def handle_stat(self, file_path):
            """Handle file/directory metadata requests via GET"""
            try:
                safe_path = self.validate_path(file_path)
                if not safe_path.exists():
                    raise FileNotFoundError(f"Path does not exist: {file_path}")
                
                stat_info = self._get_stat_info(safe_path)
                self.send_json({"status": "success", "result": stat_info})
                
            except FileNotFoundError as e:
                self.send_error(404, str(e))
            except Exception as e:
                self.send_error(500, f"Stat operation failed: {str(e)}")

        def handle_stat_post(self, data):
            """Handle file/directory metadata requests via POST"""
            try:
                safe_path = self.validate_path(data['path'])
                if not safe_path.exists():
                    raise FileNotFoundError(f"Path does not exist: {data['path']}")
                
                stat_info = self._get_stat_info(safe_path)
                self.send_json({"status": "success", "result": stat_info})
                
            except FileNotFoundError as e:
                self.send_error(404, str(e))
            except Exception as e:
                self.send_error(500, f"Stat operation failed: {str(e)}")

        def _get_stat_info(self, path: Path) -> dict:
            """Get comprehensive file/directory metadata"""
            path_stat = path.stat()
            
            # Get file type
            if path.is_file():
                file_type = "file"
            elif path.is_dir():
                file_type = "directory"
            elif path.is_symlink():
                file_type = "symlink"
            else:
                file_type = "other"
            
            # Get permissions in human-readable format
            permissions = stat.filemode(path_stat.st_mode)
            
            # Get timestamps
            created_time = datetime.fromtimestamp(path_stat.st_ctime).isoformat()
            modified_time = datetime.fromtimestamp(path_stat.st_mtime).isoformat()
            accessed_time = datetime.fromtimestamp(path_stat.st_atime).isoformat()
            
            stat_info = {
                "name": path.name,
                "path": str(path.relative_to(Path(SANDBOX_PATH))),
                "type": file_type,
                "size": path_stat.st_size,
                "permissions": permissions,
                "permissions_octal": oct(path_stat.st_mode)[-3:],
                "owner_uid": path_stat.st_uid,
                "group_gid": path_stat.st_gid,
                "created_time": created_time,
                "modified_time": modified_time,
                "accessed_time": accessed_time,
                "is_readable": os.access(path, os.R_OK),
                "is_writable": os.access(path, os.W_OK),
                "is_executable": os.access(path, os.X_OK)
            }
            
            # Add additional info for files
            if file_type == "file":
                stat_info["extension"] = path.suffix
                stat_info["stem"] = path.stem
            
            # Add additional info for directories
            elif file_type == "directory":
                try:
                    # Count items in directory (safely)
                    items = list(path.iterdir())
                    stat_info["item_count"] = len(items)
                    stat_info["file_count"] = len([item for item in items if item.is_file()])
                    stat_info["dir_count"] = len([item for item in items if item.is_dir()])
                except PermissionError:
                    stat_info["item_count"] = "Permission denied"
                    stat_info["file_count"] = "Permission denied"
                    stat_info["dir_count"] = "Permission denied"
            
            return stat_info

        def validate_path(self, file_path):
            """Enhanced path validation with better error messages"""
            if not file_path:
                raise ValueError("Path cannot be empty")
            
            path = (sandbox_path / file_path).resolve()
            if not path.is_relative_to(sandbox_path):
                raise SecurityError(f"Path traversal attempt: {file_path} resolves outside sandbox")
            
            # For move operations, don't validate file extension on destination
            # For stat operations, allow any file type
            if self.path not in ["/fs/move", "/fs/stat"] and path.suffix and path.suffix not in ALLOWED_EXTENSIONS:
                raise SecurityError(f"Unsupported file type: {path.suffix}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
            
            return path

        def send_tools_list(self):
            """Return comprehensive list of available tools including new endpoints"""
            tools = {
                "tools": [
                    # Legacy endpoints
                    {"name": "read", "endpoint": "/read", "method": "GET", "description": "Read file content"},
                    {"name": "write", "endpoint": "/write", "method": "POST", "description": "Write file content"},
                    {"name": "delete", "endpoint": "/delete", "method": "POST", "description": "Delete file or directory"},
                    {"name": "list", "endpoint": "/list", "method": "POST", "description": "List directory contents"},
                    
                    # New OpenAPI 3.1 endpoints
                    {"name": "move", "endpoint": "/fs/move", "method": "POST", "description": "Move or rename files/directories"},
                    {"name": "mkdir", "endpoint": "/fs/mkdir", "method": "POST", "description": "Create directories"},
                    {"name": "stat", "endpoint": "/fs/stat", "method": "GET/POST", "description": "Get file/directory metadata"}
                ],
                "version": "1.1.0",
                "specification": "OpenAPI 3.1 MCP File System",
                "sandbox_path": str(sandbox_path),
                "capabilities": [
                    "file_operations",
                    "directory_operations", 
                    "metadata_retrieval",
                    "move_rename_operations",
                    "secure_sandboxing"
                ]
            }
            self.send_json(tools)

        def send_json(self, data):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())

        def send_error(self, code, message):
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                "status": "error",
                "code": code,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response, indent=2).encode())

        def do_OPTIONS(self):
            """Handle CORS preflight requests"""
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
            self.end_headers()

        def log_message(self, format, *args):
            """Override to use our logger instead of stderr"""
            logger.info(f"MCP Server: {format % args}")

    return MCPRequestHandler

def start_mcp_server(host="localhost", port=8080, sandbox_path=None):
    """Start the enhanced MCP server with full OpenAPI 3.1 file system support"""
    handler = create_mcp_request_handler(Path(sandbox_path))
    server_address = (host, port)
    httpd = HTTPServer(server_address, handler)
    logger.info(f"Enhanced MCP Server v1.1.0 running on {host}:{port}")
    logger.info(f"Sandbox directory: {sandbox_path}")
    logger.info(f"Available endpoints: /read, /write, /delete, /list, /fs/move, /fs/mkdir, /fs/stat")
    logger.info(f"OpenAPI 3.1 MCP File System specification implemented")
    httpd.serve_forever()
