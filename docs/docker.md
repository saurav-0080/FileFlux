# Docker Guide

## Overview

FileFlux uses Docker to package the CLI into a reproducible environment.
The Tkinter GUI runs natively on macOS — Docker handles CLI and automation.

## Image vs Container

- **Image**: The built package (like an executable). Built once, used many times.
- **Container**: A running instance of an image. Starts, does work, stops.

## Build the Image

```bash
docker build -t fileflux:1.0.0 .
```

## Run Commands

Show help:
```bash
docker run --rm fileflux:1.0.0 --help
```

Scan a directory:
```bash
docker run --rm \
  -v /path/to/your/folder:/data \
  fileflux:1.0.0 scan /data
```

Organize a directory:
```bash
docker run --rm \
  -v /path/to/your/folder:/data \
  -v $(pwd)/database:/app/database \
  fileflux:1.0.0 organize /data
```

## Volume Mounting

The container cannot access your Mac's filesystem unless you mount it.

- `/data` — the folder you want to organize
- `/app/database` — SQLite database (mount this for persistence)
- `/app/reports` — generated reports

## Database Persistence

Without mounting, the database is lost when the container exits.
Always mount the database directory:

```bash
-v $(pwd)/database:/app/database
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_PATH | /app/database/organizer.db | SQLite database location |
| LOG_LEVEL | INFO | Logging verbosity |

## Docker Compose

Instead of long docker run commands, use Compose:

```bash
docker compose run fileflux organize /data
docker compose run fileflux scan /data
```

## Security

Never put inside the image:
- `.env` files
- API keys or passwords
- Personal files
- Production database