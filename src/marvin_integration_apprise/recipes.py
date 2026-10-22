"""Workflow Library recipes Apprise ships (SDK 0.9.0): offered in Marvin once an Apprise connection exists.

Marvin's own notification recipes already send through any ``notify`` connection, so this one is only here for what
is specific to Apprise: ``notify`` reports ``sent: false`` when a service refuses the message instead of raising, so
a plain workflow step looks successful, raises no integration alert and sends nothing to review. The recipe reads
that result and records it on the entry.
"""

from marvin_integration_sdk import WorkflowRecipe

DELIVERY_KEY = "apprise_delivery"

ANNOUNCE_AND_RECORD = WorkflowRecipe(
    id="announce-and-record-delivery",
    title="Announce published entries and record delivery",
    outcome=(
        "Each published entry of one type is sent through Apprise with its title and link, and whether every service "
        "accepted it (sent or failed) is saved on the entry."
    ),
    category="Notifications",
    tags=("announce", "publishing", "notify"),
    definition={
        "trigger": {"type": "event", "event": "entry_published"},
        "conditions": [{"field": "entry.entry_type", "op": "eq", "value": "{{entry_type}}"}],
        "actions": [
            {
                "kind": "integration",
                "id": "announce",
                "integration": "{{apprise_integration}}",
                "action": "notify",
                "args": {"title": "{{heading}}", "body": "${entry.title}\n${entry.url}"},
            },
            {
                "kind": "entry",
                "op": "set_metadata",
                "metadata": {DELIVERY_KEY: "sent"},
                "when": {"field": "steps.announce.output.sent", "op": "eq", "value": True},
            },
            {
                "kind": "entry",
                "op": "set_metadata",
                "metadata": {DELIVERY_KEY: "failed"},
                "when": {"field": "steps.announce.output.sent", "op": "eq", "value": False},
            },
        ],
    },
    variables={
        "entry_type": {"type": "entry_type_slug", "description": "Which entries to announce when they are published.", "example": "post"},
        "apprise_integration": {
            "type": "integration_slug",
            "description": "The Apprise connection (its list of services) to send through.",
            "example": "apprise",
        },
        "heading": {"type": "text", "description": "The notification's title, shown above the entry's title and link.", "example": "New on the site"},
    },
    side_effects=(
        {"kind": "notification", "description": "Sends a message to every service on the Apprise connection."},
        {"kind": "content_mutation", "description": "Saves on the entry whether it was sent or failed."},
    ),
)

RECIPES = (ANNOUNCE_AND_RECORD,)
