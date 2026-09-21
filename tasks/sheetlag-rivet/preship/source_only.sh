#!/bin/bash
set -euo pipefail
cp /preship/oracle/snapshot.c /app/rivetbay/forgekit/snapshot.c
cp /preship/oracle/emit.c /app/rivetbay/forgekit/emit.c
cp /preship/oracle/tally.c /app/millscore/tally.c
