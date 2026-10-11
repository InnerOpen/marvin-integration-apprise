# Apprise

Sends one notification to **every service** on a connection through [Apprise](https://github.com/caronc/apprise),
which reaches Slack, Discord, Telegram, email and 100+ other services from a single URL scheme. One connection is
one list of Apprise URLs; a message goes to all of them.

## Connect it

1. For each service, build its Apprise URL (for example `slack://…`, `discord://…`, `tgram://…`). The Apprise
   project documents the URL format for each service.
2. In Marvin: **Settings → Integrations**, add **Apprise Notifications**, and put the URL(s) in the **Apprise URL(s)**
   credential.
3. Several services at once: put **one URL per line** (a comma also separates them). Every message goes to every
   URL on the connection. To send to different services at different times, connect Apprise more than once.
4. The URLs carry tokens, so they are the credential: a pasted value is kept in Marvin's secret store and never
   read back, or type `{{SECRET_NAME}}` to use a workspace secret you already have (rotating that secret rotates the
   connection). Marvin scrubs the URLs from any error it records or sends.

The health check (↻ on the card) reports **unconfigured** ("No Apprise URL configured.") with no URL, and **error** ("Invalid
Apprise URL(s): …") when Apprise doesn't recognise one. It checks that the URLs are well formed; it does not send
anything, so run **Send notification** from the card (or a workflow) to confirm delivery.

Because a comma separates URLs, a URL that itself contains a comma (a list of recipients, say) is split in two.
Keep it to one value per URL, or connect it on its own.

## Send a notification

The action is **Send notification** (`notify`):

- `body` — the message (required).
- `title` — optional subject.

It returns `{ "sent": true | false, "targets": <number of URLs on the connection> }`.

It is Marvin's standard **notify** capability, so the notification recipes in the Workflow Library and a workflow
step that names `capability: notify` can send through Apprise as well as Slack. In a workflow step, `${entry.title}`,
`${entry.url}` and other templates are filled in when it runs. An event subscription (Automation → Events → pick an
event → Connect an integration action) takes `{{event_type}}` and any field of the event, such as `{{entry_title}}`.

The **Announce published entries and record delivery** recipe sends each published entry of one type with its link,
and records on the entry whether it arrived.

## It does not raise when a service refuses

`sent` is `true` only when every service accepted the message and `false` if even one did not (or there was
nothing to send to). A refused message **does not fail the step**: there is no error, no retry, no review and no integration
alert. If delivery matters, add a step that checks `${steps.<id>.output.sent}`, as the recipe does. A step
condition is `{"field": "steps.<id>.output.sent", "op": "eq", "value": false}`.

`targets` counts the URLs on the connection, not the ones that worked, and a URL Apprise can't parse is skipped when
sending, so fix any "Invalid Apprise URL(s)" the card reports.

## How it fits Marvin

- **Integration alerts.** Marvin's own alerts (a connection or workflow that needs attention) can go out through
  Apprise: **Settings → Automation → Notifications**, add Apprise's *Send notification* as a route and choose which
  kinds it takes.
- **Events.** Connect `notify` to an event, or call it from a workflow's **Run integration** step.
- Core's own Apprise notifier no longer exists: this plugin is how Marvin notifies through Apprise.

## What it can't do

- Send attachments, files or images (put a link in the body).
- Choose a message format or type: the action has only `title` and `body`.
- Send to some of the URLs only: there is no tag or target filter, so each message goes to all of them.
- Receive replies or report which service failed.

## When it fails

This plugin names no error codes, so Marvin handles a failure as an unnamed ("unknown") one, with no plugin-specific
retry policy.

- **"No Apprise URL configured for this integration."** — the credential is empty or the secret it points to has no
  value. Add the URL(s).
- **`sent: false`** — at least one service didn't accept the message; see "It does not raise" above. Check the
  service's own URL, token and channel, and that it is reachable from Marvin.
- **The card shows "Invalid Apprise URL(s)"** — Apprise doesn't know the scheme or the URL is malformed.
