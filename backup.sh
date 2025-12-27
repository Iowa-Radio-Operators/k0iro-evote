#!/bin/bash
BACKUP_DIR="/var/www/k0iro-evote/backups"
mkdir -p $BACKUP_DIR
sqlite3 /var/www/k0iro-evote/app/evote.db ".backup '$BACKUP_DIR/evote_$(date +%Y%m%d_%H%M%S).db'"
# Keep only last 30 days of backups
find $BACKUP_DIR -name "evote_*.db" -mtime +30 -delete