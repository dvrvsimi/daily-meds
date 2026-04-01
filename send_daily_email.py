"""
send_daily_email.py
───────────────────
Picks a random passage from Marcus Aurelius's Meditations
and sends it as a formatted HTML email via the Resend API.

Environment variables (set as GitHub repo secrets):
  RESEND_API_KEY   — your Resend API key
  SENDER_EMAIL     — verified sender address (e.g. stoic@yourdomain.com)
  RECIPIENT_EMAIL  — where to deliver the daily passage
"""

import json
import os
import random
import resend


def load_passages(filepath="meditations.json"):
    """Load all passages from the JSON data file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def format_email_html(passage):
    """
    Build a clean HTML email body from a passage dict.
    Each passage has: {"book": int, "section": int, "text": str}
    """
    return f"""
    <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto;
                padding: 30px; color: #2c2c2c; line-height: 1.7;">

        <h2 style="color: #8b7355; font-size: 14px; text-transform: uppercase;
                    letter-spacing: 2px; margin-bottom: 20px;">
            Daily Meditations
        </h2>

        <blockquote style="border-left: 3px solid #8b7355; padding-left: 20px;
                           margin: 0 0 25px 0; font-size: 17px;">
            {passage["text"]}
        </blockquote>

        <p style="color: #888; font-size: 13px; font-style: italic;">
            — Marcus Aurelius, <em>Meditations</em>,
            Book {passage["book"]}, §{passage["section"]}
        </p>

        <hr style="border: none; border-top: 1px solid #ddd; margin-top: 30px;">
        <p style="color: #aaa; font-size: 11px;">
            George Long translation (1862) · Public domain
        </p>
    </div>
    """


def main():
    # ── Load config from environment ──────────────────────────────────
    api_key = os.environ["RESEND_API_KEY"]
    sender = os.environ["SENDER_EMAIL"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    resend.api_key = api_key

    # ── Pick a random passage ─────────────────────────────────────────
    passages = load_passages()
    passage = random.choice(passages)

    # ── Send the email ────────────────────────────────────────────────
    result = resend.Emails.send({
        "from": f"Daily Stoic <{sender}>",
        "to": [recipient],
        "subject": f"Meditations · Book {passage['book']}, §{passage['section']}",
        "html": format_email_html(passage),
    })

    print(f"Sent Book {passage['book']}, §{passage['section']} → {recipient}")
    print(f"Resend ID: {result['id']}")


if __name__ == "__main__":
    main()
