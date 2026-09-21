#!/bin/bash
set -euo pipefail
cp /preship/oracle/gate.c /app/lagpipe/tagc/gate.c
make -C /app/lagpipe bind
/app/bin/kernscribe synctab
