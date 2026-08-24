# DNS / Custom Domain Setup — jjtc.info

Reference notes for hosting the two production apps under the already
registered `jjtc.info` domain (managed in GoDaddy), via Railway custom
domains.

## Apps and subdomains

| Subdomain | App | Repo |
|---|---|---|
| `app.jjtc.info` | JJTC client onboarding app (welcome, intake, checklist, admin dashboard) | [`JJTC-web/JJTC-Guided-Onboarding`](https://github.com/JJTC-web/JJTC-Guided-Onboarding) |
| `os.jjtc.info` | MissionOS AI (nonprofit organizational health assessment) | [`JJTC-web/Missions-ai`](https://github.com/JJTC-web/Missions-ai) |

`os.jjtc.info` was chosen over `missionos.jjtc.info` — shorter, and easier to
migrate off later if MissionOS ever gets its own dedicated domain.

Both apps are Flask services deployed on Railway (each has a `Procfile`
running gunicorn), so each gets its own Railway custom-domain entry pointed
at a different subdomain of the same `jjtc.info` root domain.

`JJTC-Client-Ease` (this repo) is a separate, standalone survey tool and is
not part of this hosting plan — these notes live here for reference only.

## DNS records (GoDaddy)

GoDaddy → My Products → `jjtc.info` → DNS → Add Record:

| Type | Name | Value | TTL |
|---|---|---|---|
| CNAME | `app` | *(CNAME target Railway gives the Guided-Onboarding project)* | 1 hour |
| CNAME | `os` | *(CNAME target Railway gives the Missions-ai project)* | 1 hour |

## Steps

1. In Railway, open the **JJTC-Guided-Onboarding** project → Settings →
   Networking → Custom Domain → enter `app.jjtc.info`. Copy the CNAME target
   Railway shows.
2. In Railway, open the **Missions-ai** project → Settings → Networking →
   Custom Domain → enter `os.jjtc.info`. Copy its CNAME target.
3. Before adding records, check GoDaddy's existing DNS list to make sure
   `app` or `os` isn't already used (e.g. by Website Builder).
4. In GoDaddy DNS for `jjtc.info`, add the two CNAME records above using the
   values from steps 1–2.
5. Save and wait for propagation. Railway shows "Waiting for DNS" then a
   green checkmark once it verifies, and auto-issues SSL.

## Follow-up once subdomains are live

Both apps were originally configured against their default Railway-provided
hostnames. After the custom domains go live:

- **JJTC-Guided-Onboarding**: already sends email from `hello@jjtc.info` and
  links to `https://www.jjtc.info`, so the root domain is already verified in
  Resend. One hardcoded reference has been fixed to track the new domain: the
  workbook PDF link (`app.py`, previously
  `https://web-production-51ad4.up.railway.app/static/workbook.pdf`) now
  reads from an `APP_BASE_URL` env var (see `env.example`) — set
  `APP_BASE_URL=https://app.jjtc.info` on the Railway service once the custom
  domain is verified. (Pushed on branch `claude/app-base-url-jjtc-info`.)
- **Missions-ai**: `RESEND_FROM_EMAIL` currently defaults to Resend's test
  sender (`onboarding@resend.dev`). Verify `jjtc.info` (or a subdomain of it)
  in Resend and set `RESEND_FROM_EMAIL` to something like
  `MissionOS AI <notifications@os.jjtc.info>` before sending to real
  submitters.
- **Both apps**: update Supabase Auth's Site URL / Redirect URLs (in each
  Supabase project's Auth settings) from the old `*.up.railway.app` hostname
  to the matching `jjtc.info` subdomain, so `/dashboard` login redirects work
  correctly on the new domain.
