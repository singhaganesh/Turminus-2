# Harbour stow book

Call `/opt/ferry/bin/cleat stow --roll PATH --chalk PATH`.
Rolls are UTF-8, one command per line. Blank lines and `#` comments are
skipped. Fields are spaces or tabs. Plate names are letters, digits, period,
underscore, or hyphen. Length, height, mass, hazmat, and board numbers are
unsigned decimals. Anything else is malformed (exit 2).

```
PLATE name LEN cm HT cm MASS kg HAZ 0|1 BOARD n
```

`LEN`, `HT`, and `MASS` must be greater than zero. `HAZ` is `0` or `1`. `BOARD`
is a positive boarding sequence: smaller numbers drive on first. Equal `BOARD`
values load in ascending plate name.

An empty roll writes an empty chalk file and exits 0. Chalk is replaced with
NDJSON. `i` starts at 1; every input plate yields one `stow` row in listing
order, not packing order. Successful `ok` is `yes`; otherwise `no`. `verb` is
`stow`. A plate that cannot fit is not placed: `ok` is `no` and `deck`, `lane`,
and `station` are omitted.

Lane lids live on `/app/dock/lane-cards.md`. Seats, stations, and keep-clear
distances live on `/app/dock/discharge.md`.
