---
name: tsenta
description: Run the user's job search through their Tsenta account. Find matched jobs, tailor their resume to each role, apply on 30+ employer systems including Workday, Greenhouse, Lever and Ashby, track application status, and read recruiter replies. Use when the user asks to find jobs, apply to jobs, tailor a resume for a role, check on applications, or triage recruiter email. Needs the Tsenta MCP server (https://api.autojobs.me/api/v1/mcp) connected as "tsenta".
---

# Tsenta job search

Tsenta is the user's own AI job application agent. Its MCP server, connected as `tsenta`, acts on the user's Tsenta account: their profile, their résumé versions and their application allowance. Applications are real. Each one goes to a real employer and uses one application from the user's allowance.

## If the tools are missing

If no `tsenta` tools are available, the server isn't connected. Don't try to connect it yourself, and don't stop the Gateway. Ask the user to add it. In the OpenClaw Control UI: **Settings → MCP → Add server**, name it `tsenta`, choose **Streamable HTTP**, enter `https://api.autojobs.me/api/v1/mcp` and add it. Then add `"auth": "oauth"` to the `tsenta` entry in the `mcp` config editor, save, and select **Sign in**. Or with these commands, which they run themselves:

```bash
openclaw gateway stop
openclaw mcp add tsenta --url https://api.autojobs.me/api/v1/mcp --transport streamable-http --auth oauth
openclaw mcp login tsenta
openclaw gateway start
```

They approve access in the browser. They need a Tsenta account: the first 25 applications are free, and paid plans add more. Setup for other assistants: https://tsenta.com/mcp

## Workflow

1. **Check readiness once per session.** Call `get-profile-status`. If `missingForApplication` lists fields, ask the user for each one and save it with the matching tool (`set-personal-info`, `set-work-authorization`, `set-application-preferences`, `set-education`, `set-work-experience`, `submit-resume`). Location (street address, city, state, country, ZIP code) can't be saved through these tools, so ask the user to add it in their Tsenta dashboard profile. Never invent profile facts.
2. **Find roles.** Call `get-job-recommendations` with the user's filters (title keywords, level, location, workplace, date posted, `needsSponsorship`). For a shortlist, call `get-jobs-by-ids` to read the requirements. Show company, title, location and date posted. If the user pastes a link, call `fetch-job-description` first.
3. **Confirm before applying.** Say which roles you will apply to and which résumé version (`list-resume-profiles`), and get an explicit yes. For a batch, check `get-application-balance` first. Then call `apply-to-job` with `jobIds` for several roles, or `jobId` or `url` for one. Tsenta tailors the résumé to each role using the user's saved mode (`get-apply-preferences`). Don't override the mode unless the user asks.
4. **Never apply twice.** After an error or a dropped connection, check `list-applications` or `get-application-status` before trying again. If the tool says a job was already applied to, stop and tell the user.
5. **Unblock waiting applications.** `list-applications` with `filter: "needs"` shows what waits on the user. For résumé or cover letter review, show the changes and call `approve-application` only after the user agrees. For a form paused before submit, call `get-application-review`, show the answers, then `submit-application-review`.
6. **Track and follow up.** Use `list-tracked-applications` and `update-tracked-application` for the tracker. Use `list-inbox-messages` (filter by `category`, such as `INTERVIEW` or `OFFER`) and `get-inbox-message` to summarize recruiter replies. Send a reply with `reply-to-inbox-message` only with text the user approved, and never add dates or times they did not give.
7. **Network.** `find-networking-contacts`, then `find-contact-email`, then `save-outreach-draft`. Tsenta never sends outreach. The user sends the draft from their own email or LinkedIn.

## Rules

- Sponsorship data is a signal from the posting or company, never a guarantee. Say "shows a sponsorship signal", not "sponsors you".
- Résumé tailoring follows the user's mode: Off, Honest or Aggressive. Don't add experience the user doesn't have.
- Report what actually happened, using `statusLabel` from `get-application-status`. "Submitted" means the employer's system received it. Nothing more.
- Auto Apply (`get-auto-apply-state`, `dry-run-auto-apply`, `commit-auto-apply-config`) needs the Power plan. Run a dry run and show the result before saving any change.
- For account or billing problems you can't solve, offer `escalate-to-support`.
