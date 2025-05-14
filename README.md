# MCP Security Toolkit

> **One‑command installer and unified config for Cyproxio’s ********************[`mcp-for-security`](https://github.com/cyproxio/mcp-for-security)******************** — plus space for new community‑driven tools.**

## ✨ About this project

Cyproxio’s original *mcp‑for‑security* repository provides Model‑Context‑Protocol (MCP) servers for many of the most popular offensive‑security programs, letting AI agents drive them through a single JSON interface. This fork keeps all that great tools **and** adds brand‑new MCP wrappers for tools that haven’t been covered yet.&#x20;

## 🚀 Quick‑start installer

1. Clone this repository.
2. Run the installation script; it will automatically:

   * install Node.js, npm, git & jq (if missing);
   * build every Node‑based MCP server with `npm install && npm run build`;
   * generate a ready‑to‑use `mcp.config.json` pointing to each binary.

```bash
./install_mcp.sh               # default path: $HOME/mcp-project/teste-others
./install_mcp.sh /opt/mcp      # custom path example
```

After the script completes, point your AI agent (Claude/ChatGPT, etc.) to the generated config and start launching scans:

```bash
claude mcp run nuclei -- -u https://example.com
```

## 📦 Tools currently supported

The installer compiles the following MCP servers shipped by Cyproxio:

| Tool                  | Purpose                                   |
| --------------------- | ----------------------------------------- |
| alterx                | Regex‑based wordlist generation           |
| amass                 | Subdomain enumeration                     |
| arjun                 | Hidden HTTP parameter discovery           |
| crtsh                 | Certificate transparency subdomain lookup |
| ffuf                  | Web content fuzzing                       |
| http‑headers‑security | HTTP security‑header audit                |
| httpx                 | Multipurpose HTTP probing                 |
| masscan               | Internet‑scale port scanning              |
| mobsf                 | Mobile application security testing       |
| nmap                  | Service & vulnerability scanning          |
| nuclei                | Template‑based vulnerability scanning     |
| shuffledns            | High‑speed DNS brute‑forecasting          |
| sqlmap                | Automated SQL injection exploitation      |
| sslscan               | TLS/SSL configuration assessment          |
| waybackurls           | Passive URL enumeration (Wayback)         |

## 🛣️ Roadmap

| Status         | Planned MCP wrapper                    |
| -------------- | -------------------------------------- |
| 🔜 in progress | **Katana** – fast spidering / crawling |
| 🗓 2025        | Let's see …                            |

## 🛠 Building Claude Desktop on Linux

If you prefer a desktop UI for Claude instead of command‑line, you can build **Claude Desktop** on any Debian‑based distro through *aaddrick/claude-desktop-debian*:

```bash
# 1. Clone the repo
git clone https://github.com/aaddrick/claude-desktop-debian.git
cd claude-desktop-debian

# 2. Build (defaults to .deb and cleans temp files)
./build.sh

# Other options
./build.sh --build appimage --clean no   # create AppImage and keep build files
./build.sh --build deb --clean yes       # explicit .deb, clean after build
```

The script checks dependencies, extracts resources from the Windows release, and produces a native `.deb` or portable `.AppImage` package — perfect for integrating with your MCP agents.

## 📜 License & credits

Original MCP server code is MIT‑licensed © [Cyproxio](https://github.com/cyproxio). Additional wrappers in this fork inherit the same license unless noted otherwise.

Happy hacking! 🚩
