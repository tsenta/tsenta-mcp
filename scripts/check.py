#!/usr/bin/env python3
"""Checks for this repository. Needs Python 3.11+ (for tomllib): `python3 scripts/check.py`.

- server.json is valid against the MCP Registry schema it names (needs `pip install jsonschema`; skipped if missing).
- Every example config parses and points at the server URL in server.json.
- Every tool named in README.md and SKILL.md is in the documented tool list in README.md.
- No em dashes in the docs.
- With --live: the server's OAuth discovery documents answer and name the same URL.
"""
import json
import pathlib
import re
import sys
import tomllib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []


def get_json(u):
    req = urllib.request.Request(u, headers={"User-Agent": "tsenta-mcp-repo-check/1.0 (+https://github.com/tsenta/tsenta-mcp)", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fail(msg):
    errors.append(msg)


server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
url = server["remotes"][0]["url"]

# 1. server.json against its schema
try:
    import jsonschema

    schema = get_json(server["$schema"])
    schema.pop("$schema", None)
    for e in jsonschema.Draft7Validator(schema).iter_errors(server):
        fail(f"server.json: {e.message} at {list(e.path)}")
    if len(server["description"]) > 100:
        fail("server.json: description is over 100 characters")
except ImportError:
    print("jsonschema not installed, skipping the schema check")

# 2. example configs: every URL in an example must be exactly the server URL
def urls_in(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from urls_in(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from urls_in(v)
    elif isinstance(obj, str) and obj.startswith(("http://", "https://")):
        yield obj


for path in sorted((ROOT / "examples").rglob("*")):
    if path.suffix == ".json":
        found = list(urls_in(json.loads(path.read_text(encoding="utf-8"))))
    elif path.suffix == ".toml":
        found = list(urls_in(tomllib.loads(path.read_text(encoding="utf-8"))))
    elif path.suffix == ".sh":
        text = path.read_text(encoding="utf-8")
        found = re.findall(r"https?://[^\s'\"]+", text)
        for blob in re.findall(r"'(\{.*?\})'", text):
            found = [u for u in found if u not in blob] + list(urls_in(json.loads(blob)))
    else:
        continue
    if not found or any(u != url for u in found):
        fail(f"{path.relative_to(ROOT)} must use exactly {url}, found {found}")

# 3. tool names: every `tool-name` used must be in a README tools table row
readme = (ROOT / "README.md").read_text(encoding="utf-8")
skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
tools_section = readme.split("## Tools", 1)[1].split("\n## ", 1)[0]
documented = set(re.findall(r"^\| `([a-z][a-z0-9-]+)` \|", tools_section, re.M))
token = re.compile(r"`([a-z]+(?:-[a-z0-9]+)+)`")
not_tools = {"streamable-http", "mcp-remote"}
for name, text in (("README.md", readme), ("SKILL.md", skill)):
    for t in set(token.findall(text)) - not_tools:
        if t not in documented:
            fail(f"{name} names `{t}`, which is not in the README tools tables")

# 4. em dashes in anything a user or directory shows
shown = [ROOT / "README.md", ROOT / "SKILL.md", ROOT / "SECURITY.md", ROOT / "examples" / "README.md", ROOT / "server.json"]
shown += sorted((ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml"))
for path in shown:
    if "—" in path.read_text(encoding="utf-8"):
        fail(f"{path.relative_to(ROOT)} has an em dash")

# 5. live discovery
if "--live" in sys.argv:
    base = url.split("/api/")[0]
    meta_url = f"{base}/.well-known/oauth-protected-resource/{url.split(base + '/', 1)[1]}"
    meta = get_json(meta_url)
    if meta.get("resource") != url:
        fail(f"{meta_url} names resource {meta.get('resource')}, not {url}")
    issuer = meta["authorization_servers"][0]
    auth = get_json(f"{issuer}/.well-known/oauth-authorization-server")
    if "registration_endpoint" not in auth:
        fail("authorization server does not advertise dynamic client registration")
    if "S256" not in auth.get("code_challenge_methods_supported", []):
        fail("authorization server does not advertise PKCE S256")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"ok: {len(documented)} documented tools, examples and server.json agree on {url}")
