# Setting up your email client (IMAP/SMTP)

Email client setup is included on every Northbeam plan (Basic and above). Use these settings
to configure Outlook, Apple Mail, Thunderbird, or any standard IMAP/SMTP client.

## Server settings

- **Incoming (IMAP):** imap.northbeamit.com, port 993, SSL/TLS
- **Outgoing (SMTP):** smtp.northbeamit.com, port 587, STARTTLS
- **Username:** your full Northbeam email address
- **Password:** your Northbeam account password (or an app-specific password if you have MFA
  enabled — see below)

## App-specific passwords (MFA accounts)

If your account has multi-factor authentication enabled, your regular password will not work
in a mail client. Generate an app-specific password instead: Account Settings → Security →
App Passwords → Generate New. Use this generated password in place of your account password
when configuring the client.

## Common setup issues

- **"Cannot connect to server"**: double-check the port and encryption type match exactly
  (IMAP must be SSL/TLS on 993; SMTP must be STARTTLS on 587). Some networks block
  non-standard ports — try from a different network to isolate this.
- **"Authentication failed"**: if MFA is enabled, confirm you're using an app-specific
  password, not your regular login password.
- **Emails send but don't receive, or vice versa**: this usually means only one of IMAP/SMTP
  is misconfigured — re-check both sets of settings independently.
- **Mobile devices**: use the same settings above; most phone mail apps auto-detect these
  once you enter your email address, but manual entry works identically.

## When to contact support

Contact support if authentication continues to fail with a correct app-specific password, or
if your client connects but folders/mail fail to sync after 30+ minutes. Include your client
name/version and the exact error message.
