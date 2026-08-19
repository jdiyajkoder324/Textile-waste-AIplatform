import socket

# Force IPv4 for all socket connections — fixes "Errno 101: Network is unreachable"
# on Render's free tier, which has broken IPv6 outbound routing.
_original_getaddrinfo = socket.getaddrinfo
def _getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _getaddrinfo_ipv4

import smtplib