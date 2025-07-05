# New Python Scripts Plan

## Proposed Scripts Analysis

### 1. log_parser - Log File Analysis Tool
**Purpose**: Parse and analyze log files with filtering and pattern matching
**Category**: Development Tools
**Key Features**:
- Filter by date ranges, log levels, keywords
- Extract error patterns and stack traces  
- Export filtered results to JSON/CSV
- Interactive terminal UI for browsing logs
- Regex pattern matching
**Dependencies**: `rich` for terminal UI, standard library otherwise
**Use Cases**:
- Debug application logs
- Monitor system logs for patterns
- Extract specific events from large log files

### 2. env_manager - Environment Variable Manager
**Purpose**: Manage and switch between different environment configurations
**Category**: Development Tools  
**Key Features**:
- Store multiple named environment sets
- Quick switching between dev/staging/prod configs
- Template support with variable substitution
- Secure handling of sensitive values
- Export to .env files or shell scripts
**Dependencies**: `cryptography` for secure storage, standard library
**Use Cases**:
- Manage API keys across environments
- Quick project environment switching
- Team environment sharing (without secrets)

### 3. port_scanner - Network Port Scanner
**Purpose**: Simple network port scanning and service detection
**Category**: Network/Security Tools
**Key Features**:
- Scan single hosts or CIDR ranges
- Common port presets (web, db, etc.)
- Service banner detection
- JSON/CSV output formats
- Rate limiting and timeout controls
**Dependencies**: `asyncio` for concurrent scanning, standard library
**Use Cases**:
- Network troubleshooting
- Security auditing
- Service discovery

## Implementation Priority

1. **log_parser** (High Priority)
   - Most universally useful for developers
   - Fills gap in current toolset
   - Good showcase for rich terminal UI

2. **env_manager** (Medium Priority)  
   - Complements existing dev tools
   - Addresses common developer pain point
   - Useful for team workflows

3. **port_scanner** (Lower Priority)
   - More specialized use case
   - Overlaps with existing tools (nmap)
   - Good for learning networking concepts

## Integration with Existing Project

### Directory Structure
```
py_scripts/
├── log_parser/
│   ├── __init__.py
│   ├── log_parser.py
│   ├── README.md
│   ├── Makefile
│   └── tests/
├── env_manager/
│   ├── __init__.py  
│   ├── env_manager.py
│   ├── README.md
│   ├── Makefile
│   └── tests/
└── port_scanner/
    ├── __init__.py
    ├── port_scanner.py  
    ├── README.md
    ├── Makefile
    └── tests/
```

### pyproject.toml Updates
```toml
[project.scripts]
log-parser = "py_scripts.log_parser.log_parser:main"
env-manager = "py_scripts.env_manager.env_manager:main"  
port-scanner = "py_scripts.port_scanner.port_scanner:main"
```

### Documentation Updates
- Add new scripts to main README.md
- Create category sections for better organization
- Include prerequisites and usage examples
- Add troubleshooting section

## Alternative Script Ideas
- **json_formatter** - Format and validate JSON files
- **color_picker** - Terminal color palette tool
- **qr_generator** - Generate QR codes from text/URLs
- **password_generator** - Secure password generation with options
- **file_organizer** - Organize files by date/type/size patterns