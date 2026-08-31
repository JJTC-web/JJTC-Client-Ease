# DNS / Custom Domain Setup — jjtc.info

Reference notes for hosting the two production apps under the already
registered `jjtc.info` domain (managed in GoDaddy), via Railway custom
domains.

## Apps and subdomains (already live)

Both subdomains already have working GoDaddy CNAME records pointing at their
Railway apps — this was already fully set up, contrary to earlier drafts of
this doc that assumed `app.jjtc.info` / `os.jjtc.info` still needed to be
created:

| Subdomain | App | Repo | CNAME target |
|---|---|---|---|
| `onboarding.jjtc.info` | JJTC client onboarding app (welcome, intake, checklist, admin dashboard) | [`JJTC-web/JJTC-Guided-Onboarding`](https://github.com/JJTC-web/JJTC-Guided-Onboarding) | `web-production-51ad4.up.railway.app` |
| `missions.jjtc.info` | MissionOS AI (nonprofit organizational health assessment) | [`JJTC-web/Missions-ai`](https://github.com/JJTC-web/Missions-ai) | `6i8u490x.up.railway.app` |

Both apps are Flask services deployed on Railway (each has a `Procfile`
running gunicorn).

`JJTC-Client-Ease` (this repo) is a separate, standalone survey tool and is
not part of this hosting plan — these notes live here for reference only.

## If a subdomain won't load

Since DNS already resolves correctly for both, a "can't open this site"
report is not a missing-DNS-record problem. Check, in order:

1. **Railway custom domain status** — in each Railway project → Settings →
   Networking, confirm the custom domain shows a green "verified" checkmark
   and not "Waiting for DNS" or an SSL-pending state.
2. **App-level errors** — the Flask app itself may be erroring (500), or a
   required env var (`DATABASE_URL`, `SUPABASE_URL`, etc.) may be unset on
   that Railway service. Check Railway's deploy logs.
3. **Browser-specific issues** — stale DNS cache, a typo in the URL, or an
   ISP/DNS resolver that hasn't picked up the record yet.

## Follow-up items

- **JJTC-Guided-Onboarding**: already sends email from `hello@jjtc.info` and
  links to `https://www.jjtc.info`, so the root domain is already verified in
  Resend. The previously hardcoded workbook PDF link
  (`https://web-production-51ad4.up.railway.app/static/workbook.pdf`) now
  reads from an `APP_BASE_URL` env var (see `env.example`), defaulting to
  `https://onboarding.jjtc.info` — the real, already-live custom domain.
  (Pushed on branch `claude/app-base-url-jjtc-info`.)
- **Missions-ai**: `RESEND_FROM_EMAIL` currently defaults to Resend's test
  sender (`onboarding@resend.dev`). Verify `jjtc.info` (or a subdomain of it)
  in Resend and set `RESEND_FROM_EMAIL` to something like
  `MissionOS AI <notifications@missions.jjtc.info>` before sending to real
  submitters.
- **Both apps**: check Supabase Auth's Site URL / Redirect URLs (in each
  Supabase project's Auth settings) reference `onboarding.jjtc.info` /
  `missions.jjtc.info` rather than the old `*.up.railway.app` hostname, so
  `/dashboard` login redirects work correctly on the custom domain.
