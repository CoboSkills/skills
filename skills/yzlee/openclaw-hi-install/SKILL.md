---
name: openclaw-hi-install
description: Installs Hi into a local OpenClaw host through the official ClawHub path, then completes register, activate, receiver setup, and health checks through Hi's high-level install control tools.
compatibility: OpenClaw host setup skill. Use only when the host is OpenClaw and the user is installing Hi through ClawHub.
---

# OpenClaw Hi Install

This installs Hirey's agent platform, not Hi.Events.

## Use When

- the current host is OpenClaw
- the user wants to install or repair Hi on this OpenClaw host
- the user wants the official OpenClaw path that ends in a working Hi installation, not just a partially mounted MCP

## Do Not Use When

- the host is not OpenClaw
- the user wants a generic personal-agent install path with a public URL instead of ClawHub
- the turn is only about using Hi after installation is already healthy

## Rules

- treat ClawHub as the canonical OpenClaw entrypoint; do not switch the user to a raw-skill or ad-hoc install path
- use the official Hi packages at the current pinned public release versions: `@hirey/hi-mcp-server@0.1.6` and, when local durable delivery is enabled, `@hirey/hi-agent-receiver@0.1.7`
- install the Hi npm packages into a user-writable vendor dir under `~/.openclaw/vendor/hi`; do not rely on `npm -g`, `sudo`, or any elevated install path
- mount `hi-mcp-server` from that vendor dir as a local `stdio` MCP child process
- always set `HI_PLATFORM_BASE_URL` explicitly to the target Hi environment
- keep `HI_MCP_TRANSPORT=stdio`
- keep `HI_MCP_PROFILE=openclaw-main` unless the user explicitly wants a different stable profile
- keep the install state in a stable directory so later turns can reuse the same identity and receiver config
- use `hi_agent_install` as the main path; do not make the user manually walk `register -> connect -> activate` unless you are diagnosing a lower-level break
- for OpenClaw, install with `host_kind="openclaw"` and enable `local_receiver`
- for local OpenClaw delivery, use `openclaw_hooks` with `http://127.0.0.1:18789/hooks/agent`
- when configuring OpenClaw hooks, keep `hooks.path="/hooks"`; `/hooks/agent` is the full agent endpoint under that base path, not the base path itself
- enable OpenClaw hook ingress with `hooks.enabled=true`; setting `hooks.path` or `hooks.token` alone is not enough because `/hooks/*` routes are only mounted when hooks are enabled
- OpenClaw hooks require a dedicated bearer token; generate a fresh random token for hooks, reuse that same token in the Hi receiver config, and never reuse the gateway auth token as `hooks.token`
- when allowing requested session keys, make sure `hooks.allowedSessionKeyPrefixes` includes the active agent prefix; for the default main agent this should include `agent:main:`
- before calling `hi_agent_install`, inspect the current OpenClaw visible session and ask whether it should become the default Hi continuation route
- if the user explicitly agrees, pass `host_session_key` and the best available reply target fields (`default_reply_channel`, `default_reply_to`, `default_reply_account_id`, `default_reply_thread_id`) together with `route_missing_policy="use_explicit_default_route"`
- if the user does not explicitly agree, do not invent a default route or placeholder session key; leave it unset and explain that continuity is origin-capture-only until a workflow writes a binding or the user later binds a default route
- continuity is not really ready unless OpenClaw allows requested session keys; verify `hooks.allowRequestSessionKey=true` and that Hi's session prefix policy is allowed before declaring the install healthy
- ask the user before permission prompts, auth prompts, or destructive reset steps
- if the install is broken, prefer `hi_agent_doctor`; if a clean reinstall is needed, use `hi_agent_reset` before rebuilding state

## Install Order

1. Confirm the target Hi environment with the user.
2. Install or update the official Hi ClawHub skill/package and any required local package steps it asks for.
3. Install the fixed Hi npm packages into `~/.openclaw/vendor/hi`, for example with `npm install --prefix ~/.openclaw/vendor/hi @hirey/hi-mcp-server@0.1.6 @hirey/hi-agent-receiver@0.1.7`, so the install stays user-local and does not require elevated exec.
4. Mount `~/.openclaw/vendor/hi/node_modules/.bin/hi-mcp-server` as the local `stdio` MCP with explicit `HI_PLATFORM_BASE_URL`, stable `HI_MCP_PROFILE`, and stable state dir.
5. If you need to enable OpenClaw hooks, set `hooks.enabled=true`, keep `hooks.path="/hooks"`, and keep the Hi receiver target at `http://127.0.0.1:18789/hooks/agent`; do not collapse those into one value.
6. Generate a fresh hooks token, set it on both OpenClaw hooks and the Hi receiver auth, make sure it is different from the gateway auth token, and set `hooks.allowedSessionKeyPrefixes` to include the active agent prefix (normally `agent:main:`).
7. Run `hi_agent_install` with:
   - `display_name`
   - `host_kind="openclaw"`
   - `enable_local_receiver=true`
   - `receiver_transport="claim"`
   - `receiver_start=true`
   - `host_adapter_kind="openclaw_hooks"`
   - the current OpenClaw hooks bearer token
   - and, only when the user explicitly confirms it, the current session as `host_session_key` plus the matching `default_reply_*` fields
8. Only when the user explicitly confirms the current session should you also set `hooks.defaultSessionKey` / default continuation route to that same visible session; otherwise leave it unset.
9. Run `hi_agent_doctor` and fix blockers before declaring success.

## Validation

- confirm `hi_agent_doctor` reports no blockers
- confirm `platform_base_url` matches the intended Hi environment
- confirm the installation is active
- confirm `delivery_capabilities` prefer `local_receiver`
- confirm the receiver config path is present and the delivery probe succeeds
- confirm the mounted `hi-mcp-server` binary comes from the user-local vendor dir and is version `0.1.6`, not an older global npm install
- if doctor reports `openclaw_hooks_base_path_misconfigured`, fix OpenClaw `hooks.path` back to `/hooks` before declaring the install healthy
- confirm `hooks.enabled=true`; otherwise `/hooks/agent` is never mounted and local receiver delivery will fail with `host_adapter_http_404`
- confirm `hooks.token` is different from the gateway auth token and that `hooks.allowedSessionKeyPrefixes` includes the active agent prefix (normally `agent:main:`)
- if the user approved a default continuation route, confirm `continuity_state` is `explicit_default_route_ready` and `default_reply_route` is populated
- if the user did not approve a default route, confirm the result honestly reports origin-capture-only / continuity-not-ready instead of pretending continuity is solved

## Boundaries

- do not ask an ordinary OpenClaw user to fetch AWS credentials, CodeArtifact tokens, or any private registry access
- do not treat direct raw-skill install as the recommended OpenClaw path; OpenClaw should come from ClawHub
- do not silently switch to a different Hi environment than the user requested
- do not install Hi through a global npm prefix that needs elevated exec when a user-local vendor dir works
- do not reuse the gateway auth token as the OpenClaw hooks token, and do not invent placeholder default session keys like `hook:ingress`
