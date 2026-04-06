---
name: paynode-402
description: Official PayNode CLI for stateless HTTP 402 micro-payments on Base L2.
author: PayNode Labs
homepage: https://github.com/PayNodeLabs/paynode-402-cli
metadata:
  openclaw:
    requires:
      env:
        - CLIENT_PRIVATE_KEY
      files:
        - "~/.config/paynode/config.json"
      bins:
        - bun
    primaryEnv: CLIENT_PRIVATE_KEY
    cliHelp: |
      Usage: bunx @paynodelabs/paynode-402-cli [command]
      Commands:
        check              Check wallet readiness (ETH/USDC)
        mint               Mint test USDC
        request <URL>      Access protected API
        list-paid-apis     Marketplace discovery
        invoke-paid-api    Execution flow
        tasks              Manage background tasks
---

# 💳 PayNode 402 CLI Skill (v2.6.0)

This skill provides autonomous payment capabilities for HTTP 402 (Payment Required) challenges on Base L2.

## 🛠️ Setup & Config (Mandatory)

To ensure this skill can sign transactions even in non-interactive shells (like OpenClaw Gateway), it supports a dual-layer configuration priority:

1. **Priority B (Environment Variable)**: The CLI will first check for `CLIENT_PRIVATE_KEY` in your system environment.
2. **Priority A (XDG Config Fallback)**: If the env var is missing, it will automatically search for a JSON config at: `~/.config/paynode/config.json`.
   - **Format**: `{"CLIENT_PRIVATE_KEY": "0x..."}`
   
**Recommendation**: Use **Priority B** for dynamic/containerized environments, and **Priority A** for persistent local development or cases where `.bashrc` is not sourced.

## 🛡️ Security Governance (Critical)

To comply with **ClawHub Safety Standards**, the Agent MUST strictly follow these protocols:

1. **Burner Wallet ONLY**: Never use high-value primary keys. Advise users to use a dedicated burner address with minimal USDC/ETH for this skill.
2. **Mainnet YES-Confirmation**: Before calling `request` or `invoke-paid-api` on **Mainnet**, the Agent MUST explicitly prompt the user: "Allow payment of <PRICE> on Mainnet?". Proceed ONLY on "YES".
3. **Data Path Isolation**: The `data_binary` field returns a local filesystem path. Only read this path if generated during the current session's request.
4. **No Parameter Hallucination**: ALWAYS call `get-api-detail <ID>` to fetch the correct `input_schema` before execution.

## 🚀 Cold Start (Network Operations)

The first action MUST be indexing the marketplace (**Outbound request**). Use this to understand current offerings:

```bash
bunx @paynodelabs/paynode-402-cli list-paid-apis --network testnet --json --limit 5
```

## 📋 Command Reference

| Command           | Usage Example                    | Purpose                        |
| :---------------- | :------------------------------- | :----------------------------- |
| `check`           | `check --network testnet --json` | Balance & Readiness check      |
| `get-api-detail`  | `get-api-detail <ID> --json`     | **REQUIRED** before invocation |
| `invoke-paid-api` | `invoke-paid-api <ID> --json`    | Market payment flow            |
| `tasks`           | `tasks list`                     | Async progress monitor         |
| `mint`            | `mint --amount 100 --json`       | Get test tokens (Base Sepolia) |

### 🛠️ Global Flags

- `--network <mainnet|testnet>`: Target (Default: testnet).
- `--confirm-mainnet`: Required for real USDC.
- `--json`: Required for agent parsing.

---

## 🔗 Resources

- **GitHub**: [PayNodeLabs/paynode-402-cli](https://github.com/PayNodeLabs/paynode-402-cli)
- **Faucet**: [Base Official Faucets](https://docs.base.org/docs/development/faucets)
- **NPM**: [@paynodelabs/paynode-402-cli](https://www.npmjs.com/package/@paynodelabs/paynode-402-cli)
- **Protocol**: [PayNode Specification](https://docs.paynode.dev)
