# models/router.py

import sys
import os
from typing import Any
from .session import CommandContext
class CommandHandler:
    def __init__(self, context: CommandContext):
        self.ctx = context
        
    def handle(self) -> None:
        raise NotImplementedError("Subclasses must implement handle()")
        
    def can_handle(self) -> bool:
        raise NotImplementedError("Subclasses must implement can_handle()")

class CommandProcessor:
    def __init__(self, context: CommandContext):
        self.ctx = context
        self.handlers = []
        self.middleware = []
        
    def add_middleware(self, middleware: CommandHandler):
        self.middleware.append(middleware)
        
    def add_handler(self, handler: CommandHandler):
        self.handlers.append(handler)
        
    def execute(self, user_input: str) -> str:
        self.ctx.user_input = user_input
        self.ctx.response = ""
        self.ctx.abort = False
        
        if self.ctx.debug_mode:
            from utils.logging import console
            console.print(f"\n[bold red]DEBUG:[/] Processing: {user_input}", style="dim")
        
        for mw in self.middleware:
            mw.handle()
            if self.ctx.abort:
                return self.ctx.abort_reason
                
        for handler in self.handlers:
            if handler.can_handle():
                handler.handle()
                return self.ctx.response
                
        return "No handler found for command"