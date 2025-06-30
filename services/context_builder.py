import sys
import os

from pathlib import Path
import re
from typing import List, Dict

class CodeContextBuilder:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.file_priority = {
            '.py': 10, '.ts': 9, '.js': 8, '.go': 7, '.rs': 7, 
            '.java': 7, '.json': 4, '.yml': 4, '.yaml': 4, '.md': 2
        }
    
    def build_context(self) -> str:
        context = "# PROJECT CONTEXT\n\n"
        files = self._discover_files()
        context += f"## Files ({len(files)} key files)\n"
        graph = self._build_import_graph(files)
        context += "### Dependencies\n" + self._format_graph(graph) + "\n\n"
        context += "## Code Snippets\n"
        for file in files[:12]:
            context += self._get_snippet(file)
        return context
    
    def _discover_files(self) -> List[Path]:
        files = []
        for ext, priority in self.file_priority.items():
            for file in self.root_path.glob(f"**/*{ext}"):
                if any(p.startswith('.') or p in {'venv', 'node_modules'} for p in file.parts):
                    continue
                files.append((file, priority))
        return [f for f, _ in sorted(files, key=lambda x: (-x[1], x[0]))][:15]
    
    def _build_import_graph(self, files: List[Path]) -> Dict[str, List[str]]:
        graph = {}
        for file in files:
            if file.suffix not in {'.py', '.ts', '.js', '.go'}:
                continue
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                imports = self._extract_imports(content, file.suffix)
                graph[file.name] = imports
            except Exception:
                continue
        return graph
    
    def _extract_imports(self, content: str, ext: str) -> List[str]:
        if ext == '.py':
            return re.findall(r'^\s*(?:from|import)\s+(\w+)', content, re.M)
        elif ext in {'.ts', '.js'}:
            return re.findall(r'import\s+.*?[\'"]([^\'"]+)[\'"]', content)
        elif ext == '.go':
            return re.findall(r'import\s+"([^"]+)"', content)
        return []
    
    def _format_graph(self, graph: Dict[str, List[str]]) -> str:
        if not graph:
            return "No dependencies found"
        return "\n".join(f"- {f}: {', '.join(deps)}" for f, deps in graph.items())
    
    def _get_snippet(self, file: Path) -> str:
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            if file.suffix == '.py':
                snippets = re.findall(r'(class\s+\w+|def\s+\w+\().*?:', content)[:3]
                snippet = "\n".join(snippets)
            else:
                snippet = "\n".join(content.splitlines()[:8])
            return f"### {file.relative_to(self.root_path)}\n```{file.suffix[1:]}\n{snippet}\n```\n\n"
        except Exception:
            return ""