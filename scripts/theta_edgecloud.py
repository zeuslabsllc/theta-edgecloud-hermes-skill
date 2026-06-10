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
CONTROLLER_BASE = "https://controller.thetaedgecloud.com"
EDGE_API_BASE = "https://api.thetaedgecloud.com"

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    # Theta controller APIs are Cloudflare-fronted and may reject Python's default urllib UA.
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}

SENSITIVE_KEY_PARTS = (
    "authorization",
    "auth_password",
    "api_key",
    "apikey",
    "bearer",
    "key",
    "password",
    "registry_password",
    "secret",
    "token",
)


def env(name: str) -> Optional[str]:
    val = os.environ.get(name)
    return val if val else None


def ondemand_token() -> Optional[str]:
    return env("THETA_ONDEMAND_API_TOKEN") or env("THETA_ONDEMAND_API_KEY") or env("THETA_API_KEY")


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def redact(obj: Any, *, parent_key: str = "") -> Any:
    """Recursively redact secret-like values before printing helper output."""
    if is_sensitive_key(parent_key):
        return "[REDACTED]"
    if isinstance(obj, dict):
        return {k: redact(v, parent_key=str(k)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v, parent_key=parent_key) for v in obj]
    return obj


def redact_text(text: str) -> str:
    try:
        parsed = json.loads(text)
        return json.dumps(redact(parsed), sort_keys=True)[:1000]
    except Exception:
        return text[:1000]


def json_out(obj: Any) -> None:
    print(json.dumps(redact(obj), indent=2, sort_keys=True))


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
    req_headers = {**DEFAULT_HEADERS, **(headers or {})}
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
        raise SystemExit(json.dumps(redact({"error": "http_error", "status": e.code, "url": url, "body": redact_text(text)}), indent=2))
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


def first_infer_request(data: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(data, dict):
        return None
    body = data.get("body")
    if isinstance(body, dict):
        reqs = body.get("infer_requests")
        if isinstance(reqs, list) and reqs and isinstance(reqs[0], dict):
            return reqs[0]
    return None


def poll_ondemand_request(request_id: str, *, timeout: int, interval: int, request_timeout: int = 60) -> Any:
    deadline = time.time() + timeout
    last = None
    while True:
        data = request_json("GET", f"{ONDEMAND_BASE}/infer_request/{urllib.parse.quote(request_id)}", headers=ondemand_headers(require=True), timeout=request_timeout)
        last = data
        req = first_infer_request(data)
        state = req.get("state") if req else None
        if state in {"success", "error", "failed", "cancelled"}:
            return data
        if time.time() >= deadline:
            return {"status": "timeout", "last": last}
        time.sleep(max(1, interval))


def ondemand_infer(args: argparse.Namespace) -> int:
    try:
        payload = json.loads(args.payload_json)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid --payload-json: {e}")
    if env("THETA_DRY_RUN") == "1" or args.dry_run:
        json_out({"dry_run": True, "service": args.service, "prediction": args.prediction, "payload": payload})
        return 0
    params = []
    if args.prediction:
        params.append(("prediction", args.prediction))
    if args.wait is not None:
        params.append(("wait", str(args.wait)))
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    data = request_json("POST", f"{ONDEMAND_BASE}/infer_request/{urllib.parse.quote(args.service)}{qs}", headers=ondemand_headers(require=True), payload=payload, timeout=args.timeout)
    if args.poll:
        req = first_infer_request(data)
        request_id = req.get("id") if req else None
        if request_id:
            data = poll_ondemand_request(request_id, timeout=args.poll_timeout, interval=args.poll_interval, request_timeout=args.timeout)
    json_out(data)
    return 0


def ondemand_status(args: argparse.Namespace) -> int:
    if args.poll:
        data = poll_ondemand_request(args.request_id, timeout=args.timeout, interval=args.interval, request_timeout=args.request_timeout)
    else:
        data = request_json("GET", f"{ONDEMAND_BASE}/infer_request/{urllib.parse.quote(args.request_id)}", headers=ondemand_headers(require=True), timeout=args.request_timeout)
    json_out(data)
    return 0


def controller_headers(require: bool = True) -> Dict[str, str]:
    key = env("THETA_EC_API_KEY")
    if not key and require:
        raise SystemExit("Missing controller API key: set THETA_EC_API_KEY")
    return {"x-api-key": key} if key else {}


def project_id() -> str:
    pid = env("THETA_EC_PROJECT_ID")
    if not pid:
        raise SystemExit("Missing THETA_EC_PROJECT_ID")
    return pid


def controller_url(base: str, path: str, params: Dict[str, Any]) -> str:
    clean = {k: v for k, v in params.items() if v is not None}
    qs = urllib.parse.urlencode(clean, doseq=True)
    return f"{base}{path}{'?' + qs if qs else ''}"


def controller_list_deployments(args: argparse.Namespace) -> int:
    params: Dict[str, Any] = {"project_id": args.project_id or project_id()}
    if args.template_name:
        params["template_name"] = args.template_name
    if args.not_template_name:
        params["not_template_name"] = args.not_template_name
    data = request_json("GET", controller_url(CONTROLLER_BASE, "/deployment/list", params), headers=controller_headers(require=True), timeout=args.timeout)
    json_out(data)
    return 0


def controller_standard_templates(args: argparse.Namespace) -> int:
    data = request_json("GET", controller_url(CONTROLLER_BASE, "/deployment_template/list_standard_templates", {"category": args.category, "page": args.page, "number": args.number}), headers=controller_headers(require=True), timeout=args.timeout)
    json_out(data)
    return 0


def controller_custom_templates(args: argparse.Namespace) -> int:
    data = request_json("GET", controller_url(CONTROLLER_BASE, "/deployment_template/list_custom_templates", {"project_id": args.project_id or project_id()}), headers=controller_headers(require=True), timeout=args.timeout)
    json_out(data)
    return 0


def controller_vm_types(args: argparse.Namespace) -> int:
    data = request_json("GET", f"{EDGE_API_BASE}/resource/vm/list", headers=controller_headers(require=False), timeout=args.timeout)
    json_out(data)
    return 0


def controller_balance(args: argparse.Namespace) -> int:
    org_id = args.org_id or env("THETA_ORG_ID")
    if not org_id:
        raise SystemExit("Missing org id: set THETA_ORG_ID or pass --org-id")
    data = request_json("GET", controller_url(EDGE_API_BASE, "/balance", {"orgID": org_id}), headers=controller_headers(require=True), timeout=args.timeout)
    json_out(data)
    return 0


def controller_create_deployment(args: argparse.Namespace) -> int:
    try:
        payload = json.loads(args.payload_json)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid --payload-json: {e}")
    if env("THETA_DRY_RUN") == "1" or args.dry_run:
        json_out({"dry_run": True, "would_call": "POST /deployment", "payload": payload})
        return 0
    if not args.yes:
        raise SystemExit("Refusing paid/mutating deployment create without --yes or THETA_DRY_RUN=1")
    data = request_json("POST", f"{CONTROLLER_BASE}/deployment", headers=controller_headers(require=True), payload=payload, timeout=args.timeout)
    json_out(data)
    return 0


def controller_delete_deployment(args: argparse.Namespace) -> int:
    if not args.deployment_id and not (args.shard and args.suffix):
        raise SystemExit("Provide either --deployment-id or both --shard and --suffix")
    if env("THETA_DRY_RUN") == "1" or args.dry_run:
        json_out({"dry_run": True, "deployment_id": args.deployment_id, "shard": args.shard, "suffix": args.suffix})
        return 0
    if not args.yes:
        raise SystemExit("Refusing deployment delete without --yes or THETA_DRY_RUN=1")
    pid = args.project_id or project_id()
    if args.deployment_id:
        url = controller_url(CONTROLLER_BASE, f"/deployment/base/{urllib.parse.quote(args.deployment_id)}", {"project_id": pid})
    else:
        url = controller_url(CONTROLLER_BASE, f"/deployment/{urllib.parse.quote(args.shard)}/{urllib.parse.quote(args.suffix)}", {"project_id": pid})
    data = request_json("DELETE", url, headers=controller_headers(require=True), timeout=args.timeout)
    json_out(data)
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
    parsed = urllib.parse.urlparse(ep)
    if parsed.scheme != "https":
        raise SystemExit("THETA_INFERENCE_ENDPOINT must be an https:// URL to avoid leaking endpoint credentials")
    return ep.rstrip("/")


def dedicated_models(args: argparse.Namespace) -> int:
    base = inference_base()
    headers = inference_headers()
    retries = max(1, args.retries)
    for attempt in range(1, retries + 1):
        try:
            data = request_json("GET", f"{base}/v1/models", headers=headers, timeout=args.timeout)
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


    s = sub.add_parser("ondemand-infer")
    s.add_argument("--service", required=True)
    s.add_argument("--payload-json", required=True)
    s.add_argument("--prediction")
    s.add_argument("--wait", type=int)
    s.add_argument("--timeout", type=int, default=120)
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--poll", action="store_true")
    s.add_argument("--poll-timeout", type=int, default=180)
    s.add_argument("--poll-interval", type=int, default=3)
    s.set_defaults(func=ondemand_infer)

    s = sub.add_parser("ondemand-status")
    s.add_argument("request_id")
    s.add_argument("--poll", action="store_true")
    s.add_argument("--timeout", type=int, default=180)
    s.add_argument("--interval", type=int, default=3)
    s.add_argument("--request-timeout", type=int, default=60)
    s.set_defaults(func=ondemand_status)

    s = sub.add_parser("controller-vm-types")
    s.add_argument("--timeout", type=int, default=60)
    s.set_defaults(func=controller_vm_types)

    s = sub.add_parser("controller-standard-templates")
    s.add_argument("--category", default="serving")
    s.add_argument("--page", type=int, default=0)
    s.add_argument("--number", type=int, default=10)
    s.add_argument("--timeout", type=int, default=60)
    s.set_defaults(func=controller_standard_templates)

    s = sub.add_parser("controller-custom-templates")
    s.add_argument("--project-id")
    s.add_argument("--timeout", type=int, default=60)
    s.set_defaults(func=controller_custom_templates)

    s = sub.add_parser("controller-list-deployments")
    s.add_argument("--project-id")
    s.add_argument("--template-name")
    s.add_argument("--not-template-name", action="append")
    s.add_argument("--timeout", type=int, default=60)
    s.set_defaults(func=controller_list_deployments)



    s = sub.add_parser("controller-balance")
    s.add_argument("--org-id")
    s.add_argument("--timeout", type=int, default=60)
    s.set_defaults(func=controller_balance)

    s = sub.add_parser("controller-create-deployment")
    s.add_argument("--payload-json", required=True)
    s.add_argument("--timeout", type=int, default=120)
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--yes", action="store_true", help="Required for real paid/mutating create")
    s.set_defaults(func=controller_create_deployment)

    s = sub.add_parser("controller-delete-deployment")
    s.add_argument("--project-id")
    s.add_argument("--deployment-id")
    s.add_argument("--shard")
    s.add_argument("--suffix")
    s.add_argument("--timeout", type=int, default=120)
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--yes", action="store_true", help="Required for real delete")
    s.set_defaults(func=controller_delete_deployment)

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



