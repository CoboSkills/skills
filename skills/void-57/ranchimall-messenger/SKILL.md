---
name: messenger_send_node
description: Send messages using FLO blockchain via a Node.js script without using a browser.
---

# Messenger Send Node Skill

When the user asks to send a message programmatically without a browser, use the `run_command` tool to execute the `send_node.js` script like this:

`node send_node.js --key "<YOUR_PRIVATE_KEY>" --receiver "<RECEIVER_FLO_ID>" --message "<MESSAGE>"`

Before running the command, ensure that you have all the necessary inputs from the user (private key, receiver ID, and the message content). If any are missing, ask the user for them. Ensure that you do not expose the private key publicly in your text responses.