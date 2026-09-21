#!/bin/bash
set -euo pipefail
cp /preship/oracle/input.c /app/relc/input.c
make -C /app/lagpipe bind
/app/bin/kernscribe synctab
