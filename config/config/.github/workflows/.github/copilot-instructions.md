# GitHub Copilot Instructions for amzn-global-automator

## Project Overview
Automated, zero-infrastructure multi-regional Amazon affiliate deal publisher using GitHub Actions and Telegram channels.

## Core Architectural Rules
1. **Compliance First**: Every generated post or link must adhere to regional *de minimis* thresholds defined in `config/countries.yaml`. No items exceeding customs limits should be processed for strict regions (e.g., Israel ~$74.99).
2. **Tag Mapping**: Always inject the correct affiliate tag mapped in `config/channels.yaml` depending on the target country channel.
3. **Zero-Infra**: No external servers. All automation runs on GitHub Actions scheduled workflows (`.github/workflows/publisher.yml`).
4. **Code Style**: Clean, modular Python 3.10+ scripts located in `src/`, with robust error handling for API limits and network timeouts.
