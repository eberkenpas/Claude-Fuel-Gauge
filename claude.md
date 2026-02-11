# Claude Fuel Gauge

A CLI tool that displays your Anthropic API rate limit status with visual progress bars.

## Overview

This tool makes a minimal API call to Anthropic and reads the rate limit headers from the response to show remaining capacity for tokens, input/output tokens, and requests.

## Requirements

- Python 3
- `requests` library
- `ANTHROPIC_API_KEY` environment variable

## Usage

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python3 fuel_gauge.py
```

## Project Structure

- `fuel_gauge.py` - Main script, single-file application
- `requirements.txt` - Dependencies (just `requests`)

## Key Implementation Details

- Uses Anthropic API v1 messages endpoint with `anthropic-version: 2023-06-01`
- Sends a minimal request (1 token max, "hi" message) to get rate limit headers
- Parses these headers: `anthropic-ratelimit-tokens-*`, `anthropic-ratelimit-input-tokens-*`, `anthropic-ratelimit-output-tokens-*`, `anthropic-ratelimit-requests-*`
- Color-coded bars: green (>=50%), yellow (20-50%), red (<20%)

## Development Notes

- Keep it simple - this is intentionally a single-file tool
- No external dependencies beyond `requests`
- ANSI colors are hardcoded for terminal output
