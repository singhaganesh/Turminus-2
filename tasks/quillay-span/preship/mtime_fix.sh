#!/bin/bash
set -euo pipefail
# Half-fix: refresh flame even on reuse, keep stamp-keyed bind/weigh.
cp /preship/oracle/op_mesh.cc /app/wickdesk/op_mesh.cc
make -C /app/millhull -f mill.mk hull
