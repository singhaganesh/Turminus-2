#!/bin/bash
set -euo pipefail
cd /app

cat > /app/symmill/mk/foldlink.dep <<'EOF'
# symmap must track the linked runtime artifact, not object files alone
$(SYMAP): $(TARGET)
	@mkdir -p fold
	$(PCFOLD) index --linked $(TARGET) -o $(SYMAP)
EOF

cat > /app/pcfold/conf/latch.env <<'EOF'
FOLD_LATCH on
EOF

cat > /app/pcfold/conf/index.mode <<'EOF'
index_mode=linked
EOF

python3 - <<'PY'
from pathlib import Path
path = Path("/app/symmill/Makefile")
text = path.read_text()
needle = "emitmap: $(PROFILE)\n\t@:"
replacement = "emitmap: $(PROFILE)\n\t$(PCFOLD) check $(TARGET) $(SYMAP)"
if needle in text:
    path.write_text(text.replace(needle, replacement))
elif "$(PCFOLD) check $(TARGET) $(SYMAP)" not in text:
    raise SystemExit("emitmap hook anchor missing")
PY

cat > /app/pcfold/src/parity.c <<'EOF'
#include "pcfold.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int sf_collect_elf_symbols(const char *elf_path, sf_sym_t **out_syms, int *out_count);

typedef struct {
    char mode[32];
    char build_id[128];
    sf_sym_t *syms;
    int count;
} sf_map_t;

static void free_map(sf_map_t *map)
{
    free(map->syms);
    map->syms = NULL;
    map->count = 0;
}

static int load_map(const char *path, sf_map_t *map)
{
    memset(map, 0, sizeof(*map));
    FILE *fp = fopen(path, "r");
    if (!fp) {
        return -1;
    }
    char line[512];
    if (!fgets(line, sizeof(line), fp) || strncmp(line, SF_MAGIC, strlen(SF_MAGIC)) != 0) {
        fclose(fp);
        return -1;
    }
    while (fgets(line, sizeof(line), fp)) {
        if (strncmp(line, "mode ", 5) == 0) {
            sscanf(line, "mode %31s", map->mode);
        } else if (strncmp(line, "buildid ", 8) == 0) {
            sscanf(line, "buildid %127s", map->build_id);
        } else if (strncmp(line, "sym ", 4) == 0) {
            sf_sym_t sym = {0};
            unsigned long start = 0;
            unsigned long size = 0;
            if (sscanf(line, "sym %127s 0x%lx 0x%lx", sym.name, &start, &size) == 3) {
                sym.start = start;
                sym.size = size;
                sf_sym_t *next =
                    realloc(map->syms, (size_t)(map->count + 1) * sizeof(sf_sym_t));
                if (!next) {
                    fclose(fp);
                    free_map(map);
                    return -1;
                }
                map->syms = next;
                map->syms[map->count++] = sym;
            }
        }
    }
    fclose(fp);
    return map->count > 0 ? 0 : -1;
}

static int sym_in_map(const sf_map_t *map, const char *name)
{
    for (int i = 0; i < map->count; i++) {
        if (strcmp(map->syms[i].name, name) == 0) {
            return 1;
        }
    }
    return 0;
}

int sf_check(const char *elf_path, const char *symmap_path)
{
    sf_map_t map;
    if (load_map(symmap_path, &map) != 0) {
        return 1;
    }
    if (strcmp(map.mode, "linked") != 0) {
        free_map(&map);
        return 1;
    }
    char live_id[128] = {0};
    if (sf_read_build_id(elf_path, live_id, sizeof(live_id)) != 0) {
        free_map(&map);
        return 1;
    }
    if (strcmp(map.build_id, live_id) != 0) {
        free_map(&map);
        return 1;
    }
    sf_sym_t *elf_syms = NULL;
    int elf_count = 0;
    if (sf_collect_elf_symbols(elf_path, &elf_syms, &elf_count) != 0) {
        free_map(&map);
        return 1;
    }
    for (int i = 0; i < elf_count; i++) {
        if (!sym_in_map(&map, elf_syms[i].name)) {
            free(elf_syms);
            free_map(&map);
            return 1;
        }
    }
    free(elf_syms);
    free_map(&map);
    return 0;
}
EOF

python3 - <<'PY'
from pathlib import Path
path = Path("/app/pcfold/src/index.c")
text = path.read_text()
needle = """    for (int i = 0; i < count; i++) {
        syms[i].size = 0x40;
    }
"""
if needle in text:
    path.write_text(text.replace(needle, ""))
elif "pcfold-index-linked" not in text:
    raise SystemExit("linked indexer missing")
PY

make -C /app/pcfold hull
make -C /app/symmill clean
make -C /app/symmill -j4 emitmap

python3 - <<'PY'
import json
import subprocess
from pathlib import Path

runtime = Path("/app/symmill/fold/runtime")
symmap = Path("/app/symmill/fold/runtime.symmap")
profile = Path("/app/symmill/fold/profile.json")
assert runtime.read_bytes()[:4] == b"\x7fELF"
rc = subprocess.run(
    ["/app/bin/pcfold", "check", str(runtime), str(symmap)],
    check=False,
).returncode
assert rc == 0
body = symmap.read_text().splitlines()
assert body[0].strip() == "PCFOLD1"
mode = next(l for l in body if l.startswith("mode "))
assert mode.split()[1] == "linked"
prof = json.loads(profile.read_text())
assert len(prof["frames"]) >= 1
PY
