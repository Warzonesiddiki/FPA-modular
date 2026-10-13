# 18 — END-USER GUIDE (FP&A Analyst)

> Written for the analyst, in plain language. This guide ships in-app (S15 Help) — screenshots are added at release (doc 16 checklist). Advisory: this tool helps you prepare and review numbers; a qualified finance professional should review the final pack before it is used outside the company.

## 1. Your first 10 minutes (sample data)
1. Open the app → **Projects** → open **Sample Company** (fictional data, safe to explore — nothing you do here affects real work).
2. Follow the banner **"Run your first month-end"**. It walks you: Import → Checks → Statements → Variances → Exceptions → Forecast → Exports.
3. On each screen, try clicking a number — everything drills down to the vouchers and the exact file and row behind it. That drill is your safety net in every review meeting.

## 2. Starting a real project
Projects → **New project** → name it (e.g., "Acme — FY27"), pick your currency and financial-year start month → Create. Keep each company's work in its own project folder. **Back up by copying the whole project folder** (Settings → Backup does this for you and checks the copy).

## 3. The monthly routine (the whole job, in order)
1. **Import (S03).** Drop this month's files: GL export, budget, any sub-ledgers. Pick the period and file type for each. If you imported last month, your column mapping is already applied — just eyeball it. Fix anything under **Validate**: quarantined rows are listed with the reason in plain words and what to do (e.g., "Account code not in your chart of accounts — add it or fix the file"). Nothing is ever silently skipped: the counts always add up (rows in = rows loaded + rows quarantined).
2. **Trial balance (S05).** The month unlocks when debits equal credits per company. If not, click the imbalance to see the vouchers causing it. Fix in your ERP and re-import the corrected file (re-import replaces — it never double-counts), or record a waiver note if you consciously proceed.
3. **Statements (S06).** Review P&L / Balance Sheet / Cash Flow. Toggle month/YTD and ₹/₹'000. Click any line to drill.
4. **Variances (S07).** Budget vs Actual, with favourable/adverse in words. Material variances (your thresholds — changeable in Settings) are highlighted. Add your explanation in the commentary box; if AI is switched on in Settings, **Draft with AI** proposes wording from these exact numbers — edit it, then Approve. Only approved commentary appears in exports.
5. **Exceptions (S08).** Work the inbox: each item is a *potential* exception ("worth a look"), with the evidence and the voucher drill attached. Assign an owner, add notes, mark Explained/Corrected, or Waive with a reason (waivers expire and come back — that's deliberate). High-severity items block period lock until handled or consciously overridden.
6. **Forecast (S09).** The app back-tests its methods on your history and shows accuracy (MAPE) per group before you trust a number. Adjust drivers in Scenarios (S10) for upside/downside — the base forecast is never overwritten.
7. **Exports (S11).** Generate the **Excel pack** (12 sheets incl. checks and full drill data) and the **Board deck (PPT)**. If any check fails, the app tells you which and why, and blocks the deck — fix the source, regenerate. PDFs for quick sharing.
8. **Lock the period** (header → Lock) when done. Locked periods can't be silently changed; unlocking leaves an audit trail (S14).

## 4. Making next month faster (the point of the tool)
Mapping profiles, thresholds, owners, and methods are all remembered. A normal month 2+ should be: drop files → confirm → review exceptions → refresh forecast → export. If you're re-doing setup, something's wrong — check Help.

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

## 7. Words we use
**Potential exception** — something worth a human look; not an accusation. **Quarantine** — rows held back with a reason, never deleted. **Snapshot** — the exact data your exports were generated from, stamped on every file. **Locked period** — closed month; changes only via audited unlock.
