# Installing and updating Northbeam software

This page covers installing the Northbeam desktop client and keeping it up to date.

## First-time installation

1. Download the installer for your OS (Windows/macOS) from the Northbeam downloads portal —
   always use the link from your account dashboard, not a third-party mirror.
2. Run the installer with administrator/admin privileges. Standard user accounts can install
   but may be prompted for an admin password by your OS.
3. On first launch, sign in with your Northbeam account credentials. The client will
   auto-configure based on your plan.
4. If the installer is blocked by antivirus or endpoint protection, this is usually a false
   positive on new releases — add an exception for the Northbeam installer, or wait 24 hours
   for signature databases to catch up.

## Updating

The client checks for updates automatically on launch and prompts you to install. To check
manually: Help → Check for Updates.

- Updates typically install in under a minute and require a restart of the client (not your
  computer).
- If an update repeatedly fails to install, try: fully quitting the client (not just closing
  the window), then relaunching before retrying the update.
- Corporate machines with restricted install permissions may need updates pushed by IT rather
  than self-installed — check with your local IT admin first if updates are consistently
  blocked.

## Common installation errors

- "Installer is corrupted": re-download — the file was likely interrupted mid-download.
- "Insufficient permissions": re-run the installer as administrator.
- Client won't launch after install: restart your machine, then relaunch. If it still won't
  launch, check the crash log at the client's Help → Open Log Folder.

## When to contact support

Contact support with your OS version, client version (Help → About), and any error text or
log file if: installation fails after a clean re-download, updates consistently fail after a
full restart, or the client crashes on launch.
