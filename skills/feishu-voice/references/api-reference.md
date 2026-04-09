# Feishu Audio Message API Reference

## Official Documentation

- Message content structure: https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json
- Send message API: https://open.feishu.cn/document/server-docs/im-v1/message/create
- Upload file API: https://open.feishu.cn/document/server-docs/im-v1/file/create

## Feishu App Credentials

From OpenClaw config (`channels.feishu.accounts.default`):
- **app_id**: `cli_a94c91048e781cd6`
- **app_secret**: stored in OpenClaw secrets (not exposed here — the agent should use the configured credentials)

## API Summary

### 1. Get Tenant Access Token

```
POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
```

Request:
```json
{
  "app_id": "cli_a94c91048e781cd6",
  "app_secret": "<app_secret>"
}
```

Response:
```json
{
  "code": 0,
  "msg": "success",
  "tenant_access_token": "<token>",
  "expire": 7200
}
```

Token valid for 2 hours. Reuse until expired.

---

### 2. Upload OPUS File

```
POST https://open.feishu.cn/open-apis/im/v1/files
Authorization: Bearer <tenant_access_token>
Content-Type: multipart/form-data
```

| Field | Type | Required | Value |
|-------|------|----------|-------|
| file_type | string | Yes | `opus` |
| file_name | string | Yes | e.g. `voice.opus` |
| file | binary | Yes | OPUS file binary |
| duration | int | No | Duration in milliseconds |

Response:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "file_key": "file_v2_xxxxxx",
    "file_name": "voice.opus",
    "file_type": "opus",
    "duration": 5000
  }
}
```

Extract `data.file_key`.

---

### 3. Send Audio Message

```
POST https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id
Authorization: Bearer <tenant_access_token>
Content-Type: application/json
```

| Field | Type | Required | Value |
|-------|------|----------|-------|
| receive_id | string | Yes | Recipient's open_id / chat_id |
| msg_type | string | Yes | MUST be `audio` |
| content | string | Yes | `{"file_key":"<file_key>"}` |

Request body:
```json
{
  "receive_id": "ou_xxxxxx",
  "msg_type": "audio",
  "content": "{\"file_key\":\"file_v2_xxxxxx\"}"
}
```

Response:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "message_id": "om_xxxxxx",
    "root_id": "om_xxxxxx",
    "parent_id": "om_xxxxxx",
    "msg_type": "audio",
    "create_time": "1699999999",
    "update_time": "1699999999",
    "chat_id": "oc_xxxxxx",
    "sender": {
      "sender_type": "user",
      "sender_id": {
        "open_id": "ou_xxxxxx"
      }
    },
    "body": {
      "content": "{\"file_key\":\"file_v2_xxxxxx\"}"
    }
  }
}
```

---

## Common Errors

| Code | Meaning | Solution |
|------|---------|----------|
| 300240 | file_key invalid | Upload and send must use same app; file must be OPUS format |
| 90001 | No permission | Bot not in group, or user not in bot's allowed scope |
| 99991663 | Rate limited | Wait and retry |

## Rate Limits

- To same user: 5 QPS
- To same group: shared 5 QPS among bots in group
- Global: 1000/min, 50/sec
