# Taibai MCP Server

A Model Context Protocol (MCP) server for accessing Dedao (得到) learning platform content via `dedao-dl`.

## Features

- 🎓 Download course transcripts with individual lessons and hot comments
- 📚 Access your purchased Dedao courses library  
- 📝 Export content as Markdown, PDF, or MP3
- 🔗 Seamless Obsidian vault integration
- 🔄 Automatic version detection and update notifications

## Prerequisites

1. **dedao-dl** - The Go-based Dedao downloader
   ```bash
   go install github.com/yann0917/dedao-dl@latest
   ```

2. **Python 3.10+** with `uv` (recommended) or `pip`

## Installation

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/terry-li-hm/taibai.git
cd taibai

# Install dependencies
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

### Using pip

```bash
# Clone and install
git clone https://github.com/yourusername/taibai.git
cd taibai
pip install -e .
```

## Configuration

### 1. Set up environment variables

Create a `.env` file or export:

```bash
# Optional: Specify where to download content (defaults to current directory)
export DEDAO_DOWNLOAD_DIR="/path/to/your/obsidian/vault/Dedao/Courses"
```

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "taibai": {
      "command": "python",
      "args": ["/path/to/taibai/server.py"],
      "env": {
        "DEDAO_DOWNLOAD_DIR": "/path/to/your/obsidian/vault/Dedao/Courses"
      }
    }
  }
}
```

### 3. Authenticate with Dedao

First time setup - login via QR code:
```python
# In Claude, use the MCP tool:
dedao_login(qrcode=True)
```

## Usage

### Available MCP Tools

- `dedao_version` - Check dedao-dl version and update availability
- `dedao_login` - Authenticate with Dedao platform
- `dedao_list_courses` - List all purchased courses  
- `dedao_course_details` - Get course information
- `dedao_download_course` - Download course content
- `dedao_article_details` - Get article information
- `dedao_download_article` - Download articles

### Example Usage in Claude

```python
# Check dedao-dl version
dedao_version()

# List your courses
dedao_list_courses()

# Download a specific course as markdown
dedao_download_course(
    course_id="743",
    format="markdown"
)

# Get course details
dedao_course_details(course_id="743")
```

## Development

### Code Quality

```bash
# Format code
ruff format .

# Lint code  
ruff check .

# Run tests
pytest
```

### Project Structure

```
taibai/
├── server.py           # Main MCP server implementation
├── pyproject.toml      # Project configuration and dependencies
├── README.md           # Documentation
└── .env.example        # Environment variables template
```

## Output Format

Downloaded courses include:
- **Individual lesson files** - Each lesson as a separate markdown file
- **Hot comments** - Community insights and discussions
- **Clean filenames** - No timestamp prefixes
- **Obsidian-ready** - Markdown formatted for knowledge graphs

## Troubleshooting

### Authentication Issues
- Ensure `dedao-dl` is authenticated: `dedao-dl who`
- Re-login if needed: Use `dedao_login(qrcode=True)`

### Download Location
- Default: `~/.taibai/output/` then moved to vault
- Override with `DEDAO_DOWNLOAD_DIR` environment variable

### Missing dedao-dl
```bash
# Install dedao-dl first
go install github.com/yann0917/dedao-dl@latest

# Verify installation
dedao-dl --version
```

## License

MIT

## Contributing

Pull requests welcome! Please:
1. Use `ruff` for formatting
2. Add tests for new features
3. Update documentation

## Credits

Built on top of [dedao-dl](https://github.com/yann0917/dedao-dl) by yann0917.