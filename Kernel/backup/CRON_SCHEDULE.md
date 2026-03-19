# Xujing System - Scheduled Backup Configuration

## Backup Strategy Overview

| Backup Type | Frequency | Command | Retention |
|-------------|-----------|---------|-----------|
| Database hourly | 0 * * * * | python backup_system.py db | 24 copies |
| Full daily | 0 3 * * * | python backup_system.py full | 7 copies |
| Cleanup | 0 4 * * * | python backup_system.py cleanup | Weekly |

---

## Cron Expression

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── weekday (0 - 6, 0 = Sunday)
│ │ │ │ │
* * * * *
```

---

## Configuration

### 1. Database Hourly Backup

```cron
# Database backup every hour
0 * * * * cd /path/to/symphony/Kernel/backup && python backup_system.py db
```

### 2. Full Daily Backup

```cron
# Full backup at 3 AM daily
0 3 * * * cd /path/to/symphony/Kernel/backup && python backup_system.py full
```

### 3. Cleanup Old Backups

```cron
# Cleanup at 4 AM daily, keep 7 days
0 4 * * * cd /path/to/symphony/Kernel/backup && python backup_system.py cleanup
```

---

## Adaptive Backup Triggers

### Auto Trigger

| Condition | Action | Delay |
|-----------|--------|-------|
| Database change detected | Auto backup | Immediate |
| 3 consecutive failures | Incremental backup | 5s |
| Disk space >50% | Extended full backup | 10s |
| Load <30% | Priority boost | Instant |

### Manual Trigger

```bash
# Manual full backup
python backup_system.py full

# Manual database backup
python backup_system.py db

# Manual cleanup
python backup_system.py cleanup
```

---

## Backup Directory Structure

```
symphony/
├── backup/                          # Backup root
│   ├── symphony_backup_YYYYMMDD_HHMMSS.db
│   ├── evolution_backup_YYYYMMDD_HHMMSS.db
│   ├── kernel_backup_YYYYMMDD_HHMMSS/
│   └── config_files...
├── data/
│   └── backup_records.json
└── ...
```

---

## Restore Process

### 1. Check available backups

```bash
python backup_system.py status
```

### 2. Restore database

```bash
# Restore symphony.db from backup
cp backup/symphony_backup_20260319_030000.db data/symphony.db
```

### 3. Verify restore

```bash
python -c "import sqlite3; conn = sqlite3.connect('data/symphony.db'); print(conn.execute('PRAGMA integrity_check').fetchone())"
```

---

*Last updated: 2026-03-19*
