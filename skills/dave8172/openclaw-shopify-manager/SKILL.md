---
name: openclaw-shopify-manager
description: Connect OpenClaw to Shopify stores for least-privilege OAuth setup, webhook signature validation, read-first store operations, and a small localhost-bound connector that can be published through user-managed HTTPS ingress such as Tailscale Serve. Use when setting up or operating Shopify access for OpenClaw, installing a Shopify app callback endpoint, checking Shopify connectivity, managing product/content/order workflows, handling Docker/container deployment edge cases, or preparing a host-managed Shopify connector service.
metadata:
  {
    "openclaw":
      {
        "primaryEnv": "SHOPIFY_API_KEY",
        "requires":
          {
            "env":
              [
                "SHOPIFY_API_KEY",
                "SHOPIFY_API_SECRET",
                "SHOPIFY_SHOP",
                "SHOPIFY_REDIRECT_URI",
              ],
          },
      },
  }
---

# OpenClaw Shopify Manager

Use this skill to set up and operate a Shopify connector for OpenClaw with a small local backend, a stable public callback/webhook URL, and conservative mutation safety.

## Core workflow

1. Read `references/setup.md` for the deployment path.
2. Read `references/tailscale.md` when Tailscale is missing or needs configuration.
3. Read `references/systemd.md` when installing or operating the backend as a host service.
4. Read `references/docker.md` when OpenClaw or the connector runs in Docker or another containerized environment.
5. Read `references/security-and-behavior.md` when clarifying what the skill does and does not do.
6. Use `scripts/shopify-connector.mjs` for auth URL generation, callback handling, webhook validation, and API calls.
7. Use `scripts/check-tailscale.sh` to detect whether Tailscale is present and whether Serve/Funnel is likely available.
8. Use `references/systemd.md` plus `assets/shopify-connector.service.txt` for documentation-only systemd setup guidance on host systems.

## Safety rules

- Default to read-only or plan-first behavior unless the user clearly asks for mutations.
- Before any destructive or store-changing action, restate the intended change briefly and get confirmation.
- Prefer least-privilege scopes. Do not request broad Shopify scopes unless the requested workflow requires them.
- Keep Shopify secrets in `.env`, not in tracked config files.
- Treat public callback URLs and Tailscale exposure as infrastructure work; verify paths and health endpoints after changes.

## Recommended deployment shape

- Run the connector locally on `127.0.0.1`.
- Persist config, token state, and logs under a dedicated directory.
- Expose the connector through a stable HTTPS path.
- Prefer Tailscale Serve/Funnel when the user wants the simplest production-grade public ingress without adding Caddy or Nginx.
- Run the connector under systemd for long-lived callback/webhook handling on host/VM deployments.
- For Docker deployments, prefer running the connector on the host or as a dedicated sidecar instead of forcing systemd into the OpenClaw container.

## Common tasks

### Connect a store

- Prepare config and `.env` from `assets/` examples.
- Install/start the systemd service if long-lived operation is needed.
- Check or install Tailscale if using Serve/Funnel.
- Generate the auth URL with `scripts/shopify-connector.mjs auth-url`.
- Complete the Shopify app install and callback.
- Verify with `shop-info` or `test`.

### Operate the backend service

For host/VM deployments:

- Use `assets/shopify-connector.service` as the service template.
- Use `systemctl` and `journalctl` directly for lifecycle and logs.
- Follow `references/systemd.md` for the manual install and verification flow.

For Docker/sidecar deployments:

- use container lifecycle commands instead of the systemd helper
- persist `config.json`, `.env`, `state/`, and `logs/` with a mounted volume
- prefer host Tailscale or host reverse proxying for the public callback path

### Expose the callback endpoint

- Prefer the Tailscale path-prefix model described in `references/tailscale.md`.
- Verify `/healthz` locally before exposing it.
- Verify the final public callback and webhook base paths match Shopify app settings exactly.

### Read and update Shopify data

Supported helper commands in the bundled connector include:

- `auth-url`
- `exchange-code`
- `run-server`
- `test`
- `shop-info`
- `list-products`
- `get-product`
- `update-product`
- `list-blogs`
- `list-articles`
- `create-article`
- `update-article`

Use write commands only after user confirmation.

## Resource map

- Setup guide: `references/setup.md`
- Tailscale guide: `references/tailscale.md`
- systemd guide: `references/systemd.md`
- Docker guide: `references/docker.md`
- Shopify scopes and safety: `references/scopes-and-safety.md`
- Connector runtime: `scripts/shopify-connector.mjs`
- Service template: `assets/shopify-connector.service`
- Tailscale checker: `scripts/check-tailscale.sh`
- Example env/config/service files: `assets/`



cripts/check-tailscale.sh`
- Example env/config/service files: `assets/`



