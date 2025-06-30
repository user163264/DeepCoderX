# services/mcpclient.py
import sys
import os
import requests

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
                timeout=10
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
                timeout=10
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
                timeout=10
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
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("error", f"HTTP {response.status_code}")}
        except Exception as e:
            return {"error": f"MCP request failed: {str(e)}"}