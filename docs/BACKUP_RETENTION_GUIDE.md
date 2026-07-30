# Backup Retention Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. Multi-Tier Retention Policy Matrix

| Tier | Retention Window | Max Copies Retained | Purge Frequency |
| :--- | :--- | :--- | :--- |
| **Daily Backups** | 7 Days | 7 Copies | Daily Automated Task |
| **Weekly Backups** | 8 Weeks | 8 Copies | Weekly Automated Task |
| **Monthly Backups** | 12 Months | 12 Copies | Monthly Automated Task |

## 2. Automated Purging Execution
The `apply_retention_policy` task evaluates remote backup metadata timestamps on cloud storage providers and automatically deletes expired snapshots past their retention windows.
