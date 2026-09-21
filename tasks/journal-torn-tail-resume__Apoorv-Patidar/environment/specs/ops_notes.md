# Operator notes: wrenkv field incidents

Notes from the on-call rotation, kept here so the next person does not have
to rediscover them. Symptom-level only; the store contract in
`store_contract.md` is the normative reference.

## Incident timeline (paraphrased from tickets)

- T1: "Loader confirmed 40 writes, machine got OOM-killed at record ~40,
  after `recover` the store serves an older snapshot. Store had been
  compacted the night before. A store that was never compacted recovers
  fine."
- T2: "Kill landed mid-record during a bulk import. `recover` now refuses to
  run at all and prints an integrity failure. Support workaround is deleting
  the log by hand, which obviously loses the day."
- T3: "Compaction was killed partway (node reboot). Store still opens, but
  writes from before the compaction are gone. Compaction that completes
  normally is fine."
- T4: "Recovery pass itself got killed (second reboot). The next recovery
  pass completes and exits 0, but the store serves less than what the first
  pass had already merged — a second kill turned a recoverable store into a
  lossy one."

## What support has confirmed

- The loader acknowledges each write individually and each acknowledgement
  is backed by a fence, so "the loader confirmed it" always means "the first
  N operations are durable".
- Kills during plain `load` (fence-aligned) never lose confirmed writes on a
  store that was never compacted, as long as `recover` actually runs.
- `dump` on a live store always looks correct, even on stores whose recovery
  is broken. The wrongness only shows up across kill + `recover`.
- Re-running `recover` twice on a healthy store changes nothing; on the
  affected stores a second run can make things worse.
