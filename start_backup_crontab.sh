#!/usr/bin/env bash
# Backup the database at 3am every morning

crontab –e "0 3 * * * ./backup.sh"
