# Exporting your data and backups

Self-service data export (**data_export**) is a Pro and Enterprise entitlement — see "What
each plan includes" if you're unsure of your current plan.

## Requesting an export

1. Go to Account → Data → Export Data.
2. Choose the scope: full account export, or a specific category (tickets, configuration,
   usage logs).
3. Choose a format: JSON (structured, best for re-import or automation) or CSV (best for
   spreadsheets).
4. Exports are generated asynchronously — you'll get an email with a secure download link
   when it's ready. Small exports (a single category) usually complete in minutes; full
   account exports can take up to a few hours for large accounts.
5. Download links expire after 72 hours for security. Request a new export if you miss the
   window.

## Automated/scheduled backups

Enterprise accounts can enable scheduled exports (daily/weekly) delivered automatically to a
configured storage destination (S3-compatible endpoint or SFTP). Configure this under
Account → Data → Scheduled Backups. This requires **api_access** to set up the destination
credentials.

## Basic-plan accounts

Basic accounts do not have self-service export. If you need your data (e.g., closing an
account, migrating), contact support — we can process a one-time manual export on request, or
you can upgrade to Pro for self-service access going forward.

## When to contact support

Contact support if: an export has been "processing" for more than 6 hours, a download link
returns an error before the 72-hour expiry, or you're on Basic and need a one-time manual
export.
