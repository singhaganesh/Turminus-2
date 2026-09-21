wrenkv, the little store engine at /app/bin/wrenkv, came back from its pilot deployment with four damage reports. Its intended behavior is spelled out, clause by clause, in /app/specs/store_contract.md, and the on-call story behind them is in /app/specs/ops_notes.md. The Go implementation mounted at /app/environment is what needs repairing.

The pilot reports:

1. Where a kill left a partially written record, `recover` exits nonzero complaining about integrity, and the workaround crews used (deleting files) throws away good records along with the broken one.
2. Such directories also stop accepting loads, and operations taken in afterwards never show up in `dump`, however often a pass is restarted.
3. A `compact` interrupted partway can lose operations that were already confirmed, sometimes leaving `dump` serving an empty view.
4. The progress coordinate in `dump` never leaves zero, and a recovery pass killed partway changes what the next one yields.

The command surface is frozen — /app/bin/wrenkv dump and its three sibling subcommands, every flag, the kill exit code, and the exact shape of the reported view, down to the covered_seq progress coordinate and its field names and types, all as the contract doc fixes them — and none of it may change. Sample inputs sit in /app/workloads/. You must fix the Go source code under /app/environment. Validation may run `go -C /app/environment test /app/...` before driving the CLI. Since the test pipeline rebuilds stores from scratch with these same commands, hand-made store files accomplish nothing: the repair belongs in the engine's own modules, at the library level, not around them.
