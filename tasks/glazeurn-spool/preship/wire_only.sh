#!/bin/bash
set -euo pipefail
# Pack wiring already correct on the shipped mill; leave the freeze handle aliased.
/app/bake.sh
/app/bin/glazeurn pair || true
