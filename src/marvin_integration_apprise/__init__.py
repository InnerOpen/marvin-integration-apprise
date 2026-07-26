"""Apprise notifications as a Marvin integration provider.

Apprise (github.com/caronc/apprise) fans one message out to 100+ services — Slack, Discord, Telegram,
email, and more — through a single URL scheme. This wraps it as a Marvin ``notify`` provider: the
Apprise URL(s) are the credential (stored behind ``secret_ref``), and a ``notify`` action sends a
title/body. Wire it to events with an integration event subscription so "on event X → notify"
replaces the old core notifier, credential and all.
"""

from __future__ import annotations

from marvin_integration_sdk import (
    CATEGORY_NOTIFY,
    CredentialField,
    IntegrationContext,
    IntegrationProvider,
    ProviderAction,
    register_provider,
)

__version__ = "0.1.0"


def _parse_urls(secret: str | None) -> list[str]:
    """Split the credential into individual Apprise URLs (newline- or comma-separated)."""
    return [u.strip() for u in (secret or "").replace(",", "\n").splitlines() if u.strip()]


@register_provider
class AppriseProvider(IntegrationProvider):
    """Multi-channel notifications via an Apprise URL."""

    slug = "apprise"
    name = "Apprise Notifications"
    description = "Send notifications to Slack, Discord, Telegram, email, and 100+ services via an Apprise URL."
    category = CATEGORY_NOTIFY

    credentials = (
        CredentialField(
            key="apprise_url",
            label="Apprise URL(s)",
            help="One or more Apprise service URLs (e.g. slack://…, discord://…). Separate multiple with a newline or comma.",
            required=True,
        ),
    )

    actions = (
        ProviderAction(
            key="notify",
            label="Send notification",
            description="Fan a title/body out to every configured Apprise URL.",
            capability="notify",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Notification title/subject."},
                    "body": {"type": "string", "description": "Notification body (required)."},
                },
                "required": ["body"],
            },
            output_schema={
                "type": "object",
                "properties": {"sent": {"type": "boolean"}, "targets": {"type": "integer"}},
            },
        ),
    )

    def check(self, ctx: IntegrationContext) -> tuple[str, str | None]:
        urls = _parse_urls(ctx.secret)
        if not urls:
            return ("unconfigured", "No Apprise URL configured.")
        import apprise

        client = apprise.Apprise()
        bad = [u for u in urls if not client.add(u)]
        if bad:
            return ("error", f"Invalid Apprise URL(s): {', '.join(bad)}")
        return ("ok", None)

    def run_action(self, key: str, args: dict, ctx: IntegrationContext) -> dict:
        if key != "notify":
            raise NotImplementedError(f"apprise provider has no action '{key}'")
        urls = _parse_urls(ctx.secret)
        if not urls:
            raise ValueError("No Apprise URL configured for this integration.")

        import apprise

        client = apprise.Apprise()
        for url in urls:
            client.add(url)
        body = args.get("body") or args.get("message") or ""
        title = args.get("title") or ""
        sent = bool(client.notify(body=body, title=title))
        ctx.logger.info(f"apprise: notified {len(urls)} target(s) ok={sent}")
        return {"sent": sent, "targets": len(urls)}
