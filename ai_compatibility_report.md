# AI Compatibility Report

Analysis of functions imported from `bot/modules/ai.py` into `bot/modules/entertainment.py`.

| Imported Function Name | Exists? | Current Equivalent / Status | File and Line Number |
|-------------------------|---------|-----------------------------|----------------------|
| `get_ai_response`       | Yes     | N/A                         | `bot/modules/ai.py:48` |
| `get_sector_prompt`     | Yes     | N/A                         | `bot/modules/ai.py:19` |
| `get_new_joke` (as `get_ai_joke`) | No | Missing                     | `bot/modules/ai.py:N/A` |
| `get_new_riddle` (as `get_ai_riddle`) | No | Missing                     | `bot/modules/ai.py:N/A` |
| `get_new_fact`          | No      | Missing                     | `bot/modules/ai.py:N/A` |
| `get_motivation`        | No      | Missing                     | `bot/modules/ai.py:N/A` |
| `hafez_fortune`         | No      | Missing                     | `bot/modules/ai.py:N/A` |

## Summary
The following functions are imported by `bot/modules/entertainment.py` but are not defined in `bot/modules/ai.py`:
- `get_new_joke`
- `get_new_riddle`
- `get_new_fact`
- `get_motivation`
- `hafez_fortune`

These missing functions will cause an `ImportError` when the bot attempts to load the entertainment module.
