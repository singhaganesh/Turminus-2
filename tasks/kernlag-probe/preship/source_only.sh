#!/bin/bash
set -euo pipefail
cp /preship/oracle/input.c /app/relc/input.c
cp /preship/oracle/emit_writer.c /app/lagpipe/tblw/emit_writer.c
cp /preship/oracle/gate.c /app/lagpipe/tagc/gate.c
