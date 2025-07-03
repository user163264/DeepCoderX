from services.llm_handler import LocalCodingHandler
from models.session import CommandContext
from services.mcpclient import MCPClient

# Initialize MCP client with correct parameters (positional arguments)
mcp_client = MCPClient("localhost", 8080)
mcp_client.api_key = "secure_mcp_key_123"

# Initialize context
ctx = CommandContext(
    root_path="/Users/admin/Documents/DeepCoderX",
    mcp_client=mcp_client,
    sandbox_path="/Users/admin/Documents"
)

# Test model loading
h = LocalCodingHandler(ctx)
print("Success!" if h.llm else "Failed")