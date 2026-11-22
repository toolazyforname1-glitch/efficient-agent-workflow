- **Dependency is the ONLY reason to serialise.** If command B needs command A's
  output (a path, an ID, a value read from a file, a test result), then A alone
  first is correct. Judge by "does B literally need A's output to be written?",
  not by habit or by topic similarity.
