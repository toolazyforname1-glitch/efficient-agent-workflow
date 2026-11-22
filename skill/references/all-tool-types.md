- **This applies to ALL tool types, not just shell commands.** Anything
  independent — several `edit` calls, several `write` calls, multiple bash
  commands, a web search (EXA / Firecrawl / context7), a `todowrite` — can go in
  ONE message instead of one per turn. Every extra turn is a whole extra request
  against the model; batching is the single biggest token saving available, far
  larger than trimming output.
