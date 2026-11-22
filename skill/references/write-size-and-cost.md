**SIZE INTERACTION:** the write-tool reliability rules (~2000–3000 chars per call, JSON escaping) apply PER CALL and still hold. Smaller calls are fine — they just all go in the SAME message. Batching many medium writes in one message is the default; splitting one oversized file across calls is the narrow exception.

**COST MATH:** 1 extra request = whole context re-sent + full decode. Batching 10 writes into one message removes 9 full requests. In any multi-file task this is the single largest saving available — bigger than any output trimming.
