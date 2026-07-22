# US-089 Frozen Baseline

- Frozen source: `6e8243f2a5cb6a32cf0a7a0ecebdb257a429bdd9`
- Disposable checkout: external artifact `frozen-baseline/checkout`
- Database fixture: checksum-verified SQLite online backup; reset before the suite.
- Raw logs: external owner-only `frozen-baseline/logs` directory.

| Command | Exit | Duration (seconds) |
| --- | ---: | ---: |
| `tool-versions` | 0 | 1 |
| `npm-ci` | 0 | 17 |
| `playwright-browser` | 0 | 1 |
| `cargo-test` | 0 | 16 |
| `web-build` | 0 | 4 |
| `web-e2e` | 0 | 17 |
| `desktop-smoke` | 0 | 7 |
| `cargo-fmt` | 0 | 0 |
| `cargo-clippy` | 0 | 4 |
| `changeset-rebuild` | 0 | 8 |
| `changeset-validator-tests` | 0 | 6 |
