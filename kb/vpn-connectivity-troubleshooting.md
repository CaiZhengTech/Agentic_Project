# Troubleshooting VPN connection drops

If you can't connect to the Northbeam VPN, or your connection drops mid-session, work through
these steps before contacting support.

## Can't connect at all

1. Confirm your internet connection works without the VPN (load any website).
2. Check the Northbeam status page for an active VPN outage (see "Checking service status
   and planned maintenance"). If there's a known incident, no further action is needed —
   we're already on it.
3. Restart the Northbeam VPN client (right-click the tray icon → Quit, then relaunch).
4. Confirm your credentials haven't expired — a locked account will also block VPN login
   (see "Resetting your password and unlocking your account").
5. If you're on a hotel, airport, or client-site network, some networks block the VPN's
   outbound port (UDP 1194). Switch the client to "TCP fallback" mode in Settings → Connection.

## Frequent disconnects

This is the most common VPN complaint we see, especially from remote and traveling staff.

1. Open the VPN client's connection log (Settings → Diagnostics → View Log) and check whether
   drops correlate with network switches (e.g., waking from sleep, switching Wi-Fi to
   cellular). If so, enable "Reconnect on network change" in Settings → Connection —
   this fixes the majority of cases.
2. Weak Wi-Fi signal or an overloaded home router can cause drops every few minutes. Try a
   wired connection or move closer to the router as a test.
3. Some consumer routers aggressively kill idle UDP sessions. Enabling "Keepalive" (Settings →
   Connection → Keepalive, default 25s) prevents the router from timing out the tunnel.
4. Corporate or public Wi-Fi with captive portals can silently drop VPN traffic. Reconnect to
   the network fully (including re-accepting any portal terms) before reconnecting the VPN.
5. If disconnects happen only on one specific network (e.g., a client site), that network's
   firewall may be the cause — TCP fallback mode (above) usually resolves this.

## When to contact support

Contact support with your VPN connection log attached if: disconnects persist after trying
"Reconnect on network change" and TCP fallback, the client crashes rather than disconnecting
cleanly, or you need **priority VPN support** — a Pro/Enterprise-only entitlement providing
same-day triage instead of standard queue order (see "What each plan includes"). Standard-plan
users are supported on a best-effort basis through the normal ticket queue.
