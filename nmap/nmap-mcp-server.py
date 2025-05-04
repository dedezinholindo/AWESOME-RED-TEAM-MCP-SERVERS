#!/usr/bin/env python3
"""
Nmap MCP Server
---------------

Exposes high‑level network‑scanning tools to any Model Context Protocol
client (e.g. Claude Desktop).  Each tool wraps a common Nmap use‑case and
returns the raw text output for downstream analysis by the LLM.

Tools provided
==============

• full_port_scan      – All TCP ports (1‑65535) with a stealth SYN scan
• stealth_syn_scan    – Quieter SYN scan on specified ports
• tcp_connect_scan    – Full TCP connect (-sT) scan, no root needed
• udp_scan            – UDP port scan (-sU)
• os_detection_scan   – OS fingerprinting (-O)
• ping_sweep          – ICMP (-sn) network sweep
• aggressive_scan     – “All‑in‑one” (-A) scan (OS + version + scripts)
• custom_scan         – Power‑user entry point for arbitrary flags
"""

from __future__ import annotations

import shlex
import subprocess
from typing import List

from mcp.server.fastmcp import FastMCP

###############################################################################
# FastMCP server setup
###############################################################################

mcp = FastMCP(
    name="nmap-scanner",
    instructions=(
        "This server exposes Nmap network‑scanning capabilities. "
        "Call an appropriate tool and the server will return the raw text "
        "output produced by the Nmap command."
    ),
)

###############################################################################
# Internal helper
###############################################################################


def _run_nmap(args: List[str]) -> str:
    """
    Execute Nmap with *args* and return its stdout.

    Raises
    ------
    RuntimeError
        If Nmap exits with a non‑zero status.
    """
    result = subprocess.run(
        ["nmap", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Nmap exited with {result.returncode}:\n{result.stderr or result.stdout}"
        )
    return result.stdout


def _add_pn(args: List[str]) -> List[str]:
    """Prepend -Pn to every scan except ping_sweep."""
    return ["-Pn", *args]


###############################################################################
# Tools
###############################################################################


@mcp.tool()
def full_port_scan(target: str, timing: str | None = "T4") -> str:
    """
    Scan **all** TCP ports (1‑65535) on *target* using a stealth SYN scan.

    Parameters
    ----------
    target : str
        Host or CIDR to scan.
    timing : str, optional
        Nmap timing template (T0–T5). Default "T4".
    """
    return _run_nmap(_add_pn(["-sS", "-p", "1-65535", f"-{timing}", target]))


@mcp.tool()
def stealth_syn_scan(target: str, ports: str = "1-1000", timing: str | None = "T3") -> str:
    """
    Quieter **SYN** scan (-sS) against selected *ports*.

    Parameters
    ----------
    target : str
        Host/network.
    ports : str
        Port list/range (e.g. "22,80,443" or "1-1024").
    timing : str, optional
        Timing template. Default "T3".
    """
    return _run_nmap(_add_pn(["-sS", "-p", ports, f"-{timing}", target]))


@mcp.tool()
def tcp_connect_scan(target: str, ports: str = "1-1024", timing: str | None = "T3") -> str:
    """
    Full **TCP connect** scan (-sT). Works without root/CAP_NET_RAW.

    target : str  – Host/network
    ports  : str  – Port spec (default 1‑1024)
    """
    return _run_nmap(_add_pn(["-sT", "-p", ports, f"-{timing}", target]))


@mcp.tool()
def udp_scan(target: str, ports: str = "1-1000", timing: str | None = "T4") -> str:
    """
    **UDP** port scan (-sU). Requires root or appropriate capabilities.
    """
    return _run_nmap(_add_pn(["-sU", "-p", ports, f"-{timing}", target]))


@mcp.tool()
def os_detection_scan(target: str, quick: bool = False) -> str:
    """
    Detect the operating system of *target* (-O).

    quick : bool – If True, add -F for a faster pre‑scan.
    """
    args = ["-O", target]
    if quick:
        args.insert(0, "-F")
    return _run_nmap(_add_pn(args))


@mcp.tool()
def ping_sweep(network: str) -> str:
    """
    ICMP **ping sweep** (-sn) over *network* (CIDR).

    Observação: esta é a única ferramenta que **não** inclui -Pn, pois o
    objetivo é justamente descobrir hosts ativos.
    """
    return _run_nmap(["-sn", network])


@mcp.tool()
def aggressive_scan(target: str) -> str:
    """
    Nmap’s **aggressive** mode (-A): OS, version, scripts, traceroute.
    """
    return _run_nmap(_add_pn(["-A", target]))


@mcp.tool()
def custom_scan(target: str, extra_args: str) -> str:
    """
    **Advanced / custom** scan.  Supply any extra Nmap flags verbatim.

    extra_args
        Example: ``"-p 80,443 --script vuln"``.
    """
    return _run_nmap(_add_pn([*shlex.split(extra_args), target]))


###############################################################################
# Entrypoint
###############################################################################

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Nmap MCP Server")
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
