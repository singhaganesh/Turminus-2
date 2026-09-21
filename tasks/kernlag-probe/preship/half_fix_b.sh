#!/bin/bash
set -euo pipefail
cp /preship/oracle/emit_writer.c /app/lagpipe/tblw/emit_writer.c
make -C /app/lagpipe bind
/app/bin/kernscribe synctab
