#!/usr/bin/env python3
"""
red_team_mcp_server.py
A super-server that imports every tool from the individual pentest tools
"""

import asyncio
from fastmcp import FastMCP, Client  

red_team = FastMCP(
    name="red_team",
    instructions="RED TEAM MCP SERVER"
)

async def setup() -> None:
    # nmap mcp server
    nmap_client = Client("nmap.py")          
    nmap_proxy = FastMCP.from_client(nmap_client, name="nmap_proxy")
    await red_team.import_server("nmap", nmap_proxy)

if __name__ == "__main__":
    asyncio.run(setup())
    red_team.run()       
