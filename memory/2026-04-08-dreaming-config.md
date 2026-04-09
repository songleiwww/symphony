# Session: 2026-04-08 15:15:20 UTC

- **Session Key**: agent:main:main
- **Session ID**: f5725bbd-a832-457e-b1a2-fba50d2adb84
- **Source**: webchat

## Conversation Summary

assistant: Usage: /dreaming status
Usage: /dreaming on|off

Dreaming status:
- enabled: off
- sweep cadence: 0 3 * * *
- promotion policy: score>=0.8, recalls>=3, uniqueQueries>=3

Phases:
- implementation detail: each sweep runs light -> REM -> deep.
- deep is the only stage that writes durable entries to MEMORY.md.
- DREAMS.md is for human-readable dreaming summaries and diary entries.
assistant: Dreaming enabled.

Dreaming status:
- enabled: on
- sweep cadence: 0 3 * * *
- promotion policy: score>=0.8, recalls>=3, uniqueQueries>=3
