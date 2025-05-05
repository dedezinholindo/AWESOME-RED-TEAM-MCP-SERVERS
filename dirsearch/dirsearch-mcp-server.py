#!/usr/bin/env python3
"""
Dirsearch MCP Server
--------------------

Exposes dirsearch web‑content‑discovery capabilities to any Model Context
Protocol client (e.g. Claude Desktop).  Each tool wraps a common use‑case and
returns the raw text output for downstream analysis by the LLM.

Tools provided
==============

• quick_scan            – Basic scan with common extensions
• recursive_scan        – Recursive brute‑force
• deep_recursive_scan   – Deep recursive brute‑force
• subdirs_scan          – Scan specific sub‑directories
• wordlist_scan         – Use one or more custom wordlists
• json_report_scan      – Save results in JSON and return its content
• proxy_scan            – Scan through an HTTP/SOCKS proxy
• authenticated_scan    – Scan with HTTP authentication (no status filter)
• custom_scan           – Power‑user entry point for arbitrary flags
"""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
from typing import List

from mcp.server.fastmcp import FastMCP

###############################################################################
# FastMCP server setup
###############################################################################

mcp = FastMCP(
    name="dirsearch-scanner",
    instructions=(
        "This server exposes dirsearch web‑content‑discovery capabilities. "
        "Call an appropriate tool and the server will return the raw text "
        "output produced by the dirsearch command."
    ),
)

###############################################################################
# Internal helpers
###############################################################################


def _run_dirsearch(args: List[str]) -> str:
    """Execute **dirsearch** with *args* and return its stdout."""
    result = subprocess.run(
        ["dirsearch", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"dirsearch exited with {result.returncode}:\n{result.stderr or result.stdout}"
        )
    return result.stdout


def _base_args(
    threads: int | None = 20,
    include_errors: bool = False,
) -> List[str]:
    """Return dirsearch flags common to most tools.

    * Quiet mode (-q) to suppress progress bar
    * Thread count (-t)
    * By default include only HTTP 2xx–3xx responses (--include-status 200-399)¹
      unless *include_errors* is True.
    """
    args: List[str] = ["-q"]
    if threads:
        args += ["-t", str(threads)]
    if not include_errors:
        # Only successful and redirect responses
        args += ["--include-status", "200-399"]
    return args


###############################################################################
# Tools
###############################################################################


@mcp.tool()
def quick_scan(
    url: str,
    extensions: str | None = "php,asp,aspx,jsp,html,js,txt",
    threads: int | None = 20,
    show_errors: bool = False,
) -> str:
    """Basic scan of *url* with a set of common extensions."""
    return _run_dirsearch(
        _base_args(threads, include_errors=show_errors)
        + ["-u", url, "-e", extensions]
    )


@mcp.tool()
def recursive_scan(
    url: str,
    extensions: str | None = "php,asp,aspx,jsp,html,js,txt",
    max_depth: int | None = 3,
    threads: int | None = 20,
    show_errors: bool = False,
) -> str:
    """Recursively brute‑force directories up to *max_depth* for *url*."""
    args = (
        _base_args(threads, include_errors=show_errors)
        + ["-u", url, "-e", extensions, "-r"]
    )
    if max_depth is not None:
        args += ["-R", str(max_depth)]
    return _run_dirsearch(args)


@mcp.tool()
def deep_recursive_scan(
    url: str,
    extensions: str | None = "php,asp,aspx,jsp,html,js,txt",
    threads: int | None = 40,
    show_errors: bool = False,
) -> str:
    """Perform deep recursive brute‑force on *url*."""
    return _run_dirsearch(
        _base_args(threads, include_errors=show_errors)
        + ["-u", url, "-e", extensions, "--deep-recursive"]
    )


@mcp.tool()
def subdirs_scan(
    url: str,
    subdirs: str,
    extensions: str | None = "php,asp,aspx,jsp,html,js,txt",
    threads: int | None = 20,
    show_errors: bool = False,
) -> str:
    """Scan specific sub‑directories of *url*."""
    return _run_dirsearch(
        _base_args(threads, include_errors=show_errors)
        + ["-u", url, "-e", extensions, "--subdirs", subdirs]
    )


@mcp.tool()
def wordlist_scan(
    url: str,
    wordlists: str,
    extensions: str | None = "",
    threads: int | None = 20,
    show_errors: bool = False,
) -> str:
    """Use one or more custom wordlists for brute‑forcing."""
    args = _base_args(threads, include_errors=show_errors) + ["-u", url, "-w", wordlists]
    if extensions:
        args += ["-e", extensions]
    return _run_dirsearch(args)


@mcp.tool()
def json_report_scan(
    url: str,
    extensions: str | None = "php,asp,aspx,jsp,html,js,txt",
    threads: int | None = 20,
    show_errors: bool = False,
) -> str:
    """Run a scan and return the JSON report content as string."""
    import json  # Local import to avoid unnecessary dependency if unused

    with tempfile.TemporaryDirectory() as tmp:
        report_path = os.path.join(tmp, "report.json")
        _run_dirsearch(
            _base_args(threads, include_errors=show_errors)
            + [
                "-u",
                url,
                "-e",
                extensions,
                "--format",
                "json",
                "-o",
                report_path,
            ]
        )
        with open(report_path, "r", encoding="utf-8") as fh:
            return fh.read()


@mcp.tool()
def proxy_scan(
    url: str,
    proxy: str,
    extensions: str | None = "php,asp,aspx,jsp,html,js,txt",
    threads: int | None = 20,
    show_errors: bool = False,
) -> str:
    """Run dirsearch through an HTTP/SOCKS proxy."""
    return _run_dirsearch(
        _base_args(threads, include_errors=show_errors)
        + ["-u", url, "-e", extensions, "--proxy", proxy]
    )


@mcp.tool()
def authenticated_scan(
    url: str,
    auth_cred: str,
    auth_type: str = "basic",
    extensions: str | None = "php,asp,aspx,jsp,html,js,txt",
    threads: int | None = 20,
) -> str:
    """
    Brute‑force *url* with HTTP authentication.

    Note: **No default status‑code filter** so that auth failures (401/403) and
    other error codes are visible.
    """
    return _run_dirsearch(
        _base_args(threads, include_errors=True)  # Always include all codes
        + [
            "-u",
            url,
            "-e",
            extensions,
            "--auth",
            auth_cred,
            "--auth-type",
            auth_type,
        ]
    )


@mcp.tool()
def custom_scan(url: str, extra_args: str) -> str:
    """Advanced/custom scan entry point (no status-code filter by default)."""
    return _run_dirsearch(
        _base_args(include_errors=True)  # Let the caller decide in extra_args
        + ["-u", url]
        + shlex.split(extra_args)
    )


###############################################################################
# Entrypoint
###############################################################################

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dirsearch MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="SSE port if using --transport sse (default: 8000)",
    )
    cli = parser.parse_args()

    if cli.transport == "sse" and cli.port != 8000:
        mcp.settings.port = cli.port

    mcp.run(transport=cli.transport)
