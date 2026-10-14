# 18 — END-USER GUIDE (FP&A Analyst)

> Written for the analyst, in plain language. This guide ships in-app (S15 Help) — screenshots are added at release (doc 16 checklist). Advisory: this tool helps you prepare and review numbers; a qualified finance professional should review the final pack before it is used outside the company.

## 1. Your first 10 minutes (sample data)
1. Open the app → **Projects** → create/open **Sample Company** (fictional data, safe to explore — nothing you do here affects real work). Creating it prepares a separate empty sample workspace and its fiscal years, not a finished set of books.
2. Follow the banner **"Run your first month-end"**. It walks you: Import → Checks → Statements → Variances → Exceptions → Forecast → Exports. At the Import step, load the bundled masters first, then the GL, budget and other sample files through the normal validation/commit steps. You can drop the sample files **or** click **Connect to the demo ledger (local)** and **Pull this month** — that is exactly what the Dynamics 365 connection does with your real ledger, demonstrated on a pretend one that runs on your own computer.
3. On each screen, try clicking a number — everything drills down to the vouchers and the exact file and row behind it. That drill is your safety net in every review meeting.

## 2. Starting a real project
Projects → **New project** → name it (e.g., "Acme — FY27"), pick a supported currency, financial-year start month and initial fiscal year (the year it starts, e.g. 2026 for Apr-2026…Mar-2027) → Create. Add another fiscal year in Periods when needed; simply viewing the list never creates one. Keep each company's work in its own project folder. **Back up by copying the whole project folder** (Settings → Backup does this for you and checks the copy).

**Connect Dynamics 365 once (optional, recommended).** Settings → **Connections** → pick *Finance / F&O* or *Business Central*, paste the environment URL and the two IDs your IT administrator gives you (see §8), click **Sign in with Microsoft** (your normal Microsoft login opens in your browser — the app never sees your password), then **Test connection**: it lists the companies you can read and confirms it found every table it needs. Pick your company. Done — from now on the monthly import is one click. The connection is **read-only**: the app can never post, change or delete anything in Dynamics 365, it never connects in the background, and your sign-in is kept in Windows Credential Manager, not in the project file. If IT prefers no personal sign-in, they can give you an *application* ID and secret instead (same screen, "Application" mode).

## 3. The monthly routine (the whole job, in order)
1. **Import (S03).** Connected to Dynamics 365? Choose **Dynamics 365 → Pull this month** (or **Refresh this month** on the dashboard): the app reads the period's GL, vendor transactions and trial balance straight from your company and lands them in the same Validate step as a file — nothing is committed until you say so. Pull again any time: if nothing changed in Dynamics 365 it tells you so; if it did, the new pull replaces the old one and shows you the difference first. Not connected, or need something the connection doesn't cover (e.g. budgets in Business Central)? Drop this month's files: GL export, budget, any sub-ledgers. Pick the period and file type for each. If you imported last month, your column mapping is already applied — just eyeball it. Fix anything under **Validate**: quarantined rows are listed with the reason in plain words and what to do (e.g., "Account code not in your chart of accounts — add it or fix the file"). Nothing is ever silently skipped: the counts always add up (rows in = rows loaded + rows quarantined).
2. **Trial balance (S05).** The month unlocks when debits equal credits per company. If not, click the imbalance to see the vouchers causing it. Fix in your ERP and re-import the corrected file (re-import replaces — it never double-counts), or record a waiver note if you consciously proceed.
3. **Statements (S06).** Review P&L / Balance Sheet / Cash Flow. Toggle month/YTD and ₹/₹'000. Click any line to drill.
4. **Variances (S07).** Budget vs Actual, with favourable/adverse in words. Material variances (your thresholds — changeable in Settings) are highlighted. Add your explanation in the commentary box; if AI is switched on in Settings, **Draft with AI** proposes wording from these exact numbers — edit it, then Approve. Only approved commentary appears in exports.
5. **Exceptions (S08).** Work the inbox: each item is a *potential* exception ("worth a look"), with the evidence and the voucher drill attached — and a **Suggested fix**: what entry would put it right (reverse, move to another account or cost centre, re-post at the corrected amount, book the accrual…), with the numbers it is based on and a confidence level. Four hygiene checks read the ledger the way you would: narration that doesn't match the account, an amount far outside a vendor's usual range (decimal slips), a cost centre the account never uses, and the same vendor billed twice days apart. For each suggestion: **Apply as adjustment** (a management-view correction inside the app, the ledger stays untouched), **Add to journal export** (collect corrections for the ERP), or **Not applicable** with a note. Assign an owner, add notes, mark Explained/Corrected, or Waive with a reason (waivers expire and come back — that's deliberate). High-severity items block period lock until handled or consciously overridden.
   **Dynamics 365 users:** export *Voucher transactions* for the month and, for vendor-level checks, *Vendor transactions* for the same dates; import both — the app fills in vendors by voucher. Attach the *Trial balance* export to the GL import and the app ties out every account before anything is committed.
6. **Forecast (S09).** The app back-tests its methods on your history and shows accuracy (MAPE) per group before you trust a number. Adjust drivers in Scenarios (S10) for upside/downside — the base forecast is never overwritten.
7. **Exports (S11).** Generate the **Excel pack** (12 sheets incl. checks and full drill data) and the **Board deck (PPT)**. If any check fails, the app tells you which and why, and blocks the deck — fix the source, regenerate. PDFs for quick sharing.
8. **Rectification journal (S11).** When the inbox is worked, generate the **journal file** of everything you queued, in your ERP's journal-import shape (Dynamics 365 Finance / Business Central / generic CSV). Import it in the ERP, review, post. Next month, when the corrections come back in the GL export, the app recognises them and offers to mark the items verified.
9. **Lock the period** (header → Lock) when done. Locked periods can't be silently changed; unlocking leaves an audit trail (S14).

## 4. Making next month faster (the point of the tool)
Mapping profiles, thresholds, owners, and methods are all remembered. A normal month 2+ should be: pull from Dynamics 365 (or drop files) → confirm → review exceptions → refresh forecast → export. If you're re-doing setup, something's wrong — check Help.

## 5. Settings worth knowing
Thresholds (what counts as "material", spike limits, approval limit for split-detection) — Settings explains each in one line and what changing it does. AI: off unless you add your own provider key; when off, nothing leaves your laptop (nothing leaves it anyway except those AI calls you explicitly enable). Data location: shown in Settings → About — that's the folder to back up.

## 6. Troubleshooting
| What you see | What it means / do this |
|---|---|
| "Control totals do not match" | The totals you declared differ from the file. Check you picked the right file/period; correct the declared totals or the file. Your staging is saved — nothing was committed. |
| Rows quarantined | Listed one-by-one with reasons and fixes in the Validate step. The month can proceed only when you've seen them — fix or consciously proceed where allowed. |
| "Trial balance does not balance" | S05 shows the imbalance by account/voucher. Usually a missing leg in the ERP export. |
| A rule says "not run" | It needs data you haven't imported (e.g., budget or prior periods). The reason is shown — import it or ignore consciously. |
| Excel generated but PPT blocked | A check failed (Checks sheet in Excel names it). The deck is blocked on purpose so a wrong number never reaches the board. |
| Audit verification failed | Don't work in that project. Restore your latest backup (Settings) and contact support with a diagnostics bundle (Help → Download diagnostics — it contains no financial values). |
| SmartScreen warning on install (pilot builds) | Click "More info → Run anyway" only if you received the installer directly from your project owner. |
| "Microsoft sign-in didn't complete" (with an AADSTS code) | Your administrator hasn't finished the one-time setup (§8), or consent is needed. Send them the exact text shown — it names the missing permission. The file import works meanwhile. |
| "Your Microsoft sign-in has expired" | Normal after a long gap or a password change. Click **Sign in again** — nothing else changes. |
| "{n} entities or fields weren't found in your Dynamics 365" | Your Dynamics 365 names a table or column differently (customisations do this). Pick the replacement from the list, or ask your administrator which entity holds it; the choice is saved once. |
| "Dynamics 365 is busy and kept asking us to wait" | Throttling. Try again in a few minutes, pull one source at a time, or pull outside business hours. |
| "Dynamics 365 changed while we were reading it" | Someone was posting during the pull; nothing was imported. Pull again in a moment. |

## 7. Words we use
**Pull** — reading this month straight from Dynamics 365 into the Validate step; it never changes anything in Dynamics 365. **Potential exception** — something worth a human look; not an accusation. **Quarantine** — rows held back with a reason, never deleted. **Snapshot** — the exact data your exports were generated from, stamped on every file. **Locked period** — closed month; changes only via audited unlock.

## 8. For your IT administrator — the one-time Dynamics 365 setup (≈15 minutes)
This is the full list; the detailed version with exact menu names is doc 26 §8.9.
1. In **Microsoft Entra ID → App registrations**, create a *public client* (mobile/desktop) registration with redirect URI `http://localhost`. Give the analyst the **Application (client) ID** and **Directory (tenant) ID**.
2. Add the API permission for the product — *Dynamics ERP* (Finance / F&O) or *Dynamics 365 Business Central* (delegated) — and grant admin consent if your tenant requires it. Access is further limited by the analyst's own security role / permission set in the product; a **read-only or reporting role is enough** — the app only reads.
3. Only if you prefer a service identity instead of the analyst's sign-in: add a client secret or certificate and register the application inside the product (F&O: *System administration → Microsoft Entra ID applications*; Business Central: *Microsoft Entra Applications*) with a read-only role. The analyst pastes the secret once; it is stored in Windows Credential Manager.
4. Nothing to open on the firewall beyond what Office already uses: the app talks only to `login.microsoftonline.com` and your Dynamics 365 host, over HTTPS, only when the analyst clicks.
The app never posts, edits or deletes anything in Dynamics 365, never connects in the background, and sends no telemetry.

## 9. Removing a project
Projects → Delete asks for the exact project name and refuses while work or a download is active. It signs that project out and moves the folder to private trash for at least 30 days; an offline computer purges on a later app start. The project disappears from normal lists immediately after successful deletion. Separately saved exports/backups are not erased. Deleting a sample uses the same confirmation and retention rules. If the action fails, follow the retry guidance; do not assume files or credentials were removed.
