#!/usr/bin/env python3
"""Claude Fuel Gauge - Show remaining API token capacity."""

import os
import sys
from datetime import datetime, timezone

import requests

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
BAR_WIDTH = 40

# ANSI color codes
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_color(pct):
    if pct >= 50:
        return GREEN
    elif pct >= 20:
        return YELLOW
    return RED


def render_bar(pct, width=BAR_WIDTH):
    filled = round(width * pct / 100)
    empty = width - filled
    color = get_color(pct)
    return f"{color}{'█' * filled}{DIM}{'░' * empty}{RESET}"


def format_remaining_time(reset_str):
    try:
        reset_dt = datetime.fromisoformat(reset_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = reset_dt - now
        total_seconds = int(delta.total_seconds())
        if total_seconds <= 0:
            return "now"
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if not parts:
            parts.append(f"{seconds}s")
        return " ".join(parts)
    except (ValueError, TypeError):
        return "unknown"


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print(f"{RED}Error: ANTHROPIC_API_KEY environment variable not set.{RESET}")
        print("Export your key:  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    body = {
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "hi"}],
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=body, timeout=30)
    except requests.ConnectionError:
        print(f"{RED}Error: Could not connect to the Anthropic API.{RESET}")
        sys.exit(1)
    except requests.Timeout:
        print(f"{RED}Error: Request timed out.{RESET}")
        sys.exit(1)

    if resp.status_code == 401:
        print(f"{RED}Error: Invalid API key (401 Unauthorized).{RESET}")
        sys.exit(1)
    if resp.status_code == 403:
        print(f"{RED}Error: Access forbidden (403). Check your API key permissions.{RESET}")
        sys.exit(1)

    h = resp.headers

    # Token gauge (combined)
    tokens_limit = int(h.get("anthropic-ratelimit-tokens-limit", 0))
    tokens_remaining = int(h.get("anthropic-ratelimit-tokens-remaining", 0))
    tokens_reset = h.get("anthropic-ratelimit-tokens-reset", "")

    # Input tokens
    input_limit = int(h.get("anthropic-ratelimit-input-tokens-limit", 0))
    input_remaining = int(h.get("anthropic-ratelimit-input-tokens-remaining", 0))

    # Output tokens
    output_limit = int(h.get("anthropic-ratelimit-output-tokens-limit", 0))
    output_remaining = int(h.get("anthropic-ratelimit-output-tokens-remaining", 0))

    # Requests
    req_limit = int(h.get("anthropic-ratelimit-requests-limit", 0))
    req_remaining = int(h.get("anthropic-ratelimit-requests-remaining", 0))

    def pct(remaining, limit):
        return (remaining / limit * 100) if limit else 0

    tokens_pct = pct(tokens_remaining, tokens_limit)
    input_pct = pct(input_remaining, input_limit)
    output_pct = pct(output_remaining, output_limit)
    req_pct = pct(req_remaining, req_limit)

    time_left = format_remaining_time(tokens_reset)

    print()
    print(f"{BOLD}⛽ Claude Fuel Gauge{RESET}")
    print("═" * 47)
    print()

    if tokens_limit:
        print(f"Tokens:  [{render_bar(tokens_pct)}]  {tokens_pct:.0f}%")
        print(f"         {tokens_remaining:,} / {tokens_limit:,} remaining")
        print()

    if input_limit:
        print(f"Input:   [{render_bar(input_pct)}]  {input_pct:.0f}%")
        print(f"         {input_remaining:,} / {input_limit:,} remaining")

    if output_limit:
        print(f"Output:  [{render_bar(output_pct)}]  {output_pct:.0f}%")
        print(f"         {output_remaining:,} / {output_limit:,} remaining")

    if req_limit:
        print(f"Reqs:    [{render_bar(req_pct)}]  {req_pct:.0f}%")
        print(f"         {req_remaining:,} / {req_limit:,} remaining")

    if tokens_reset:
        print()
        print(f"Resets:  {tokens_reset} (in {time_left})")

    print()


if __name__ == "__main__":
    main()
