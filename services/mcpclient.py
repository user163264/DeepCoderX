# services/mcpclient.py
import sys
import os
import requests
from config import config

class MCPClient:
    def __init__(self, endpoint, api_key):
        self.endpoint = endpoint
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
    
    def read_file(self, path):
        try:
            response = requests.get(
                f"{self.endpoint}/read?file={path}",
                headers=self.headers,
                timeout=config.MCP_CLIENT_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("error", f"HTTP {response.status_code}")}
        except Exception as e:
            return {"error": f"MCP request failed: {str(e)}"}
    
    def write_file(self, path, content):
        try:
            payload = {"file": path, "content": content}
            response = requests.post(
                f"{self.endpoint}/write",
                headers=self.headers,
                json=payload,
                timeout=config.MCP_CLIENT_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("error", f"HTTP {response.status_code}")}
        except Exception as e:
            return {"error": f"MCP request failed: {str(e)}"}
    
    def list_dir(self, path):
        try:
            payload = {"path": path}
            response = requests.post(
                f"{self.endpoint}/list",
                headers=self.headers,
                json=payload,
                timeout=config.MCP_CLIENT_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("error", f"HTTP {response.status_code}")}
        except Exception as e:
            return {"error": f"MCP request failed: {str(e)}"}
    
    def delete_path(self, path, recursive=False):
        try:
            payload = {"path": path, "recursive": recursive}
            response = requests.post(
                f"{self.endpoint}/delete",
                headers=self.headers,
                json=payload,
                timeout=config.MCP_CLIENT_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("error", f"HTTP {response.status_code}")}
        except Exception as e:
            return {"error": f"MCP request failed: {str(e)}"}
    
    # ENHANCED MCP CLIENT - OpenAPI 3.1 MCP File System Compliance
    
    def move_file(self, source, destination, overwrite=False):
        """Move or rename a file or directory to a new location."""
        try:
            payload = {
                "source": source,
                "destination": destination,
                "overwrite": overwrite
            }
            response = requests.post(
                f"{self.endpoint}/fs/move",
                headers=self.headers,
                json=payload,
                timeout=config.MCP_CLIENT_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.content else {}
                return {"error": error_data.get("error", f"HTTP {response.status_code}")}
        except Exception as e:
            return {"error": f"MCP move request failed: {str(e)}"}
    
    def mkdir(self, path, parents=True, exist_ok=True):
        """Create a new directory, optionally creating parent directories."""
        try:
            payload = {
                "path": path,
                "parents": parents,
                "exist_ok": exist_ok
            }
            response = requests.post(
                f"{self.endpoint}/fs/mkdir",
                headers=self.headers,
                json=payload,
                timeout=config.MCP_CLIENT_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.content else {}
                return {"error": error_data.get("error", f"HTTP {response.status_code}")}
        except Exception as e:
            return {"error": f"MCP mkdir request failed: {str(e)}"}
    
    def stat(self, path):
        """Get detailed metadata information about a file or directory."""
        try:
            payload = {"path": path}
            response = requests.post(
                f"{self.endpoint}/fs/stat",
                headers=self.headers,
                json=payload,
                timeout=config.MCP_CLIENT_TIMEOUT
            )
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.content else {}
                return {"error": error_data.get("error", f"HTTP {response.status_code}")}
        except Exception as e:
            return {"error": f"MCP stat request failed: {str(e)}"}