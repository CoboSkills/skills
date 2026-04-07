---
name: messenger_send_node
description: Send messages using FLO blockchain via a Node.js script without using a browser.
requires:
  binaries:
    - node
    - npm
  env:
    - FLO_PRIVATE_KEY
---

# Messenger Send Node Skill

When the user asks to send a message programmatically without a browser, you must use the `run_command` tool to execute the `send_node.js` script.

## Setup & Dependencies
Before executing the script, ensure dependencies are installed by running:
`npm install`

## Network Activity Warning
**Note**: At runtime, this script fetches a supernode list from the FLO blockchain and establishes wss/https connections to discovered supernodes to broadcast the transaction. Network activity is expected.

## Security & Credentials (CRITICAL)
- **NEVER** ask the user to paste their private key in the chat.
- Instruct the user to securely set their private key as an environment variable named `FLO_PRIVATE_KEY` in their shell. No files or CLI arguments are allowed for this.

## Execution
Once the private key is securely available via the env var, execute the script like this:

```bash
node send_node.js --receiver "<RECEIVER_FLO_ID>" --message "<MESSAGE>"
```