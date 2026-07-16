# Moon Dev AI Agents - API Readiness Report

## Security notice

Credential values are intentionally not stored in this repository. Configure every
provider through local environment variables or an untracked `.env` file. Never add
full keys, key prefixes, fingerprints, or private wallet material to a report or commit.

## Provider configuration

| Service | Environment variable | Repository status |
|---|---|---|
| MoonDev | `MOONDEV_API_KEY` | Value redacted; verify locally |
| Anthropic | `ANTHROPIC_KEY` | Value redacted; verify locally |
| DeepSeek | `DEEPSEEK_KEY` | Value redacted; verify locally |
| xAI Grok | `GROK_API_KEY` | Value redacted; verify locally |
| OpenRouter | `OPENROUTER_API_KEY` | Value redacted; verify locally |
| Aster | `ASTER_API_KEY`, `ASTER_API_SECRET` | Configure locally before use |
| Birdeye | `BIRDEYE_API_KEY` | Configure locally before use |
| Solana RPC | `RPC_ENDPOINT` | Configure locally before use |
| Solana wallet | `SOLANA_PRIVATE_KEY` | Configure locally before use |

## Safe readiness check

1. Copy the repository's example environment file to a local ignored `.env` file.
2. Supply credentials from the relevant provider dashboard or a secrets manager.
3. Run the project's validation or test command without printing environment values.
4. Confirm that `.env`, generated reports, wallet material, and private outputs remain
   ignored before committing.
5. Rotate any credential that was previously stored in Git history or shared elsewhere.

This document records required configuration names only. It is not proof that a live
credential is active, funded, authorized, or safe for trading.
