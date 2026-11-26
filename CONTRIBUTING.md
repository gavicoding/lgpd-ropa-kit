# Contributing

Bug reports and pull requests are welcome.

1. Open an issue first for anything bigger than a small fix, so we can agree on the approach.
2. New rules need a code (`R0NN`), a message in Portuguese and English in `messages.py`, a test
   for the case that fires and one for the case that does not, and a line in both READMEs.
3. Use made-up data only: "Empresa Exemplo Ltda", the `exemplo.test` domain and fictional
   processors. Never commit a real inventory.
4. If you change the sample or the report, regenerate `examples/` and `docs/` (see the README).
5. Before pushing:

   ```bash
   pip install -e ".[dev]"
   ruff check . && ruff format --check . && pytest
   ```

6. Write commit messages in the imperative ("Add rule for children's data"), one topic per commit.

By contributing you agree that your work is released under the MIT license.
