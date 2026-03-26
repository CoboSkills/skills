# Setup

## Overview

This skill assumes a small local Shopify connector process that does three jobs:

1. Generates Shopify OAuth install URLs
2. Accepts the OAuth callback and exchanges the code for an offline token
3. Accepts validated Shopify webhooks

Run it locally and expose it over HTTPS. For most OpenClaw users, the easiest production-friendly path is Tailscale Serve/Funnel.

If OpenClaw runs in Docker, read `docker.md` before choosing where the connector should live.

## Recommended filesystem layout

Example target layout on the host:

- runtime root: `~/oc/shopify-runtime`
- config: `~/oc/shopify-runtime/config.json`
- secrets/env: `~/oc/shopify-runtime/.env`
- logs: `~/oc/shopify-runtime/logs/`
- state: `~/oc/shopify-runtime/state/`

Keep secrets out of git.

## Deployment shape decision

Choose one before installing anything:

1. Host/VM deployment: connector on the host, managed by systemd
2. Docker OpenClaw + host connector: OpenClaw in Docker, connector on the host
3. Docker sidecar deployment: connector in a dedicated container with mounted persistent storage

For most Docker users, option 2 is the least fragile.

## Minimal setup sequence

1. Copy `assets/config.example.json` and `assets/env.example` into the runtime root.
2. Fill Shopify app credentials in `.env`.
3. Set the final public callback URL in both config and Shopify.
4. Start the local connector.
5. Expose it publicly over HTTPS.
6. Generate the install URL.
7. Complete app installation in Shopify.
8. Verify with a read-only API call.

## Runtime configuration

Use config for non-secret values and `.env` for secrets/runtime state.

### Non-secret config

Expected keys:

- `shop`
- `apiVersion`
- `scopes`
- `redirectUri`
- `publicBaseUrl`
- `serverHost`
- `serverPort`
- `mode`
- `allowedMutations`

### Secret env

Expected keys:

- `SHOPIFY_API_KEY`
- `SHOPIFY_API_SECRET`
- `SHOPIFY_ACCESS_TOKEN`

## Production notes

- Bind locally on `127.0.0.1`, not `0.0.0.0`, unless there is a specific reason not to.
- Use systemd if callbacks or webhooks must survive shell disconnects and reboots.
- Keep scopes lean.
- Verify the exact callback path before installing the Shopify app.

## Validation checklist

Before using the connector in production, verify:

- local `healthz` responds
- service stays up under systemd
- public HTTPS URL is reachable
- Shopify callback path matches exactly
- offline token is written locally after install
- at least one read-only API call succeeds
