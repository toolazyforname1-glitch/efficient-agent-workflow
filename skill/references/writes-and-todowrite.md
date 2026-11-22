  - **Multiple `write`/`edit` calls on DIFFERENT files are ALWAYS independent —
    emit all of them in ONE message.** Writing file 1, ending the turn, then
    writing file 2 in the next request is the most expensive habit in this
    harness: N files = N requests instead of 1. See "BATCH FILE WRITES" at the
    top of this file. (Payload-size rules still apply per call; they never
    justify serialising across turns.)
  - `todowrite` is independent of everything — batch it with the work it
    describes rather than spending a turn on it alone.
