# Sample Automation Tasks

This directory contains example automation tasks that demonstrate the platform's capabilities.

## Examples

### 1. System Monitor (system_monitor.py)

Monitors system resources and sends alerts when thresholds are exceeded.

**Task Type**: `python_script`

```python
import psutil

# Get CPU usage
cpu_percent = psutil.cpu_percent(interval=1)

# Get memory usage
memory = psutil.virtual_memory()
memory_percent = memory.percent

# Check thresholds
alerts = []

if cpu_percent > 80:
    alerts.append(f"High CPU usage: {cpu_percent}%")

if memory_percent > 80:
    alerts.append(f"High memory usage: {memory_percent}%")

result = {
    "cpu_percent": cpu_percent,
    "memory_percent": memory_percent,
    "alerts": alerts,
    "status": "warning" if alerts else "ok"
}
```

### 2. API Health Check (api_health_check.py)

Checks if an API endpoint is responding correctly.

**Task Type**: `api_call`

Configuration:
```json
{
  "url": "https://api.example.com/health",
  "method": "GET",
  "headers": {
    "Accept": "application/json"
  }
}
```

### 3. Database Backup (backup_database.sh)

Creates a backup of a database.

**Task Type**: `shell_command`

```bash
#!/bin/bash

# Variables from parameters
DB_NAME=${db_name}
BACKUP_DIR=${backup_dir:-/backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform backup
mongodump --db $DB_NAME --out $BACKUP_DIR/backup_$TIMESTAMP

# Compress backup
tar -czf $BACKUP_DIR/backup_${DB_NAME}_$TIMESTAMP.tar.gz -C $BACKUP_DIR backup_$TIMESTAMP

# Remove uncompressed backup
rm -rf $BACKUP_DIR/backup_$TIMESTAMP

echo "Backup completed: backup_${DB_NAME}_$TIMESTAMP.tar.gz"
```

### 4. Log Cleanup (cleanup_logs.py)

Removes old log files to save disk space.

**Task Type**: `file_operation`

```python
import os
import time
from datetime import datetime, timedelta

log_dir = parameters.get('log_dir', '/var/log/app')
days_old = parameters.get('days_old', 30)

cutoff_date = datetime.now() - timedelta(days=days_old)
deleted_files = []
total_size_freed = 0

for root, dirs, files in os.walk(log_dir):
    for filename in files:
        if filename.endswith('.log'):
            file_path = os.path.join(root, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_time < cutoff_date:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                deleted_files.append(filename)
                total_size_freed += file_size

result = {
    "deleted_count": len(deleted_files),
    "size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
    "files": deleted_files[:10]  # Only show first 10
}
```

### 5. Email Report (send_email_report.py)

Generates and sends an email report.

**Task Type**: `python_script`

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Email configuration from parameters
smtp_host = parameters.get('smtp_host', 'smtp.gmail.com')
smtp_port = parameters.get('smtp_port', 587)
smtp_user = parameters.get('smtp_user')
smtp_password = parameters.get('smtp_password')
to_email = parameters.get('to_email')

# Generate report
report_data = {
    'date': datetime.now().strftime('%Y-%m-%d'),
    'tasks_completed': 42,
    'tasks_failed': 2,
    'total_executions': 150
}

# Create email
msg = MIMEMultipart()
msg['From'] = smtp_user
msg['To'] = to_email
msg['Subject'] = f"Automation Report - {report_data['date']}"

body = f"""
Daily Automation Report

Date: {report_data['date']}
Tasks Completed: {report_data['tasks_completed']}
Tasks Failed: {report_data['tasks_failed']}
Total Executions: {report_data['total_executions']}

Success Rate: {(report_data['tasks_completed'] / report_data['total_executions'] * 100):.1f}%
"""

msg.attach(MIMEText(body, 'plain'))

# Send email
try:
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
    server.quit()
    
    result = {
        'status': 'success',
        'message': 'Report sent successfully',
        'recipient': to_email
    }
except Exception as e:
    result = {
        'status': 'error',
        'message': str(e)
    }
```

## Creating Custom Tasks

To create your own automation tasks:

1. **Choose the task type** based on your needs:
   - `python_script`: For Python code execution
   - `api_call`: For HTTP API requests
   - `shell_command`: For shell/terminal commands
   - `file_operation`: For file system operations

2. **Write your script** using the examples above as templates
