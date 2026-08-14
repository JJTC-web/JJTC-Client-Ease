# JJTC-Client-Ease

Flask app for collecting client feedback after meetings.

## Client review flow

- `/login` — optional, one-time client identification (name + email) before leaving a review. Clients can skip it and review anonymously via the link on that page.
- `/nps` — the review form (score 0-10 + comments). Each client (by email) or browser session can only submit once.
- On submit, an email is sent to the firm with the review and a color-coded actionable step (red = detractor, amber = passive, green = promoter).
- `/results` — internal view of all submissions, color-coded by tier.

## Environment variables

| Variable | Purpose | Required |
|---|---|---|
| `SECRET_KEY` | Flask session signing key | Recommended in production |
| `OWNER_EMAIL` | Where review emails are sent | Defaults to the firm owner's email |
| `SMTP_HOST` | SMTP server host | Required to send review emails (skipped if unset) |
| `SMTP_PORT` | SMTP server port | Defaults to `587` |
| `SMTP_USERNAME` | SMTP login username | Optional, depends on provider |
| `SMTP_PASSWORD` | SMTP login password | Optional, depends on provider |
| `SMTP_FROM` | From address for outgoing mail | Defaults to `SMTP_USERNAME` or `OWNER_EMAIL` |

If `SMTP_HOST` isn't set, review submissions still save normally — the app just logs that it skipped sending the email.
