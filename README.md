# marvin-integration-apprise

[Apprise](https://github.com/caronc/apprise) multi-channel notifications as a Marvin integration
provider. Sends to Slack, Discord, Telegram, email, and 100+ services through a single Apprise URL
scheme, wired to Marvin events.

## What it provides

- **Provider** `apprise` (category `notify`).
- **Credential** — one or more Apprise URLs (e.g. `slack://…`, `discord://…`), stored behind the
  workspace secret backend (`secret_ref`), never on the integration row.
- **Action** `notify` (capability `notify`) — fans a `title`/`body` out to every configured URL.

Connect it to an event with an integration event subscription (`on <event> → notify`) and it
replaces the legacy core notifier, credential and all.

## Install

The provider is discovered through the `marvin.integrations` entry point — installing the package
into the Marvin environment registers it on startup.

```bash
pip install marvin-integration-apprise
```

For a Marvin container, add it to the image or a Helm `initContainers` step (see the Marvin chart
README for the plugin-install pattern).

## Logo

`logo.png` is the Apprise logo from [caronc/apprise](https://github.com/caronc/apprise/blob/master/apprise/assets/themes/default/apprise-logo.png), scaled to 390×160 (BSD-2-Clause, © Chris Caron; the licence ships beside it as `logo-LICENSE.txt`). Marvin shows it in place of the 🔔 emoji; it identifies the integration and doesn't imply endorsement by the Apprise project.

## Develop

```bash
uv run --group dev pytest
```

The SDK is resolved from the sibling `../MarvinIntegrationSDK` checkout in development (see
`pyproject.toml`); released builds take it from the index.
