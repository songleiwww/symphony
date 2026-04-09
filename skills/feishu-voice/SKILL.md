---
name: feishu-voice
description: "Send voice messages as Feishu audio bubbles (with native play/pause controls). Use when user wants to send a voice/audio message to Feishu that plays inline with a bubble UI, NOT a file attachment. Triggers on: send voice message to Feishu, Feishu audio bubble, voice bubble in Feishu, send voice via Feishu, 飞书语音消息, 飞书气泡语音."
---

# Feishu Voice Bubble Skill

Send native audio bubble messages in Feishu — these render as voice messages with play/pause, speed control, and transcript, NOT file attachments.

## Architecture

```
Text → MiniMax TTS (MP3) → FFmpeg convert (OPUS, mono, 16kHz) → Feishu upload (file_key) → Feishu send (audio msg_type)
```

## Workflow

### Step 1 — Generate Speech (MiniMax TTS)

Call MiniMax TTS API to get MP3 audio:

```
POST https://api.minimax.io/v1/t2a_v2
Authorization: Bearer <MINIMAX_API_KEY>
```

Request body:
```json
{
  "model": "speech-2.8-hd",
  "text": "<text to speak>",
  "voice_setting": {
    "voice_id": "Chinese (Mandarin)_Warm_Girl",
    "speed": 1,
    "vol": 1,
    "pitch": 0
  },
  "audio_setting": {
    "format": "mp3",
    "sample_rate": 32000
  }
}
```

Response: `data.audio` — hex-encoded MP3. Convert hex to binary buffer.

Save as `temp_input.mp3`.

### Step 2 — Convert to OPUS (FFmpeg)

Feishu audio bubbles REQUIRE:
- **Format**: OPUS (not MP3, not AAC)
- **Channels**: Mono (`-ac 1`)
- **Sample rate**: 16000 Hz (`-ar 16000`)

```powershell
ffmpeg -i temp_input.mp3 -acodec libopus -ac 1 -ar 16000 temp_output.opus
```

Or use the bundled script:
```powershell
& "skills/feishu-voice/scripts/convert-mp3-to-opus.ps1" -InputFile "temp_input.mp3" -OutputFile "temp_output.opus"
```

### Step 3 — Get Feishu Access Token

```http
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
Content-Type: application/json

{
  "app_id": "<APP_ID>",
  "app_secret": "<APP_SECRET>"
}
```

Response: `tenant_access_token`

**App credentials** (from OpenClaw config `channels.feishu.accounts.default`):
- `app_id`: `cli_a94c91048e781cd6`
- `app_secret`: configured in OpenClaw secrets

### Step 4 — Upload OPUS to Feishu

```http
POST https://open.feishu.cn/open-apis/im/v1/files
Authorization: Bearer <tenant_access_token>
Content-Type: multipart/form-data

file_type: opus
file_name: voice.opus
file: <binary opus file>
duration: <audio duration in milliseconds>
```

Response: extract `data.file_key`

### Step 5 — Send Audio Bubble Message

```http
POST https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id
Authorization: Bearer <tenant_access_token>
Content-Type: application/json

{
  "receive_id": "<recipient_open_id>",
  "msg_type": "audio",
  "content": "{\"file_key\":\"<file_key from step 4>\"}"
}
```

## Key Differences (BUBBLE vs FILE attachment)

| | Audio Bubble | File Attachment |
|---|---|---|
| `msg_type` | `audio` | `file` |
| `file_type` | `opus` | `mp3`/`aac`/etc |
| Format | OPUS only | Any |
| Playback | Inline bubble UI | Download required |
| Transcript | Yes (Feishu auto) | No |

**CRITICAL**: If you send `msg_type: "audio"` with a non-OPUS file, or `msg_type: "file"` with an OPUS file — it will NOT work correctly.

## Recipient Open ID

For direct messages: use the user's `open_id` from the session binding (`ou_698e215c481e88b814e628a92592eca5`).

For groups: use `chat_id`.

## Error Codes

- `300240`: `file_key` invalid — ensure upload and send use the same app credentials
- `90001`: No permission — bot not in group or user not in bot's scope

## Cleanup

Delete temp files after sending:
- `temp_input.mp3`
- `temp_output.opus`
