"""
Outlook Drafter: Creates draft email in local Outlook via COM automation.
Draft includes HTML body with Outlook's native signature and PDF attachment.
NEVER sends email — creates draft for review only.

Uses win32com (pywin32) to talk directly to the Outlook desktop app.
No Azure registration or Microsoft Graph API needed.
"""

import re
from pathlib import Path


# Sign-off phrases that mark the start of the AI-generated signature block.
# Everything from this line onward gets stripped so Outlook's native sig is used.
_SIGNOFF_PATTERNS = [
    r"^All the best,",
    r"^Best regards,",
    r"^Best,",
    r"^Regards,",
    r"^Sincerely,",
    r"^Thanks,",
    r"^Thank you,",
    r"^Warm regards,",
]


def _strip_text_signature(body_text: str) -> str:
    """Remove the plain-text signature block from AI-generated email body.

    Looks for a sign-off line (e.g., 'All the best,') and strips everything
    from that line onward, since Outlook will supply its own HTML signature.
    """
    lines = body_text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        for pattern in _SIGNOFF_PATTERNS:
            if re.match(pattern, stripped, re.IGNORECASE):
                # Keep everything before the sign-off, trim trailing blanks
                return "\n".join(lines[:i]).rstrip()
    return body_text


def _text_to_html(body_text: str) -> str:
    """Convert plain-text email body to simple HTML."""
    lines = body_text.split("\n")
    html_lines = []
    for line in lines:
        # Convert markdown bold **text** to <strong>
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        # Convert markdown bullet * to bullet point
        if line.startswith("* "):
            line = "&bull; " + line[2:]
        html_lines.append(line)

    return "<br>\n".join(html_lines)


def _build_recipients_str(recipient_list: list[dict]) -> str:
    """Convert config recipient list to semicolon-separated email string."""
    return "; ".join(
        r["email"]
        for r in recipient_list
        if r.get("email") and r["email"] != "TO_BE_FILLED"
    )


async def create_outlook_draft(
    subject: str,
    body_text: str,
    pdf_path: str,
    config: dict,
) -> dict:
    """
    Create a draft email in Outlook Drafts folder with PDF attached.

    Strategy:
      1. Create a new mail item and access GetInspector — this triggers
         Outlook to insert the user's default signature automatically.
      2. Read back HTMLBody (which now contains the native signature).
      3. Strip the AI-generated text signature from body_text.
      4. Insert our email content before the Outlook signature.
      5. Save as draft.

    Returns {"draft_id": "com", "web_link": ""} on success,
    or {"error": "..."} on failure. Never raises — pipeline continues either way.
    """
    try:
        import win32com.client as win32

        outlook_config = config.get("outlook", {})

        # Connect to running Outlook instance
        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 = olMailItem

        # Access GetInspector to trigger Outlook's signature insertion.
        # We don't need to display the window — just touching the property is enough.
        _inspector = mail.GetInspector  # noqa: F841

        # Capture the signature HTML that Outlook auto-inserted
        sig_html = mail.HTMLBody or ""

        # Strip the text signature from the AI body (Outlook's native sig replaces it)
        clean_body = _strip_text_signature(body_text)
        body_html = _text_to_html(clean_body)

        # Insert our content before Outlook's signature.
        # Outlook's HTMLBody typically has <body>..signature..</body>.
        # We inject our email content right after the <body> tag.
        body_tag_match = re.search(r"(<body[^>]*>)", sig_html, re.IGNORECASE)
        if body_tag_match:
            insert_pos = body_tag_match.end()
            mail.HTMLBody = (
                sig_html[:insert_pos]
                + f'<div style="font-family: Calibri, sans-serif; font-size: 11pt;">'
                + body_html
                + "<br><br></div>"
                + sig_html[insert_pos:]
            )
        else:
            # Fallback: no body tag found, just set directly
            mail.HTMLBody = (
                '<html><head><meta charset="utf-8"></head>'
                f'<body style="font-family: Calibri, sans-serif; font-size: 11pt;">'
                f"{body_html}</body></html>"
            )

        # Set subject and recipients
        mail.Subject = subject

        to_str = _build_recipients_str(outlook_config.get("recipients_to", []))
        cc_str = _build_recipients_str(outlook_config.get("recipients_cc", []))
        if to_str:
            mail.To = to_str
        if cc_str:
            mail.CC = cc_str

        # Attach PDF (must be absolute path for COM)
        pdf_file = Path(pdf_path).resolve()
        if pdf_file.exists():
            mail.Attachments.Add(str(pdf_file))

        # Save as draft (do NOT send)
        mail.Save()

        return {"draft_id": "com", "web_link": ""}

    except ImportError:
        return {"error": "pywin32 not installed. Run: pip install pywin32"}
    except Exception as e:
        return {"error": f"Outlook COM error: {e}"}
