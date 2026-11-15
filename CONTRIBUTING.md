# Contributing to Bluey

Bug reports and pull requests are welcome.

## Reporting a bug

Open an issue with the bug report template: what you did, what you expected,
what happened, and your setup (Ubuntu/Windows/macOS version, Python version,
iPhone or browser client). Security problems follow
[docs/SECURITY.md](docs/SECURITY.md), not the public tracker.

## Before opening a pull request

- Keep the trust model intact: the desktop acts only on the owner's approved
  phone, asks before OS-level actions, and never answers strangers. Changes
  that weaken an approval gate will be rejected.
- Run the Desktop test suite and add coverage for what you changed:

  ```sh
  cd Desktop
  python3 -m pytest tests
  ```

- The Swift sources under `iOS/`, `Mac/` and `Shared/` are the upstream phone
  app and its protocol; coordinate before changing them, because the desktop
  port must stay wire-compatible (`docs/PROTOCOL.md`).
- Keep comments and docs in the same voice as the file you are touching.
