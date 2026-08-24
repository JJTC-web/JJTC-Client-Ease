# DNS / Custom Domain Setup — jjtc.info

Reference notes for pointing subdomains of `jjtc.info` (managed in GoDaddy) at
Railway-hosted services.

## Subdomains

| Subdomain | Purpose |
|---|---|
| `app.jjtc.info` | JJTC AI agent (client onboarding, welcome, intake) |
| `os.jjtc.info` | MissionOS AI |

`os.jjtc.info` was chosen over `missionos.jjtc.info` — shorter, and easier to
migrate off later if MissionOS ever gets its own dedicated domain.

## DNS records (GoDaddy)

GoDaddy → My Products → `jjtc.info` → DNS → Add Record:

| Type | Name | Value | TTL |
|---|---|---|---|
| CNAME | `app` | *(CNAME target Railway gives the JJTC app project)* | 1 hour |
| CNAME | `os` | *(CNAME target Railway gives the MissionOS project)* | 1 hour |

## Steps

1. In Railway, open the **JJTC agent project** → Settings → Networking →
   Custom Domain → enter `app.jjtc.info`. Copy the CNAME target Railway shows.
2. In Railway, open the **MissionOS project** → Settings → Networking →
   Custom Domain → enter `os.jjtc.info`. Copy its CNAME target.
3. In GoDaddy DNS for `jjtc.info`, add the two CNAME records above using the
   values from steps 1–2.
4. Save and wait for propagation. Railway shows "Waiting for DNS" then a
   green checkmark once it verifies, and auto-issues SSL.
5. Before adding the records, check GoDaddy's DNS list to make sure `app` or
   `os` isn't already used (e.g. by Website Builder).

## Follow-up once subdomains are live

The JJTC app's Supabase Auth config and Resend sending domain were originally
set up against the default Railway-provided hostname. After `app.jjtc.info`
goes live, update:

- Resend's "from" sending domain to match `app.jjtc.info`.
- Any hardcoded redirect URLs in Supabase Auth (Site URL / Redirect URLs) to
  use `app.jjtc.info` instead of the old `*.up.railway.app` hostname.

Otherwise emails and auth redirects may keep referencing the old Railway URL.

*Note: this app (`JJTC-Client-Ease`) is a standalone Flask survey tool and
does not itself use Railway custom domains, Supabase, or Resend — these notes
are recorded here for reference since no other repo was specified.*
