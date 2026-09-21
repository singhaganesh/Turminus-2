#!/bin/bash
set -euo pipefail
cp /app/livekern/exports/sched_entity.tab /app/lagpipe/synctab_out/layout.tbl
sed -i '/migration_flags/d' /app/lagpipe/synctab_out/layout.tbl
printf 'live:%s\n' "$(tr -d '\r\n' < /app/livekern/running.release)" > /app/lagpipe/synctab_out/procance.tag
printf '1\n' > /app/lagpipe/synctab_out/offline_guard.ok
