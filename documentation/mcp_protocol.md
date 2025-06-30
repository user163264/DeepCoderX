
### Protocol Message Examples

Request Fields:
- tool: Operation type (read_file/write_file/list_dir/run_bash)
- path: Target file/directory path
- request_id: Unique identifier

Response Fields:
- status: Operation result (success/error)
- content: Response data or error message
- request_id: Echo of request identifier

Example Structure:
# Request
TOOL: read_file
PATH: app.py
REQUEST_ID: uuid4

# Response
STATUS: success
CONTENT: <file contents>
REQUEST_ID: uuid4