"""
core/servers.py
Gestion de la liste des serveurs (lecture JSON local) + tests réseau simples.
"""

from __future__ import annotations
import json
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import List, Optional

SERVERS_FILE = os.path.join("assets", "servers.json")

@dataclass
class Server:
    name: str
    url: str
    region: Optional[str] = None

def load_servers() -> List[Server]:
    """
    Lit assets/servers.json et retourne une liste de Server.
    Format attendu:
    [
      {"name":"Primary CDN","url":"https://github.com/KaRyuuuu/RIS_App/releases/latest/download","region":"EU"},
      ...
    ]
    """
    if not os.path.exists(SERVERS_FILE):
        return []
    with open(SERVERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    servers: List[Server] = []
    for item in data:
        name = item.get("name") or "Unnamed"
        url = item.get("url") or ""
        region = item.get("region")
        servers.append(Server(name=name, url=url, region=region))
    return servers

def head_ping(url: str, timeout: float = 5.0) -> tuple[bool, float, str]:
    """
    Effectue une requête HEAD (si supportée) pour mesurer la latence.
    Retourne (ok, latency_ms, err_msg).
    - ok: True si code HTTP 200-399
    - latency_ms: temps mesuré en millisecondes (ou -1 si échec)
    - err_msg: texte d'erreur si échec
    """
    req = urllib.request.Request(url, method="HEAD")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode() or 0
            latency = (time.perf_counter() - start) * 1000.0
            ok = 200 <= code < 400
            return (ok, latency, "" if ok else f"HTTP {code}")
    except urllib.error.HTTPError as e:
        latency = (time.perf_counter() - start) * 1000.0
        return (False, latency, f"HTTPError {e.code}")
    except urllib.error.URLError as e:
        return (False, -1.0, f"URLError {e.reason}")
    except Exception as e:
        return (False, -1.0, str(e))
