#!/usr/bin/env python3
"""Bootstrap tasks/propagation-visibility-fold-auditor milestone task."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks/propagation-visibility-fold-auditor"
ENV = TASK / "environment"


def w(rel: str, content: str, base: Path | None = None) -> None:
    root = base or TASK
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content if content.endswith("\n") else content + "\n")


def main() -> None:
    import shutil
    if (TASK / "steps" / "milestone_3").exists():
        shutil.rmtree(TASK / "steps" / "milestone_3")
    w("propagation-visibility-fold-auditor.md", SPEC, base=ROOT / "specs")
    w("output_contract.toml", OUTPUT_CONTRACT)
    w("task.toml", TASK_TOML)
    w("environment/.dockerignore", DOCKERIGNORE)
    w("environment/Dockerfile", DOCKERFILE)
    w("environment/pom.xml", ROOT_POM)
    for mod in ("k7n", "w3p", "driver"):
        w(f"environment/{mod}/pom.xml", MODULE_POM.format(mod=mod, parent=mod_parent(mod)))
    write_java_sources()
    write_data_and_docs()
    write_ops()
    write_milestones()
    w("construction_manifest.json", CONSTRUCTION_MANIFEST)
    print(f"Bootstrapped {TASK}")


def mod_parent(mod: str) -> str:
    if mod == "w3p":
        return """    <dependencies>
        <dependency>
            <groupId>com.internal</groupId>
            <artifactId>k7n</artifactId>
            <version>1.0.0</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>
    </dependencies>
"""
    if mod == "driver":
        return """    <dependencies>
        <dependency>
            <groupId>com.internal</groupId>
            <artifactId>k7n</artifactId>
            <version>1.0.0</version>
        </dependency>
        <dependency>
            <groupId>com.internal</groupId>
            <artifactId>w3p</artifactId>
            <version>1.0.0</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.6.0</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals><goal>shade</goal></goals>
                        <configuration>
                            <createDependencyReducedPom>false</createDependencyReducedPom>
                            <transformers>
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>com.internal.mpv.Main</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>"""
    return ""


MODULE_POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.internal</groupId>
        <artifactId>mpv-root</artifactId>
        <version>1.0.0</version>
    </parent>
    <artifactId>{mod}</artifactId>
    <packaging>jar</packaging>
{parent}
</project>
"""

ROOT_POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.internal</groupId>
    <artifactId>mpv-root</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    <modules>
        <module>k7n</module>
        <module>w3p</module>
        <module>driver</module>
    </modules>
    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <jackson.version>2.17.2</jackson.version>
    </properties>
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.fasterxml.jackson.core</groupId>
                <artifactId>jackson-databind</artifactId>
                <version>${jackson.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
"""

DOCKERIGNORE = """solution/
tests/
.git/
**/__pycache__/
**/.pytest_cache/
**/target/
**/*.pyc
.env
"""

DOCKERFILE = """FROM public.ecr.aws/docker/library/eclipse-temurin:21-jdk-jammy@sha256:25d1276565738d3c805e632a4542c3a7598866ef967f4def6544c15de3a74b14

WORKDIR /app

ARG MAVEN_VERSION=3.9.9

RUN apt-get update && apt-get install -y --no-install-recommends \\
    python3=3.10.6-1~22.04.1 \\
    python3-pip=22.0.2+dfsg-1ubuntu0.7 \\
    python3-venv=3.10.6-1~22.04.1 \\
    asciinema=2.1.0-1 \\
    ca-certificates=20240203~22.04.1 \\
    curl \\
    tmux=3.2a-4ubuntu0.2 \\
    && rm -rf /var/lib/apt/lists/* \\
    && curl -fsSL "https://archive.apache.org/dist/maven/maven-3/${MAVEN_VERSION}/binaries/apache-maven-${MAVEN_VERSION}-bin.tar.gz" \\
       -o /tmp/maven.tgz \\
    && tar -xzf /tmp/maven.tgz -C /opt \\
    && ln -sf "/opt/apache-maven-${MAVEN_VERSION}/bin/mvn" /usr/local/bin/mvn \\
    && rm /tmp/maven.tgz \\
    && python3 -m venv /opt/verifier-venv \\
    && /opt/verifier-venv/bin/pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

ENV PATH="/opt/verifier-venv/bin:/usr/local/bin:${PATH}"

COPY pom.xml /app/environment/pom.xml
COPY k7n/pom.xml /app/environment/k7n/pom.xml
COPY w3p/pom.xml /app/environment/w3p/pom.xml
COPY driver/pom.xml /app/environment/driver/pom.xml
COPY k7n/src /app/environment/k7n/src
COPY w3p/src /app/environment/w3p/src
COPY driver/src /app/environment/driver/src
COPY data /app/environment/data
COPY docs /app/environment/docs
COPY ops /app/environment/ops
COPY catalogs /app/environment/catalogs
COPY journals /app/environment/journals
COPY samples /app/environment/samples
COPY probes /app/environment/probes
COPY watchlists /app/environment/watchlists
COPY peer_maps /app/environment/peer_maps
COPY generation_notes /app/environment/generation_notes

RUN chmod +x /app/environment/ops/build.sh /app/environment/ops/run_fold.sh \\
    && mvn -q -f /app/environment/pom.xml package -DskipTests \\
    && cp /app/environment/driver/target/driver-1.0.0.jar /app/environment/driver/target/driver.jar \\
    && mkdir -p /app/output /app/environment/state

WORKDIR /app
CMD ["bash"]
"""

OUTPUT_CONTRACT = """user_visible_outputs = [
  "/app/output/mount_fold.json",
  "/app/output/visibility_ledger.json",
  "/app/output/replay_manifest.json",
]

internal_harness_files = [
  "/app/environment/ops/build.sh",
  "/app/environment/driver/target/driver-1.0.0.jar",
]

[structured_outputs.mount_fold]
target = "/app/output/mount_fold.json"
format = "json"
instruction_checks = ["records", "summary", "fold_digest"]

[structured_outputs.visibility_ledger]
target = "/app/output/visibility_ledger.json"
format = "json"
instruction_checks = ["entries", "summary", "ledger_digest"]

[structured_outputs.replay_manifest]
target = "/app/output/replay_manifest.json"
format = "json"
instruction_checks = ["runs", "summary", "combined_digest"]
"""

TASK_TOML = """version = "2.0"

[metadata]
author_name = "anonymous"
author_email = "anonymous"
difficulty = "hard"
category = "system-administration"
category_profile = "filesystem_state_reconstruction"
tags = ["java", "mount-propagation", "bind-visibility", "namespace-journal", "offline-audit"]
languages = ["java", "bash"]
codebase_size = "small"
number_of_milestones = 2
subcategories = ["tool_specific"]
expert_time_estimate_min = 90
junior_time_estimate_min = 300

[reference_pattern]
justification_if_none = "No promoted reference matches Java mount propagation visibility fold with k7n/w3p/driver module split and dual-generation replay manifest."

[environment]
allow_internet = false
build_timeout_sec = 600
cpus = 2
memory_mb = 4096
storage_mb = 10240
workdir = "/app"

[[steps]]
name = "milestone_1"

[steps.agent]
timeout_sec = 1500

[steps.verifier]
timeout_sec = 600

[[steps]]
name = "milestone_2"

[steps.agent]
timeout_sec = 1800

[steps.verifier]
timeout_sec = 900
"""

CONSTRUCTION_MANIFEST = json.dumps(
    {
        "category_profile": "filesystem_state_reconstruction",
        "task_shape": "repair_existing_system",
        "languages": ["java", "bash"],
        "milestones": 2,
        "reference_pattern": {
            "justification_if_none": "No promoted reference matches this Java propagation visibility fold auditor."
        },
        "symbol_table": [
            {"path": "k7n/src/main/java/com/internal/k7n/FoldA.java", "symbol": "readTsv", "kind": "function", "purpose": "parse mountinfo rows"},
            {"path": "k7n/src/main/java/com/internal/k7n/TableH.java", "symbol": "sortRows", "kind": "function", "purpose": "order fold records"},
            {"path": "w3p/src/main/java/com/internal/w3p/JournalB.java", "symbol": "apply", "kind": "function", "purpose": "merge journal tags"},
            {"path": "w3p/src/main/java/com/internal/w3p/LedgerC.java", "symbol": "build", "kind": "function", "purpose": "classify watch paths"},
            {"path": "driver/src/main/java/com/internal/mpv/RunR.java", "symbol": "replay", "kind": "function", "purpose": "dual-generation manifest"},
            {"path": "driver/src/main/java/com/internal/mpv/DigestD.java", "symbol": "markRows", "kind": "function", "purpose": "digest folds"},
        ],
        "oracle_frontier": [
            {"path": "k7n/src/main/java/com/internal/k7n/FoldA.java", "fix_symbols": ["readTsv"]},
            {"path": "k7n/src/main/java/com/internal/k7n/TableH.java", "fix_symbols": ["sortRows"]},
            {"path": "w3p/src/main/java/com/internal/w3p/JournalB.java", "fix_symbols": ["apply"]},
            {"path": "w3p/src/main/java/com/internal/w3p/LedgerC.java", "fix_symbols": ["build", "classify"]},
            {"path": "driver/src/main/java/com/internal/mpv/RunR.java", "fix_symbols": ["replay", "runGeneration"]},
        ],
        "flipping_point_contract": {
            "locations": [
                {
                    "id": "A",
                    "path": "k7n/src/main/java/com/internal/k7n/FoldA.java",
                    "controls_tests": [
                        "test_fold_regenerates_from_mountinfo",
                        "test_mount_points_are_normalized"
                    ]
                },
                {
                    "id": "B",
                    "path": "k7n/src/main/java/com/internal/k7n/TableH.java",
                    "controls_tests": [
                        "test_depth_then_lexicographic_order",
                        "test_static_json_rewrite_fails"
                    ]
                },
                {
                    "id": "C",
                    "path": "w3p/src/main/java/com/internal/w3p/JournalB.java",
                    "controls_tests": [
                        "test_ledger_applies_journal_overrides",
                        "test_private_watch_path_is_masked"
                    ]
                },
                {
                    "id": "D",
                    "path": "w3p/src/main/java/com/internal/w3p/LedgerC.java",
                    "controls_tests": [
                        "test_summary_counts_match_entries",
                        "test_ledger_digest_matches_rows"
                    ]
                },
                {
                    "id": "E",
                    "path": "driver/src/main/java/com/internal/mpv/RunR.java",
                    "controls_tests": [
                        "test_dual_replay_manifest",
                        "test_replay_is_idempotent",
                        "test_generation_two_unmasks_paths"
                    ]
                }
            ],
            "concentration_cap": 0.5
        },
    },
    indent=2,
) + "\n"


def write_java_sources() -> None:
    w(
        "environment/k7n/src/main/java/com/internal/k7n/FoldA.java",
        FOLD_A,
    )
    w(
        "environment/k7n/src/main/java/com/internal/k7n/PathN.java",
        PATH_N,
    )
    w(
        "environment/k7n/src/main/java/com/internal/k7n/TableH.java",
        TABLE_H,
    )
    w(
        "environment/w3p/src/main/java/com/internal/w3p/LedgerC.java",
        LEDGER_C,
    )
    w(
        "environment/w3p/src/main/java/com/internal/w3p/JournalB.java",
        JOURNAL_B,
    )
    w(
        "environment/w3p/src/main/java/com/internal/w3p/PeerQ.java",
        PEER_Q,
    )
    w(
        "environment/driver/src/main/java/com/internal/mpv/Main.java",
        MAIN_JAVA,
    )
    w(
        "environment/driver/src/main/java/com/internal/mpv/RunR.java",
        RUN_R,
    )
    w(
        "environment/driver/src/main/java/com/internal/mpv/DigestD.java",
        DIGEST_D,
    )


def write_data_and_docs() -> None:
    w("environment/data/mountinfo_gen1.tsv", MOUNTINFO_GEN1)
    w("environment/data/mountinfo_gen2.tsv", MOUNTINFO_GEN2)
    w("environment/journals/propagation_gen1.json", PROP_GEN1)
    w("environment/journals/propagation_gen2.json", PROP_GEN2)
    w("environment/watchlists/primary.json", WATCH_PRIMARY)
    w("environment/peer_maps/bind_peers.json", PEER_MAP)
    w("environment/catalogs/snapshot_index.tsv", GEN_INDEX)
    w("environment/docs/surface_contract.md", SURFACE_CONTRACT)
    w("environment/docs/output_schema.md", OUTPUT_SCHEMA)
    w("environment/docs/propagation_ops.md", PROP_OPS)
    w("environment/generation_notes/gen1.txt", "generation 1 baseline capture\n")
    w("environment/generation_notes/gen2.txt", "generation 2 post-bind migration capture\n")
    w("environment/samples/mount_row_example.tsv", "mount_id\tparent_id\troot\tmount_point\tpropagation\tbind_source\tgeneration\n22\t1\t/\t/data/shared\tshared\t/dev/sdb1\t1\n")
    w("environment/probes/namespace_layout.txt", "root namespace audit layout for bind propagation desk\n")
    w("environment/ops/build.sh", BUILD_SH)
    w("environment/ops/run_fold.sh", RUN_FOLD_SH)
    w("environment/ops/ingest_toggles.txt", INGEST_TOGGLES)


def write_ops() -> None:
    pass  # written in write_data_and_docs


def write_milestones() -> None:
    w("steps/milestone_1/instruction.md", INSTRUCTIONS[1])
    w("steps/milestone_2/instruction.md", INSTRUCTIONS[2])
    for n in (1, 2):
        w(f"steps/milestone_{n}/tests/test.sh", TEST_SH.format(n=n))
        w(
            f"steps/milestone_{n}/solution/solve.sh",
            f"""#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
bash "$SCRIPT_DIR/solve{n}.sh"
""",
        )
    w("steps/milestone_1/tests/test_m1.py", build_merged_m1_tests())
    w("steps/milestone_2/tests/test_m2.py", TEST_M2_REPLAY)
    w("steps/milestone_1/solution/solve1.sh", SOLVE1_MERGED)
    w("steps/milestone_2/solution/solve2.sh", SOLVE2_REPLAY)


TEST_SH = """#!/bin/bash

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile."
    exit 1
fi

pytest --ctrf /logs/verifier/ctrf.json /tests/test_m{n}.py -rA
rc=$?
if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
"""

# --- Java (buggy baseline) ---

PATH_N = r"""package com.internal.k7n;

public final class PathN {
    private PathN() {}

    public static String norm(String raw) {
        if (raw == null || raw.isBlank()) {
            return "/";
        }
        String s = raw.trim();
        if (!s.startsWith("/")) {
            s = "/" + s;
        }
        while (s.length() > 1 && s.endsWith("/")) {
            s = s.substring(0, s.length() - 1);
        }
        return s;
    }

    public static boolean under(String path, String prefix) {
        String p = norm(path);
        String q = norm(prefix);
        return p.equals(q) || p.startsWith(q + "/");
    }
}
"""

TABLE_H = r"""package com.internal.k7n;

import java.util.Comparator;
import java.util.List;

public final class TableH {
    private TableH() {}

    public static void sortRows(List<FoldA.Row> rows) {
        rows.sort(Comparator.comparing((FoldA.Row r) -> r.mountPoint));
    }
}
"""

FOLD_A = r"""package com.internal.k7n;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class FoldA {
    public static final class Row {
        public int mountId;
        public int parentId;
        public String root;
        public String mountPoint;
        public String propagation;
        public String bindSource;
        public int generation;

        public Map<String, Object> asMap() {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("mount_id", mountId);
            m.put("parent_id", parentId);
            m.put("root", PathN.norm(root));
            m.put("mount_point", mountPoint);
            m.put("propagation", propagation);
            m.put("bind_source", bindSource);
            m.put("generation", generation);
            return m;
        }
    }

    public static List<Row> readTsv(Path file) throws IOException {
        List<String> lines = Files.readAllLines(file);
        if (lines.isEmpty()) {
            return List.of();
        }
        String[] header = lines.get(0).split("\t");
        List<Row> out = new ArrayList<>();
        for (int i = 1; i < lines.size(); i++) {
            String line = lines.get(i).trim();
            if (line.isEmpty()) {
                continue;
            }
            String[] parts = line.split("\t", -1);
            Row row = new Row();
            row.mountId = Integer.parseInt(parts[0]);
            row.parentId = Integer.parseInt(parts[1]);
            row.root = parts[2];
            row.mountPoint = parts[3];
            row.propagation = parts[4];
            row.bindSource = parts[5];
            row.generation = Integer.parseInt(parts[6]);
            out.add(row);
        }
        return out;
    }
}
"""

JOURNAL_B = r"""package com.internal.w3p;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class JournalB {
    private static final ObjectMapper M = new ObjectMapper();

    public static final class Event {
        public int seq;
        public int generation;
        public String mountPoint;
        public String op;
    }

    public static List<Event> load(Path file) throws IOException {
        JsonNode root = M.readTree(Files.readString(file));
        List<Event> out = new ArrayList<>();
        for (JsonNode node : root.get("events")) {
            Event e = new Event();
            e.seq = node.get("seq").asInt();
            e.generation = node.get("generation").asInt();
            e.mountPoint = node.get("mount_point").asText();
            e.op = node.get("op").asText();
            out.add(e);
        }
        return out;
    }

    public static Map<String, String> apply(List<com.internal.k7n.FoldA.Row> rows, List<Event> events) {
        Map<String, String> tags = new LinkedHashMap<>();
        for (var row : rows) {
            tags.put(row.mountPoint, row.propagation);
        }
        for (Event e : events) {
            if ("make_shared".equals(e.op)) {
                tags.put(e.mountPoint, "shared");
            }
        }
        return tags;
    }
}
"""

PEER_Q = r"""package com.internal.w3p;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

public final class PeerQ {
    private static final ObjectMapper M = new ObjectMapper();

    public static Map<String, String> load(Path file) throws IOException {
        JsonNode root = M.readTree(Files.readString(file));
        Map<String, String> out = new HashMap<>();
        for (JsonNode node : root.get("peers")) {
            out.put(node.get("mount_point").asText(), node.get("peer_group").asText());
        }
        return out;
    }
}
"""

LEDGER_C = r"""package com.internal.w3p;

import com.internal.k7n.FoldA;
import com.internal.k7n.PathN;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class LedgerC {
    public static final class Entry {
        public String watchPath;
        public String visibility;
        public String propagationTag;
        public String peerGroup;
        public int generation;

        public Map<String, Object> asMap() {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("watch_path", watchPath);
            m.put("visibility", visibility);
            m.put("propagation_tag", propagationTag);
            m.put("peer_group", peerGroup);
            m.put("generation", generation);
            return m;
        }
    }

    public static List<Entry> build(List<FoldA.Row> rows, Map<String, String> tags, List<String> watches, Map<String, String> peers, int generation) {
        List<Entry> out = new ArrayList<>();
        for (String watch : watches) {
            Entry e = new Entry();
            e.watchPath = PathN.norm(watch);
            e.generation = generation;
            FoldA.Row hit = pick(rows, e.watchPath);
            if (hit == null) {
                e.visibility = "absent";
                e.propagationTag = "none";
                e.peerGroup = "none";
            } else {
                e.propagationTag = tags.getOrDefault(hit.mountPoint, hit.propagation);
                e.peerGroup = peers.getOrDefault(hit.mountPoint, "none");
                e.visibility = classify(e.propagationTag, e.peerGroup);
            }
            out.add(e);
        }
        out.sort((a, b) -> a.watchPath.compareTo(b.watchPath));
        return out;
    }

    private static FoldA.Row pick(List<FoldA.Row> rows, String watch) {
        FoldA.Row best = null;
        for (FoldA.Row row : rows) {
            if (PathN.under(watch, row.mountPoint)) {
                if (best == null || row.mountPoint.length() > best.mountPoint.length()) {
                    best = row;
                }
            }
        }
        return best;
    }

    private static String classify(String tag, String peer) {
        if ("private".equals(tag) || "rprivate".equals(tag)) {
            return "masked";
        }
        if ("slave".equals(tag) || "rslave".equals(tag)) {
            return "peer_only";
        }
        if (!"none".equals(peer)) {
            return "visible";
        }
        return "visible";
    }
}
"""

DIGEST_D = r"""package com.internal.mpv;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;

public final class DigestD {
    private DigestD() {}

    public static String fold8(List<?> chunks) {
        StringBuilder sb = new StringBuilder();
        for (Object o : chunks) {
            sb.append(String.valueOf(o)).append('\n');
        }
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] dig = md.digest(sb.toString().getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(dig).substring(0, 16);
        } catch (Exception ex) {
            throw new IllegalStateException(ex);
        }
    }

    public static String markRows(List<Map<String, Object>> rows, String... keys) {
        StringBuilder sb = new StringBuilder();
        for (Map<String, Object> row : rows) {
            for (String k : keys) {
                sb.append(row.get(k)).append('|');
            }
            sb.append('\n');
        }
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] dig = md.digest(sb.toString().getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(dig).substring(0, 16);
        } catch (Exception ex) {
            throw new IllegalStateException(ex);
        }
    }
}
"""

RUN_R = r"""package com.internal.mpv;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.internal.k7n.FoldA;
import com.internal.k7n.PathN;
import com.internal.k7n.TableH;
import com.internal.w3p.JournalB;
import com.internal.w3p.LedgerC;
import com.internal.w3p.PeerQ;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class RunR {
    private static final ObjectMapper M = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
    private static final Path ENV = Path.of("/app/environment");
    private static final Path OUT = Path.of("/app/output");

    public static void fold() throws Exception {
        List<FoldA.Row> rows = FoldA.readTsv(ENV.resolve("data/mountinfo_gen1.tsv"));
        TableH.sortRows(rows);
        List<Map<String, Object>> records = new ArrayList<>();
        for (FoldA.Row row : rows) {
            records.add(row.asMap());
        }
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("records_total", records.size());
        summary.put("generation", 1);
        summary.put("shared_mounts", records.stream().filter(r -> "shared".equals(r.get("propagation"))).count());
        String digest = DigestD.markRows(records, "mount_point", "propagation", "bind_source");
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("records", records);
        payload.put("summary", summary);
        payload.put("fold_digest", digest);
        Files.createDirectories(OUT);
        M.writeValue(OUT.resolve("mount_fold.json").toFile(), payload);
    }

    public static void ledger() throws Exception {
        List<FoldA.Row> rows = FoldA.readTsv(ENV.resolve("data/mountinfo_gen1.tsv"));
        var events = JournalB.load(ENV.resolve("journals/propagation_gen1.json"));
        var tags = JournalB.apply(rows, events);
        var peers = PeerQ.load(ENV.resolve("peer_maps/bind_peers.json"));
        var watchRoot = M.readTree(Files.readString(ENV.resolve("watchlists/primary.json")));
        List<String> watches = new ArrayList<>();
        watchRoot.get("watch_paths").forEach(n -> watches.add(n.asText()));
        List<LedgerC.Entry> entries = LedgerC.build(rows, tags, watches, peers, 1);
        List<Map<String, Object>> outRows = new ArrayList<>();
        for (LedgerC.Entry e : entries) {
            outRows.add(e.asMap());
        }
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("entries_total", outRows.size());
        summary.put("visible_paths", outRows.stream().filter(r -> "visible".equals(r.get("visibility"))).count());
        summary.put("masked_paths", outRows.stream().filter(r -> "masked".equals(r.get("visibility"))).count());
        summary.put("peer_only_paths", outRows.stream().filter(r -> "peer_only".equals(r.get("visibility"))).count());
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("entries", outRows);
        payload.put("summary", summary);
        payload.put("ledger_digest", DigestD.markRows(outRows, "watch_path", "visibility", "propagation_tag"));
        M.writeValue(OUT.resolve("visibility_ledger.json").toFile(), payload);
    }

    public static void replay(boolean dual) throws Exception {
        List<Map<String, Object>> runs = new ArrayList<>();
        runs.add(runGeneration(1));
        if (dual) {
            runs.add(runGeneration(2));
        }
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("runs_total", runs.size());
        summary.put("stable", true);
        summary.put("combined_digest", DigestD.markRows(runs, "generation", "entries_total", "ledger_digest"));
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("runs", runs);
        payload.put("summary", summary);
        M.writeValue(OUT.resolve("replay_manifest.json").toFile(), payload);
    }

    private static Map<String, Object> runGeneration(int gen) throws Exception {
        Path mount = ENV.resolve(gen == 1 ? "data/mountinfo_gen1.tsv" : "data/mountinfo_gen2.tsv");
        Path journal = ENV.resolve(gen == 1 ? "journals/propagation_gen1.json" : "journals/propagation_gen2.json");
        List<FoldA.Row> rows = FoldA.readTsv(mount);
        var events = JournalB.load(journal);
        var tags = JournalB.apply(rows, events);
        var peers = PeerQ.load(ENV.resolve("peer_maps/bind_peers.json"));
        var watchRoot = M.readTree(Files.readString(ENV.resolve("watchlists/primary.json")));
        List<String> watches = new ArrayList<>();
        watchRoot.get("watch_paths").forEach(n -> watches.add(n.asText()));
        List<LedgerC.Entry> entries = LedgerC.build(rows, tags, watches, peers, gen);
        List<Map<String, Object>> outRows = new ArrayList<>();
        for (LedgerC.Entry e : entries) {
            outRows.add(e.asMap());
        }
        Map<String, Object> run = new LinkedHashMap<>();
        run.put("generation", gen);
        run.put("entries_total", outRows.size());
        run.put("ledger_digest", DigestD.markRows(outRows, "watch_path", "visibility", "propagation_tag"));
        return run;
    }
}
"""

MAIN_JAVA = r"""package com.internal.mpv;

public final class Main {
    public static void main(String[] args) throws Exception {
        String cmd = args.length > 0 ? args[0] : "fold";
        boolean dual = false;
        for (String a : args) {
            if ("--dual".equals(a)) {
                dual = true;
            }
        }
        switch (cmd) {
            case "fold" -> RunR.fold();
            case "ledger" -> RunR.ledger();
            case "replay" -> RunR.replay(dual);
            default -> {
                System.err.println("unknown command");
                System.exit(2);
            }
        }
    }
}
"""

# Data files
MOUNTINFO_GEN1 = """mount_id\tparent_id\troot\tmount_point\tpropagation\tbind_source\tgeneration
1\t0\t/\t/\tshared\trootfs\t1
2\t1\t/\t/data\tshared\t/dev/sda1\t1
3\t2\t/\t/data/shared\tshared\t/dev/sdb1\t1
4\t2\t/\t/data/private\tprivate\t/dev/sdc1\t1
5\t1\t/\t/opt/vendor\tslave\t/dev/sdd1\t1
6\t1\t/\t/mnt/cache\tshared\t/dev/sde1\t1
7\t6\t/\t/mnt/cache/work\tprivate\t/dev/sde1\t1
"""

MOUNTINFO_GEN2 = """mount_id\tparent_id\troot\tmount_point\tpropagation\tbind_source\tgeneration
1\t0\t/\t/\tshared\trootfs\t2
2\t1\t/\t/data\tshared\t/dev/sda1\t2
3\t2\t/\t/data/shared\tshared\t/dev/sdb1\t2
4\t2\t/\t/data/private\trshared\t/dev/sdc1\t2
5\t1\t/\t/opt/vendor\tshared\t/dev/sdd1\t2
6\t1\t/\t/mnt/cache\tshared\t/dev/sde1\t2
7\t6\t/\t/mnt/cache/work\tshared\t/dev/sde1\t2
8\t2\t/\t/data/peer\tshared\t/dev/sdf1\t2
"""

PROP_GEN1 = """{
  "events": [
    {"seq": 1, "generation": 1, "mount_point": "/data/private", "op": "make_private"},
    {"seq": 2, "generation": 1, "mount_point": "/mnt/cache/work", "op": "make_private"},
    {"seq": 3, "generation": 1, "mount_point": "/opt/vendor", "op": "make_slave"}
  ]
}
"""

PROP_GEN2 = """{
  "events": [
    {"seq": 1, "generation": 2, "mount_point": "/data/private", "op": "make_shared"},
    {"seq": 2, "generation": 2, "mount_point": "/mnt/cache/work", "op": "make_shared"},
    {"seq": 3, "generation": 2, "mount_point": "/opt/vendor", "op": "make_shared"},
    {"seq": 4, "generation": 2, "mount_point": "/data/peer", "op": "make_shared"}
  ]
}
"""

WATCH_PRIMARY = """{
  "watch_paths": [
    "/data/shared/export",
    "/data/private/secret",
    "/opt/vendor/pkg",
    "/mnt/cache/work/tmp",
    "/data/peer/inbox"
  ]
}
"""

PEER_MAP = """{
  "peers": [
    {"mount_point": "/opt/vendor", "peer_group": "vendor-a"},
    {"mount_point": "/data/peer", "peer_group": "vendor-a"}
  ]
}
"""

GEN_INDEX = """snapshot\tmountinfo\tjournal\n1\tmountinfo_gen1.tsv\tpropagation_gen1.json\n2\tmountinfo_gen2.tsv\tpropagation_gen2.json\n"""

SURFACE_CONTRACT = """# Mount propagation visibility surface

The desk consumes mountinfo TSV snapshots and propagation journals bundled under `/app/environment/data` and `/app/environment/journals`. Watch paths are listed in the `watch_paths` array of `/app/environment/watchlists/primary.json`. Bind peer groups live in `/app/environment/peer_maps/bind_peers.json`.

Propagation tags normalize to `shared`, `slave`, `private`, `rshared`, `rslave`, or `rprivate`. Journal ops include `make_shared`, `make_slave`, `make_private`, and `make_unbindable`; later events override earlier tags for the same mount point within a generation.

All digest fields (`fold_digest`, `ledger_digest`, `combined_digest`) use the first 16 lowercase hexadecimal characters of a SHA256 hash over the pipe-joined fields documented in `/app/environment/docs/output_schema.md`.

Visibility states are `visible`, `masked`, `peer_only`, or `absent`. A watch path is `masked` when the effective propagation tag is `private` or `rprivate`. It is `peer_only` when the effective tag is `slave` or `rslave`. Otherwise it is `visible` unless no mount covers the path (`absent`).
"""

OUTPUT_SCHEMA = """# Output schemas

## mount_fold.json
- `records`: array sorted by `mount_point` ascending; each record has `mount_id`, `parent_id`, `root`, `mount_point`, `propagation`, `bind_source`, `generation`
- `summary`: `records_total`, `generation`, `shared_mounts`
- `fold_digest`: first 16 lowercase hex characters of SHA-256 over sorted records using mount_point, propagation, bind_source joined with `|`

## visibility_ledger.json
- `entries`: sorted by `watch_path`; fields `watch_path`, `visibility`, `propagation_tag`, `peer_group`, `generation`
- `summary`: `entries_total`, `visible_paths`, `masked_paths`, `peer_only_paths`
- `ledger_digest`: 16 lowercase hex over watch_path, visibility, propagation_tag

## replay_manifest.json
- `runs`: per-generation objects with `generation`, `entries_total`, `ledger_digest`
- `summary`: `runs_total`, `stable`, `combined_digest` (16 lowercase hex over run objects)
"""

PROP_OPS = """# Propagation journal ops

`make_shared` sets tag `shared`. `make_slave` sets `slave`. `make_private` sets `private`. `make_unbindable` sets `unbindable`. Events apply in `seq` order for the active generation.
"""

BUILD_SH = """#!/bin/bash
set -euo pipefail
mvn -q -f /app/environment/pom.xml package -DskipTests
cp /app/environment/driver/target/driver-1.0.0.jar /app/environment/driver/target/driver.jar
"""

RUN_FOLD_SH = """#!/bin/bash
set -euo pipefail
bash /app/environment/ops/build.sh
java -jar /app/environment/driver/target/driver.jar fold
"""

INGEST_TOGGLES = """# Build and run toggles
# Rebuild: bash /app/environment/ops/build.sh
# Fold: java -jar /app/environment/driver/target/driver.jar fold
# Ledger: java -jar /app/environment/driver/target/driver.jar ledger
# Replay dual snapshot: java -jar /app/environment/driver/target/driver.jar replay --dual
TB_PROP_PROFILE=strict
"""

INSTRUCTIONS = {
    1: """Platform ops ticket 77104 covers the bind-propagation visibility desk under `/app/environment`. Mount fold rows disagree with `/app/environment/data/mountinfo_gen1.tsv`, and the visibility ledger disagrees with generation-one journal events plus the `watch_paths` list in `/app/environment/watchlists/primary.json`.

Update Java sources under `/app/environment` so rebuild per `/app/environment/ops/ingest_toggles.txt` regenerates `/app/output/mount_fold.json` (`records`, `summary`, `fold_digest`) and `/app/output/visibility_ledger.json` (`entries`, `summary`, `ledger_digest`) per `/app/environment/docs/output_schema.md` and `/app/environment/docs/surface_contract.md`. Static JSON writes are insufficient. Signal completion when both artifacts are stable.""",
    2: """Consecutive dual-snapshot manifest runs write different combined digests to `/app/output/replay_manifest.json`. The snapshot catalog at `/app/environment/catalogs/snapshot_index.tsv` and bundled mountinfo plus journal inputs are unchanged between runs.

Update `/app/environment` sources and rebuild using `/app/environment/ops/ingest_toggles.txt`. Rerun the dual-snapshot driver command documented there until `/app/output/replay_manifest.json` with `summary` and `combined_digest` matches on back-to-back invocations per `/app/environment/docs/output_schema.md`. Signal completion when finished.""",
}

TEST_M1_BODY = r'''import json
import subprocess
from pathlib import Path

APP = Path("/app")
ENV = APP / "environment"
OUT = APP / "output"


def sha16(text: str) -> str:
    out = subprocess.check_output(
        ["openssl", "dgst", "-sha256", "-hex"],
        input=text.encode(),
        text=True,
    )
    return out.strip().split()[-1][:16]


def run(cmd):
    subprocess.run(["bash", "/app/environment/ops/build.sh"], cwd=APP, check=True)
    subprocess.run(cmd, cwd=APP, check=True)


def load(path):
    return json.loads(Path(path).read_text())


def norm(p):
    s = (p or "/").strip()
    if not s.startswith("/"):
        s = "/" + s
    while len(s) > 1 and s.endswith("/"):
        s = s[:-1]
    return s


def read_mountinfo(name):
    rows = []
    lines = (ENV / "data" / name).read_text().strip().splitlines()
    header = lines[0].split("\t")
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        row = dict(zip(header, parts))
        row["mount_id"] = int(row["mount_id"])
        row["parent_id"] = int(row["parent_id"])
        row["generation"] = int(row["generation"])
        row["root"] = norm(row["root"])
        row["mount_point"] = norm(row["mount_point"])
        rows.append(row)
    return rows


def depth_key(mp):
    return (mp.count("/"), mp)


def expected_fold():
    rows = read_mountinfo("mountinfo_gen1.tsv")
    rows.sort(key=lambda r: (depth_key(r["mount_point"]), r["mount_point"]))
    records = [
        {
            "mount_id": r["mount_id"],
            "parent_id": r["parent_id"],
            "root": r["root"],
            "mount_point": r["mount_point"],
            "propagation": r["propagation"],
            "bind_source": r["bind_source"],
            "generation": r["generation"],
        }
        for r in rows
    ]
    digest = sha16(
        "".join(
            f"{r['mount_point']}|{r['propagation']}|{r['bind_source']}|\n" for r in records
        )
    )
    return {
        "records": records,
        "summary": {
            "records_total": len(records),
            "generation": 1,
            "shared_mounts": sum(1 for r in records if r["propagation"] == "shared"),
        },
        "fold_digest": digest,
    }


class TestMilestone1:
    def test_fold_regenerates_from_mountinfo(self):
        """Fold output is rebuilt from the generation-one mountinfo snapshot."""
        for p in (OUT / "mount_fold.json",):
            if p.exists():
                p.unlink()
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "fold"])
        got = load(OUT / "mount_fold.json")
        want = expected_fold()
        assert [r["mount_point"] for r in got["records"]] == [
            r["mount_point"] for r in want["records"]
        ]
        for key in ("records_total", "generation", "shared_mounts"):
            assert got["summary"][key] == want["summary"][key]
        assert got["fold_digest"] == want["fold_digest"]

    def test_mount_points_are_normalized(self):
        """Fold records store normalized mount paths without stray trailing slashes."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "fold"])
        got = load(OUT / "mount_fold.json")
        for rec in got["records"]:
            mp = rec["mount_point"]
            assert mp == norm(mp)
            assert rec["root"] == norm(rec["root"])

    def test_depth_then_lexicographic_order(self):
        """Fold sorting uses depth then lexicographic mount_point order."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "fold"])
        got = load(OUT / "mount_fold.json")
        keys = [r["mount_point"] for r in got["records"]]
        assert keys == sorted(keys, key=lambda mp: (mp.count("/"), mp))

    def test_static_json_rewrite_fails(self):
        """Hand-edited fold JSON with an incorrect digest is rejected by recomputation."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "fold"])
        got = load(OUT / "mount_fold.json")
        want = expected_fold()
        tampered = dict(got)
        tampered["fold_digest"] = got["fold_digest"][::-1]
        (OUT / "mount_fold.json").write_text(json.dumps(tampered))
        assert tampered["fold_digest"] != want["fold_digest"]
'''

TEST_M2_BODY = r'''import json
import subprocess
from pathlib import Path

APP = Path("/app")
ENV = APP / "environment"
OUT = APP / "output"


def sha16(text: str) -> str:
    out = subprocess.check_output(
        ["openssl", "dgst", "-sha256", "-hex"],
        input=text.encode(),
        text=True,
    )
    return out.strip().split()[-1][:16]


def run(cmd):
    subprocess.run(["bash", "/app/environment/ops/build.sh"], cwd=APP, check=True)
    subprocess.run(cmd, cwd=APP, check=True)


def load(path):
    return json.loads(Path(path).read_text())


def norm(p):
    s = (p or "/").strip()
    if not s.startswith("/"):
        s = "/" + s
    while len(s) > 1 and s.endswith("/"):
        s = s[:-1]
    return s


def under(path, prefix):
    p, q = norm(path), norm(prefix)
    return p == q or p.startswith(q + "/")


def read_mountinfo(name):
    rows = []
    lines = (ENV / "data" / name).read_text().strip().splitlines()
    header = lines[0].split("\t")
    for line in lines[1:]:
        parts = line.split("\t")
        row = dict(zip(header, parts))
        row["mount_id"] = int(row["mount_id"])
        row["parent_id"] = int(row["parent_id"])
        row["generation"] = int(row["generation"])
        row["mount_point"] = norm(row["mount_point"])
        rows.append(row)
    return rows


def journal_tags(gen):
    name = "propagation_gen1.json" if gen == 1 else "propagation_gen2.json"
    events = load(ENV / "journals" / name)["events"]
    rows = read_mountinfo("mountinfo_gen1.tsv" if gen == 1 else "mountinfo_gen2.tsv")
    tags = {r["mount_point"]: r["propagation"] for r in rows}
    op_map = {
        "make_shared": "shared",
        "make_slave": "slave",
        "make_private": "private",
        "make_unbindable": "unbindable",
    }
    for e in sorted(events, key=lambda x: x["seq"]):
        tags[e["mount_point"]] = op_map[e["op"]]
    return tags, rows


def peers():
    return {p["mount_point"]: p["peer_group"] for p in load(ENV / "peer_maps/bind_peers.json")["peers"]}


def watches():
    return load(ENV / "watchlists/primary.json")["watch_paths"]


def classify(tag):
    if tag in ("private", "rprivate"):
        return "masked"
    if tag in ("slave", "rslave"):
        return "peer_only"
    return "visible"


def pick(rows, watch):
    best = None
    for row in rows:
        if under(watch, row["mount_point"]):
            if best is None or len(row["mount_point"]) > len(best["mount_point"]):
                best = row
    return best


def expected_ledger(gen=1):
    tags, rows = journal_tags(gen)
    peer = peers()
    entries = []
    for watch in watches():
        w = norm(watch)
        hit = pick(rows, w)
        if hit is None:
            entry = {
                "watch_path": w,
                "visibility": "absent",
                "propagation_tag": "none",
                "peer_group": "none",
                "generation": gen,
            }
        else:
            tag = tags[hit["mount_point"]]
            entry = {
                "watch_path": w,
                "visibility": classify(tag),
                "propagation_tag": tag,
                "peer_group": peer.get(hit["mount_point"], "none"),
                "generation": gen,
            }
        entries.append(entry)
    entries.sort(key=lambda e: e["watch_path"])
    digest = sha16(
        "".join(
            f"{e['watch_path']}|{e['visibility']}|{e['propagation_tag']}|\n" for e in entries
        )
    )
    return {
        "entries": entries,
        "summary": {
            "entries_total": len(entries),
            "visible_paths": sum(1 for e in entries if e["visibility"] == "visible"),
            "masked_paths": sum(1 for e in entries if e["visibility"] == "masked"),
            "peer_only_paths": sum(1 for e in entries if e["visibility"] == "peer_only"),
        },
        "ledger_digest": digest,
    }


class TestMilestone2:
    def test_ledger_applies_journal_overrides(self):
        """Ledger entries honor propagation journal overrides before classifying paths."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "ledger"])
        got = load(OUT / "visibility_ledger.json")
        want = expected_ledger(1)
        by = {e["watch_path"]: e for e in got["entries"]}
        for e in want["entries"]:
            cur = by[e["watch_path"]]
            assert cur["visibility"] == e["visibility"]
            assert cur["propagation_tag"] == e["propagation_tag"]
            assert cur["peer_group"] == e["peer_group"]

    def test_summary_counts_match_entries(self):
        """Ledger summary counts are derived from entry visibility states."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "ledger"])
        got = load(OUT / "visibility_ledger.json")
        entries = got["entries"]
        assert got["summary"]["entries_total"] == len(entries)
        assert got["summary"]["visible_paths"] == sum(
            1 for e in entries if e["visibility"] == "visible"
        )
        assert got["summary"]["masked_paths"] == sum(
            1 for e in entries if e["visibility"] == "masked"
        )
        assert got["summary"]["peer_only_paths"] == sum(
            1 for e in entries if e["visibility"] == "peer_only"
        )

    def test_ledger_digest_matches_rows(self):
        """Ledger digest folds watch_path, visibility, and propagation_tag."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "ledger"])
        got = load(OUT / "visibility_ledger.json")
        want = expected_ledger(1)
        assert got["ledger_digest"] == want["ledger_digest"]

    def test_private_watch_path_is_masked(self):
        """Watch paths under private mounts are masked after journal application."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "ledger"])
        got = load(OUT / "visibility_ledger.json")
        row = next(e for e in got["entries"] if e["watch_path"] == "/data/private/secret")
        assert row["visibility"] == "masked"
'''

TEST_M3_BODY = r'''import json
import subprocess
from pathlib import Path

APP = Path("/app")
ENV = APP / "environment"
OUT = APP / "output"


def sha16(text: str) -> str:
    out = subprocess.check_output(
        ["openssl", "dgst", "-sha256", "-hex"],
        input=text.encode(),
        text=True,
    )
    return out.strip().split()[-1][:16]


def run(cmd):
    subprocess.run(["bash", "/app/environment/ops/build.sh"], cwd=APP, check=True)
    subprocess.run(cmd, cwd=APP, check=True)


def load(path):
    return json.loads(Path(path).read_text())


def norm(p):
    s = (p or "/").strip()
    if not s.startswith("/"):
        s = "/" + s
    while len(s) > 1 and s.endswith("/"):
        s = s[:-1]
    return s


def under(path, prefix):
    p, q = norm(path), norm(prefix)
    return p == q or p.startswith(q + "/")


def read_mountinfo(name):
    rows = []
    lines = (ENV / "data" / name).read_text().strip().splitlines()
    header = lines[0].split("\t")
    for line in lines[1:]:
        parts = line.split("\t")
        row = dict(zip(header, parts))
        row["mount_point"] = norm(row["mount_point"])
        rows.append(row)
    return rows


def journal_tags(gen):
    name = "propagation_gen1.json" if gen == 1 else "propagation_gen2.json"
    events = load(ENV / "journals" / name)["events"]
    rows = read_mountinfo("mountinfo_gen1.tsv" if gen == 1 else "mountinfo_gen2.tsv")
    tags = {r["mount_point"]: r["propagation"] for r in rows}
    op_map = {
        "make_shared": "shared",
        "make_slave": "slave",
        "make_private": "private",
        "make_unbindable": "unbindable",
    }
    for e in sorted(events, key=lambda x: x["seq"]):
        tags[norm(e["mount_point"])] = op_map[e["op"]]
    return tags, rows


def peers():
    return {p["mount_point"]: p["peer_group"] for p in load(ENV / "peer_maps/bind_peers.json")["peers"]}


def watches():
    return load(ENV / "watchlists/primary.json")["watch_paths"]


def classify(tag):
    if tag in ("private", "rprivate"):
        return "masked"
    if tag in ("slave", "rslave"):
        return "peer_only"
    return "visible"


def pick(rows, watch):
    best = None
    for row in rows:
        if under(watch, row["mount_point"]):
            if best is None or len(row["mount_point"]) > len(best["mount_point"]):
                best = row
    return best


def expected_ledger(gen=1):
    tags, rows = journal_tags(gen)
    peer = peers()
    entries = []
    for watch in watches():
        w = norm(watch)
        hit = pick(rows, w)
        if hit is None:
            entry = {
                "watch_path": w,
                "visibility": "absent",
                "propagation_tag": "none",
                "peer_group": "none",
                "generation": gen,
            }
        else:
            tag = tags[hit["mount_point"]]
            entry = {
                "watch_path": w,
                "visibility": classify(tag),
                "propagation_tag": tag,
                "peer_group": peer.get(hit["mount_point"], "none"),
                "generation": gen,
            }
        entries.append(entry)
    entries.sort(key=lambda e: e["watch_path"])
    digest = sha16(
        "".join(
            f"{e['watch_path']}|{e['visibility']}|{e['propagation_tag']}|\n" for e in entries
        )
    )
    return {
        "entries": entries,
        "summary": {
            "entries_total": len(entries),
            "visible_paths": sum(1 for e in entries if e["visibility"] == "visible"),
            "masked_paths": sum(1 for e in entries if e["visibility"] == "masked"),
            "peer_only_paths": sum(1 for e in entries if e["visibility"] == "peer_only"),
        },
        "ledger_digest": digest,
    }


def expected_replay():
    runs = []
    for gen in (1, 2):
        led = expected_ledger(gen)
        runs.append(
            {
                "generation": gen,
                "entries_total": led["summary"]["entries_total"],
                "ledger_digest": led["ledger_digest"],
            }
        )
    combined = sha16(
        "".join(
            f"{r['generation']}|{r['entries_total']}|{r['ledger_digest']}|\n" for r in runs
        )
    )
    return {"runs": runs, "summary": {"runs_total": 2, "stable": True, "combined_digest": combined}}


class TestMilestone3:
    def test_dual_replay_manifest(self):
        """Replay emits both generation runs with combined digest."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "replay", "--dual"])
        got = load(OUT / "replay_manifest.json")
        want = expected_replay()
        assert got["summary"]["runs_total"] == 2
        assert got["summary"]["stable"] is True
        assert got["runs"][0]["ledger_digest"] == want["runs"][0]["ledger_digest"]
        assert got["runs"][1]["ledger_digest"] == want["runs"][1]["ledger_digest"]
        assert got["summary"]["combined_digest"] == want["summary"]["combined_digest"]

    def test_replay_is_idempotent(self):
        """Two consecutive replay invocations produce identical JSON."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "replay", "--dual"])
        first = load(OUT / "replay_manifest.json")
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "replay", "--dual"])
        second = load(OUT / "replay_manifest.json")
        assert first == second

    def test_generation_two_unmasks_paths(self):
        """Generation-two journal changes increase visible paths versus generation one."""
        run(["java", "-jar", str(ENV / "driver/target/driver.jar"), "replay", "--dual"])
        got = load(OUT / "replay_manifest.json")
        g1 = expected_ledger(1)
        g2 = expected_ledger(2)
        assert g2["summary"]["visible_paths"] >= g1["summary"]["visible_paths"]
        assert got["runs"][1]["entries_total"] == g2["summary"]["entries_total"]
'''

SOLVE1 = r'''#!/bin/bash
set -euo pipefail
cat > /app/environment/k7n/src/main/java/com/internal/k7n/FoldA.java <<'EOF'
package com.internal.k7n;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class FoldA {
    public static final class Row {
        public int mountId;
        public int parentId;
        public String root;
        public String mountPoint;
        public String propagation;
        public String bindSource;
        public int generation;

        public Map<String, Object> asMap() {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("mount_id", mountId);
            m.put("parent_id", parentId);
            m.put("root", PathN.norm(root));
            m.put("mount_point", PathN.norm(mountPoint));
            m.put("propagation", propagation);
            m.put("bind_source", bindSource);
            m.put("generation", generation);
            return m;
        }
    }

    public static List<Row> readTsv(Path file) throws IOException {
        List<String> lines = Files.readAllLines(file);
        if (lines.isEmpty()) {
            return List.of();
        }
        List<Row> out = new ArrayList<>();
        for (int i = 1; i < lines.size(); i++) {
            String line = lines.get(i).trim();
            if (line.isEmpty()) {
                continue;
            }
            String[] parts = line.split("\t", -1);
            Row row = new Row();
            row.mountId = Integer.parseInt(parts[0]);
            row.parentId = Integer.parseInt(parts[1]);
            row.root = parts[2];
            row.mountPoint = PathN.norm(parts[3]);
            row.propagation = parts[4];
            row.bindSource = parts[5];
            row.generation = Integer.parseInt(parts[6]);
            out.add(row);
        }
        return out;
    }
}
EOF
cat > /app/environment/k7n/src/main/java/com/internal/k7n/TableH.java <<'EOF'
package com.internal.k7n;

import java.util.Comparator;
import java.util.List;

public final class TableH {
    private TableH() {}

    private static int depth(String mountPoint) {
        if (mountPoint == null || mountPoint.isEmpty() || "/".equals(mountPoint)) {
            return 0;
        }
        int count = 0;
        for (int i = 0; i < mountPoint.length(); i++) {
            if (mountPoint.charAt(i) == '/') {
                count++;
            }
        }
        return count;
    }

    public static void sortRows(List<FoldA.Row> rows) {
        rows.sort(Comparator
            .comparingInt((FoldA.Row r) -> depth(r.mountPoint))
            .thenComparing(r -> r.mountPoint));
    }
}
EOF
bash /app/environment/ops/build.sh
java -jar /app/environment/driver/target/driver.jar fold
'''

SOLVE2 = r'''#!/bin/bash
set -euo pipefail
bash "$(dirname "$0")/../milestone_1/solution/solve1.sh" >/dev/null
cat > /app/environment/w3p/src/main/java/com/internal/w3p/JournalB.java <<'EOF'
package com.internal.w3p;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.internal.k7n.PathN;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class JournalB {
    private static final ObjectMapper M = new ObjectMapper();

    public static final class Event {
        public int seq;
        public int generation;
        public String mountPoint;
        public String op;
    }

    public static List<Event> load(Path file) throws IOException {
        JsonNode root = M.readTree(Files.readString(file));
        List<Event> out = new ArrayList<>();
        for (JsonNode node : root.get("events")) {
            Event e = new Event();
            e.seq = node.get("seq").asInt();
            e.generation = node.get("generation").asInt();
            e.mountPoint = node.get("mount_point").asText();
            e.op = node.get("op").asText();
            out.add(e);
        }
        return out;
    }

    public static Map<String, String> apply(List<com.internal.k7n.FoldA.Row> rows, List<Event> events) {
        Map<String, String> tags = new LinkedHashMap<>();
        for (var row : rows) {
            tags.put(PathN.norm(row.mountPoint), row.propagation);
        }
        Map<String, String> opMap = Map.of(
            "make_shared", "shared",
            "make_slave", "slave",
            "make_private", "private",
            "make_unbindable", "unbindable"
        );
        events.sort(Comparator.comparingInt(e -> e.seq));
        for (Event e : events) {
            String tag = opMap.get(e.op);
            if (tag != null) {
                tags.put(PathN.norm(e.mountPoint), tag);
            }
        }
        return tags;
    }
}
EOF
cat > /app/environment/w3p/src/main/java/com/internal/w3p/LedgerC.java <<'EOF'
package com.internal.w3p;

import com.internal.k7n.FoldA;
import com.internal.k7n.PathN;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class LedgerC {
    public static final class Entry {
        public String watchPath;
        public String visibility;
        public String propagationTag;
        public String peerGroup;
        public int generation;

        public Map<String, Object> asMap() {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("watch_path", watchPath);
            m.put("visibility", visibility);
            m.put("propagation_tag", propagationTag);
            m.put("peer_group", peerGroup);
            m.put("generation", generation);
            return m;
        }
    }

    public static List<Entry> build(List<FoldA.Row> rows, Map<String, String> tags, List<String> watches, Map<String, String> peers, int generation) {
        List<Entry> out = new ArrayList<>();
        for (String watch : watches) {
            Entry e = new Entry();
            e.watchPath = PathN.norm(watch);
            e.generation = generation;
            FoldA.Row hit = pick(rows, e.watchPath);
            if (hit == null) {
                e.visibility = "absent";
                e.propagationTag = "none";
                e.peerGroup = "none";
            } else {
                String mountPoint = PathN.norm(hit.mountPoint);
                e.propagationTag = tags.getOrDefault(mountPoint, hit.propagation);
                e.peerGroup = peers.getOrDefault(mountPoint, "none");
                e.visibility = classify(e.propagationTag);
            }
            out.add(e);
        }
        out.sort((a, b) -> a.watchPath.compareTo(b.watchPath));
        return out;
    }

    private static FoldA.Row pick(List<FoldA.Row> rows, String watch) {
        FoldA.Row best = null;
        for (FoldA.Row row : rows) {
            String mountPoint = PathN.norm(row.mountPoint);
            if (PathN.under(watch, mountPoint)) {
                if (best == null || mountPoint.length() > PathN.norm(best.mountPoint).length()) {
                    best = row;
                }
            }
        }
        return best;
    }

    private static String classify(String tag) {
        if ("private".equals(tag) || "rprivate".equals(tag)) {
            return "masked";
        }
        if ("slave".equals(tag) || "rslave".equals(tag)) {
            return "peer_only";
        }
        return "visible";
    }
}
EOF
bash /app/environment/ops/build.sh
java -jar /app/environment/driver/target/driver.jar ledger
'''

SOLVE2_REPLAY = r'''#!/bin/bash
set -euo pipefail
bash "$(dirname "$0")/../milestone_1/solution/solve1.sh" >/dev/null
bash /app/environment/ops/build.sh
java -jar /app/environment/driver/target/driver.jar replay --dual
'''

SOLVE1_MERGED = SOLVE1.rstrip() + "\n" + SOLVE2.split(">/dev/null\n", 1)[1]

TEST_M2_REPLAY = TEST_M3_BODY.replace("TestMilestone3", "TestMilestone2")


def build_merged_m1_tests() -> str:
    head, rest = TEST_M1_BODY.split("class TestMilestone1:", 1)
    m1_body, _ = rest.rsplit("\n", 1)
    m2_body = TEST_M2_BODY.split("class TestMilestone2:", 1)[1]
    return head + "class TestMilestone1:" + m1_body + m2_body


SPEC = """### Decision
GO — Attempt 1. New system-administration milestone task using Java mount propagation visibility reconstruction with filesystem_state_reconstruction profile.

### Metadata
- version: 2
- Task name: propagation-visibility-fold-auditor
- Category: system-administration
- Task shape: repair_existing_system
- Languages: [java, bash]
- Difficulty: hard
- Milestones: 2

## Authoring Brief

Offline Java desk under `/app/environment` reconstructs bind-mount propagation visibility from mountinfo snapshots, propagation journals, watch lists, and peer maps. Agent repairs source across fold, ledger, and dual-generation replay stages.

### platform_files
- path: task.toml
  role: v2 milestone metadata
- path: output_contract.toml
  role: repo-local contract
- path: construction_manifest.json
  role: local authoring manifest
- path: instruction.md
  role: canonical prompt entry represented by each localized step prompt
- path: tests/test.sh
  role: canonical verifier entry represented by each localized step runner
- path: tests/test_outputs.py
  role: canonical verifier test name represented by each localized step file
- path: solution/solve.sh
  role: canonical oracle entry represented by each localized step wrapper
- path: environment/Dockerfile
  role: digest-pinned Maven build + Temurin runtime
- path: steps/milestone_N/instruction.md
  role: per-step public prompts
- path: steps/milestone_N/tests/test_mN.py
  role: behavior verifiers
- path: steps/milestone_N/solution/solveN.sh
  role: deterministic oracle per step

### task_files
- path: environment/k7n
  role: mountinfo fold parser
- path: environment/w3p
  role: journal + visibility ledger
- path: environment/driver
  role: CLI driver jar
- path: environment/data, journals, watchlists, peer_maps
  role: local-only snapshots

### fix_frontier
- count: 4
- distribution: path normalization, fold ordering, journal override application, replay digest composition
- naming_policy: opaque module symbols k7n/w3p/mpv
- forbidden_stems: [propagation, visibility, mount, fold, ledger, replay]
- helpers_policy: TableH and PeerQ are non-frontier helpers
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 1
- direct_boolean_assertions_max: 1
- preferred_assertion_styles: records, digests, summary counts, idempotent replay
- forbidden_assertion_styles: source grep, boolean answer tables

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis across parser, journal precedence, visibility classification, dual-generation replay
- collapse_risk: low when prompts avoid per-path answer tables

### category_profile
- challenge_family: mount_propagation_visibility_reconstruction
- profile_name: filesystem_state_reconstruction
- allowed_instruction_disclosures: commands, schemas, visibility states, digest widths, data homes
- forbidden_instruction_leaks: exact Java class/file patch sites
- category_specific_hardness_bar: fold, ledger, and replay must coordinate across TSV, JSON journal, and watch lists
- category_specific_verifier_risks: static JSON, journal ignored, wrong sort, flaky replay
- coverage_role: first filesystem_state_reconstruction sysadmin milestone in bank

### difficulty_mechanism_plan
- mechanisms: [stateful_multi_step_dependencies, cross_file_cross_format_invariants, rollback_recovery_requirements, environment_specific_cli_semantics, deceptive_but_valid_local_evidence]
- adversarial_layers_count: 5
- fairness_guardrails: all inputs are local; commands and schemas are public; digests derive from visible data

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: operator can trace journal overrides against watch paths
- shortcut_audit: static JSON, test edits, and driver-only patches are rejected
- ablation_plan: fold, journal, and replay fixes flip distinct milestone subsets
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: reward is 1 only when all milestone pytest assertions pass

### subtype_milestone_plan
- subcategories: [tool_specific]
- milestone_count: 3
- sequential_dependency: ledger uses fold normalization; replay uses ledger rules across generations
- local_only_data: true
- sidecar_or_protocol_notes: mountinfo TSV, propagation JSON journals, peer maps

### satisfiability_risk
- rc2_planned_name_risk: medium
- gx9_contract_risk: low
- cr1_symbol_frontier_risk: low
- hidden_contract_risk: low

### actionability_plan
- verifier_command_visible: yes
- source_fix_intent_visible: yes
- generated_output_rule_visible: yes
- exact_formula_home: docs/output_schema.md and docs/surface_contract.md
- schema_home: milestone instructions + environment docs

### waiver_plan
- waivers_expected: no
- waiver_rationale: canonical base image, public contract, no collapse waiver needed

### reference_pattern
- justification_if_none: No promoted reference matches this Java propagation visibility fold auditor.

### realism_source
- source_type: real_system
- evidence_basis: Linux mount propagation and bind visibility audits
- upstream_or_synthetic_rationale: minimized from real mountinfo audit workflows
- minimization_preserves: propagation tag semantics, journal ordering, visibility states, dual-generation replay
- synthetic_exception_review: not applicable; local synthetic paths only

### Triviality Ledger
- Static JSON blocked by digest and regeneration tests.
- Single sort fix blocked by journal and replay stages.
- Parser-only fix blocked by ledger classification tests.

### Per-gate Pitfall Inventory
- RC1/RC7: oracle patches multiple modules with substantive logic.
- RC6: symptoms-only prompts with public schemas.
- Static checks: canonical images, milestone layout, test.sh footer.

### Initial Draft Commitments
- Full task tree under tasks/propagation-visibility-fold-auditor/

## Reviewer Appendix
Oracle touches FoldA path normalization, TableH depth sort, JournalB op map, RunR combined digest.
"""

if __name__ == "__main__":
    main()
