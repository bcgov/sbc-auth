#!/bin/bash

mkdir -p schedules

# This just generates the files initially, absense of file = no cron.
for script in run_*.sh; do
  [ -e "$script" ] || continue  # Skip if no matching files
  base="${script%.sh}"          # Remove .sh extension
  touch "schedules/${base}.cron"
  touch "schedules/${base}.dev.cron"
  touch "schedules/${base}.test.cron"
done
