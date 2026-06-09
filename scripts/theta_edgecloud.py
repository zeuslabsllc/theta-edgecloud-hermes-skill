#!/usr/bin/env python3
"""Minimal Theta EdgeCloud helper for Hermes skills.

Dependency-free by design: uses Python stdlib only. Keeps credentials in env vars
and never prints secrets.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

ONDEMAND_BASE = "https://ondemand.thetaedgecloud.com"


def env(name: str) -> Optional[str]:
    val = os.environ.get(name)
    return val if val else None


def ondemand_token() -> Optional[str]:
    return env("THETA_ONDEMAND_API_TOKEN") or env("THETA_ONDEMAND_API_KEY") or env("THETA_API_KEY")


def json_out(obj: Any) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True))


def capabilities(_: argparse.Namespace) -> int:
    caps = {
        "controller_project_apis": {
            "configured": bool(env("THETA_EC_API_KEY") and env("THETA_EC_PROJECT_ID")),
            "required": ["THETA_EC_API_KEY", "THETA_EC_PROJECT_ID"],
        },
        "org_balance": {
            "configured": bool(env("THETA_EC_API_KEY") and env("THETA_ORG_ID")),
            "required": ["THETA_EC_API_KEY", "THETA_ORG_ID"],
        },
        "ondemand": {
            "configured": bool(ondemand_token()),
            "required_any": ["THETA_ONDEMAND_API_TOKEN", "THETA_ONDEMAND_API_KEY", "THETA_API_KEY"],
        },
        "dedicated_inference": {
            "configured": bool(env("THETA_INFERENCE_ENDPOINT") and (env("THETA_INFERENCE_AUTH_TOKEN") or (env("THETA_INFERENCE_AUTH_USER") and env("THETA_INFERENCE_AUTH_PASS")))),
            "required": ["THETA_INFERENCE_ENDPOINT", "THETA_INFERENCE_AUTH_TOKEN OR THETA_INFERENCE_AUTH_USER+THETA_INFERENCE_AUTH_PASS"],
        },
        "video_api": {
            "configured": bool(env("THETA_VIDEO_SA_ID") and env("THETA_VIDEO_SA_SECRET")),
            "required": ["THETA_VIDEO_SA_ID", "THETA_VIDEO_SA_SECRET"],
        },
        "dry_run": env("THETA_DRY_RUN") == "1",
    }
    json_out(caps)
    return 0


def setup(_: argparse.Namespace) -> int:
    print("Theta EdgeCloud setup checklist")
    print("1. Log in: https://www.thetaedgecloud.com/")
    print("2. Account -> Projects -> select project -> Create API Key")
    print("3. Set THETA_EC_API_KEY and THETA_EC_PROJECT_ID for controller/deployment features")
    print("4. Set THETA_ONDEMAND_API_TOKEN or THETA_ONDEMAND_API_KEY for on-demand models")
    print("5. Set THETA_INFERENCE_ENDPOINT + auth token/user/pass for dedicated inference")
    print("6. Set THETA_DRY_RUN=1 for safer first runs")
    print("Run: python scripts/theta_edgecloud.py capabilities")
    return 0


def request_json(method: str, url: str, *, headers: Optional[Dict[str, str]] = None, payload: Any = None, timeout: int = 120) -> Any:
    body = None
    req_headers = {"Accept": "application/json", **(headers or {})}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
            if not raw.strip():
                return {"status": r.status, "body": ""}
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"status": r.status, "text": raw}
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        raise SystemExit(json.dumps({"error": "http_error", "status": e.code, "url": url, "body": text[:1000]}, indent=2))
    except urllib.error.URLError as e:
        raise SystemExit(json.dumps({"error": "url_error", "url": url, "reason": str(e.reason)}, indent=2))


def ondemand_headers(require: bool = True) -> Dict[str, str]:
    tok = ondemand_token()
    if not tok and require:
        raise SystemExit("Missing on-demand token: set THETA_ONDEMAND_API_TOKEN, THETA_ONDEMAND_API_KEY, or THETA_API_KEY")
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def ondemand_list_services(args: argparse.Namespace) -> int:
    data = request_json("GET", f"{ONDEMAND_BASE}/service/list?expand=template_id", headers=ondemand_headers(require=False), timeout=args.timeout)
    json_out(data)
    return 0


def parse_chat_text(data: Any) -> str:
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict) and msg.get("content"):
                return str(msg["content"])
        out = data.get("output")
        if isinstance(out, dict):
            for key in ("message", "text", "content"):
                if out.get(key):
                    return str(out[key])
    return json.dumps(data, indent=2)


def ondemand_chat(args: argparse.Namespace) -> int:
    if env("THETA_DRY_RUN") == "1" or args.dry_run:
        json_out({"dry_run": True, "service": args.service, "message": args.message, "would_call": "Theta on-demand chat"})
        return 0
    headers = ondemand_headers(require=True)
    messages = [{"role": "user", "content": args.message}]
    if args.service == "gpt_oss_120b":
        payload = {"model": "gpt_oss_120b", "messages": messages, "stream": False}
        data = request_json("POST", f"{ONDEMAND_BASE}/infer_request/chat/completions", headers=headers, payload=payload, timeout=args.timeout)
    else:
        payload = {"input": {"messages": messages}}
        if args.variant:
            payload["variant"] = args.variant
        url = f"{ONDEMAND_BASE}/infer_request/{urllib.parse.quote(args.service)}?prediction=completions"
        data = request_json("POST", url, headers=headers, payload=payload, timeout=args.timeout)
    if args.json:
        json_out(data)
    else:
        print(parse_chat_text(data))
    return 0


def inference_headers() -> Dict[str, str]:
    token = env("THETA_INFERENCE_AUTH_TOKEN")
    user = env("THETA_INFERENCE_AUTH_USER")
    pw = env("THETA_INFERENCE_AUTH_PASS")
    if token:
        return {"Authorization": f"Bearer {token}"}
    if user and pw:
        encoded = base64.b64encode(f"{user}:{pw}".encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
    raise SystemExit("Missing dedicated inference auth: set THETA_INFERENCE_AUTH_TOKEN or THETA_INFERENCE_AUTH_USER+THETA_INFERENCE_AUTH_PASS")


def inference_base() -> str:
    ep = env("THETA_INFERENCE_ENDPOINT")
    if not ep:
        raise SystemExit("Missing THETA_INFERENCE_ENDPOINT")
    return ep.rstrip("/")


def dedicated_models(args: argparse.Namespace) -> int:
    retries = max(1, args.retries)
    for attempt in range(1, retries + 1):
        try:
            data = request_json("GET", f"{inference_base()}/v1/models", headers=inference_headers(), timeout=args.timeout)
            json_out(data)
            return 0
        except SystemExit as e:
            if attempt >= retries:
                raise
            print(f"Readiness attempt {attempt}/{retries} failed; retrying in {args.sleep}s...", file=sys.stderr)
            time.sleep(args.sleep)
    return 1


def dedicated_chat(args: argparse.Namespace) -> int:
    if env("THETA_DRY_RUN") == "1" or args.dry_run:
        json_out({"dry_run": True, "model": args.model, "message": args.message, "would_call": "dedicated /v1/chat/completions"})
        return 0
    payload = {"model": args.model, "messages": [{"role": "user", "content": args.message}], "stream": False}
    data = request_json("POST", f"{inference_base()}/v1/chat/completions", headers=inference_headers(), payload=payload, timeout=args.timeout)
    if args.json:
        json_out(data)
    else:
        print(parse_chat_text(data))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Theta EdgeCloud helper for Hermes")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(func=setup)
    sub.add_parser("capabilities").set_defaults(func=capabilities)

    s = sub.add_parser("ondemand-list-services")
    s.add_argument("--timeout", type=int, default=60)
    s.set_defaults(func=ondemand_list_services)

    s = sub.add_parser("ondemand-chat")
    s.add_argument("--service", default="qwen3")
    s.add_argument("--variant")
    s.add_argument("--message", required=True)
    s.add_argument("--timeout", type=int, default=120)
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=ondemand_chat)

    s = sub.add_parser("dedicated-models")
    s.add_argument("--timeout", type=int, default=30)
    s.add_argument("--retries", type=int, default=6)
    s.add_argument("--sleep", type=int, default=15)
    s.set_defaults(func=dedicated_models)

    s = sub.add_parser("dedicated-chat")
    s.add_argument("--model", default="default")
    s.add_argument("--message", required=True)
    s.add_argument("--timeout", type=int, default=120)
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=dedicated_chat)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
