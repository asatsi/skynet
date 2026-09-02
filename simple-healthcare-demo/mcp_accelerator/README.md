# MCP Accelerator — Java Spring Boot to MCP Server Parser & Generator

**MCP Accelerator** is a generic automation tool that scans Java Spring Boot microservice codebases, analyzes OpenAPI 3.0 specifications and Spring `@RestController` source annotations, automatically categorizes microservices into logical business domains, and synthesizes domain-scoped **Model Context Protocol (MCP)** servers over HTTP/SSE and Stdio.

---

## Key Features

1. **Multi-Service & OpenAPI Parsing**:
   - Automatically detects Spring Boot projects via `pom.xml` / `build.gradle`.
   - Extracts server ports and application names from `application.properties` / `application.yml`.
   - Parses `openapi.yaml`, `openapi.json`, or falls back to scanning Spring `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping` annotations in `.java` source files.

2. **Smart Domain Classification**:
   - Groups microservices into cohesive business domains (e.g. `healthcare_domain`, `insurance_domain`, `scheduling_domain`).
   - Merges tool definitions so **one domain MCP server provides access to all tools within that domain**.
   - Resolves tool name collisions automatically.

3. **Domain MCP Server Generation**:
   - Synthesizes standalone, executable Python MCP servers for each domain using official `mcp.server.fastmcp`.
   - Generates async `httpx` handlers mapping tool parameters to microservice REST API calls.
   - Includes `pyproject.toml` (`uv`-compatible), `run.py`, and `README.md` for every generated domain server.

---

## Directory Structure

```
mcp_accelerator/
├── src/
│   └── mcp_accelerator/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py                # Rich CLI interface (scan & generate)
│       ├── parser.py             # Spring Boot & OpenAPI specification parser
│       ├── domain_classifier.py  # Domain aggregator & tool collision resolver
│       ├── generator.py          # MCP Server code generator
│       └── models.py             # Data models (MicroserviceMetadata, ToolEndpoint, DomainGroup)
├── pyproject.toml                # Hatchling package build configuration
├── run_accelerator.py            # Standalone launcher script
└── README.md
```

---

## How to Run with `uv`

Navigate to `skynet/mcp_accelerator`:

```bash
cd /Users/skpagare/my-lab/skynet/mcp_accelerator
```

### Option A: Using the Installed CLI Command (`mcp-accelerator`)

```bash
# Scan projects & preview domain tool categorization
uv run mcp-accelerator scan /path/to/spring/boot/projects

# Generate domain-scoped MCP servers
uv run mcp-accelerator generate /path/to/spring/boot/projects --output ./generated_servers
```

### Option B: Using the Launcher Script (`run_accelerator.py`)

```bash
# Scan projects
uv run run_accelerator.py scan /path/to/spring/boot/projects

# Generate domain-scoped MCP servers
uv run run_accelerator.py generate /path/to/spring/boot/projects --output ./generated_servers
```

---

## Running a Generated Domain MCP Server

Navigate to any generated domain server and start it with `uv`:

```bash
cd generated_servers/healthcare_domain_mcp
uv run python run.py
```
