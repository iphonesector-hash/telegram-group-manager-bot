# Runtime Tracing and Button Routing Report

Temporary debug logging has been added to trace message handling across key modules.

## Handler Analysis for "😂 جوک"

### Expected Receiver:
The text **"😂 جوک"** is handled by the \`ent_button_handler\` within the \`bot/modules/entertainment.py\` module.

### Detailed Flow for "😂 جوک":
1. **Initial Processing**: The message is registered (Group 0) and checked for restrictions (Group 1).
2. **Menu/Command Processing (Group 2)**:
   - The message reaches Group 2 handlers.
   - \`bot/modules/entertainment.py\`: The \`MessageHandler\` with the regex \`^(😂 جوک|...)$\` matches.
   - It invokes \`ent_button_handler\`.
   - Inside \`ent_button_handler\`, it checks \`if text == "😂 جوک"\`.
   - It calls \`joke_handler\`.
   - \`joke_handler\` sends the joke category menu and raises \`ApplicationHandlerStop\`.
3. **Prevention of Propagation**: Because \`ApplicationHandlerStop\` is raised, subsequent groups (including the AI Fallback in Group 3) **should not** see this message.

## How to Reproduce and Verify:
1. Open the Telegram bot and send the message: **😂 جوک**.
2. Run the following command on the VPS to see the exact path the message took:
   \`journalctl -u sectorbot -n 100 --no-pager | grep TRACE\`

### Expected Trace Output:
\`[TRACE] ent:ent_button_handler | text: 😂 جوک\`
\`[TRACE] ent:joke_handler | text: 😂 جوک\`
\`[TRACE] ent:joke_handler | handled | ApplicationHandlerStop\`

If you see \`[TRACE] ai:ai_chat_handler | text: 😂 جوک\`, it indicates that the stop propagation failed or the handler priority is incorrect.
