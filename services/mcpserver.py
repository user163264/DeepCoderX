# services/mcpserver.py

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
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

        def validate_path(self, file_path):
            path = (sandbox_path / file_path).resolve()
            if not path.is_relative_to(sandbox_path):
                raise SecurityError("Path traversal attempt")
            if path.suffix and path.suffix not in ALLOWED_EXTENSIONS:
                raise SecurityError("Unsupported file type")
            return path

        def send_tools_list(self):
            tools = {
                "tools": [
                    {"name": "read", "endpoint": "/read", "method": "GET"},
                    {"name": "write", "endpoint": "/write", "method": "POST"},
                    {"name": "delete", "endpoint": "/delete", "method": "POST"},
                    {"name": "list", "endpoint": "/list", "method": "POST"}
                ]
            }
            self.send_json(tools)

        def send_json(self, data):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

        def send_error(self, code, message):
            self.send_response(code)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error {code}: {message}".encode())

    return MCPRequestHandler

def start_mcp_server(host="localhost", port=8080, sandbox_path=None):
    handler = create_mcp_request_handler(Path(sandbox_path))
    server_address = (host, port)
    httpd = HTTPServer(server_address, handler)
    logger.info(f"MCP Server running on {host}:{port}")
    logger.info(f"Sandbox directory: {sandbox_path}")
    httpd.serve_forever()