#!/usr/bin/env python3
"""
Leap 报关技能统一任务脚本。
合并了任务提交（POST /process）、轮询（GET /process/tasks/...）两个行为，
以此保证进程阻塞，直到任务最终 completed 或 failed，避免被跳过。
同时支持仅轮询已有任务的 poll 模式。

用法:
  分类任务 (单文件):
    python scripts/submit_and_poll.py --mode classify --file-id <id>
  分类任务 (多文件):
    python scripts/submit_and_poll.py --mode classify --file-id <id1> --file-id <id2>
  报关任务:
    python scripts/submit_and_poll.py --mode customs --json-data '{"files": [{"file_id": "...", "segments": [...]}]}'
  仅轮询已有任务:
    python scripts/submit_and_poll.py --mode poll --result-id <result_id>

零外部依赖 — 仅使用 Python 标准库。
"""
import json
import os
import sys
import time
import argparse
import urllib.request
import urllib.error

DEFAULT_BASE_URL = "https://platform.daofeiai.com"


def _request(method: str, url: str, api_key: str, json_body=None, timeout: int = 30) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"连接或请求失败: {e}")


def _poll_until_done(base_url: str, api_key: str, result_id: str,
                     interval: int, max_wait: int):
    """同步轮询阻塞，直到 completed / failed / 超时。"""
    poll_url = f"{base_url}/api/v1/process/tasks/{result_id}"
    start_time = time.time()
    time.sleep(5)  # 首次缓冲

    attempt = 0
    while True:
        attempt += 1
        elapsed = int(time.time() - start_time)

        if elapsed > max_wait:
            print(json.dumps({
                "status": "timeout",
                "result_id": result_id,
                "elapsed_seconds": elapsed,
                "message": f"等待超过 {max_wait} 秒，请稍后手动跟踪。",
                "manual_check": f'curl -H "Authorization: Bearer $LEAP_API_KEY" "{poll_url}"',
            }, ensure_ascii=False, indent=2))
            sys.exit(1)

        try:
            data = _request("GET", poll_url, api_key)
            status = data.get("status", "unknown")
            progress = data.get("progress", 0)

            print(json.dumps({
                "poll_attempt": attempt,
                "elapsed_seconds": elapsed,
                "status": status,
                "progress": progress,
            }, ensure_ascii=False), file=sys.stderr)

            if status == "completed":
                print(json.dumps(data, ensure_ascii=False, indent=2))
                sys.exit(0)

            if status == "failed":
                print(json.dumps({
                    "status": "failed",
                    "error_message": data.get("error_message", "未知错误"),
                    "result_id": result_id,
                    "elapsed_seconds": elapsed,
                    "suggestion": "请检查上传文件是否完整，或尝试重新提交任务。",
                }, ensure_ascii=False, indent=2))
                sys.exit(1)

        except RuntimeError as e:
            err_str = str(e)
            if "404" in err_str:
                print(json.dumps({
                    "status": "error",
                    "error_message": f"任务不存在: {result_id}，请检查 result_id 是否正确"
                }, ensure_ascii=False, indent=2))
                sys.exit(1)
            print(json.dumps({
                "poll_attempt": attempt,
                "elapsed_seconds": elapsed,
                "error": err_str
            }, ensure_ascii=False), file=sys.stderr)

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="同步提交并等待 Leap 流程任务")
    parser.add_argument("--mode", required=True, choices=["classify", "customs", "poll"],
                        help="任务模式: classify=分类, customs=报关, poll=仅轮询已有任务")
    parser.add_argument("--file-id", action="append", default=[], help="文件ID (classify 模式下可多次指定)")
    parser.add_argument("--json-data", help="报关所需的 segments 参数 JSON 字符串 (customs 模式必填)")
    parser.add_argument("--result-id", help="已有任务的 result_id (poll 模式必填)")
    parser.add_argument("--interval", type=int, default=8, help="轮询间隔（秒）")
    parser.add_argument("--max-wait", type=int, default=300, help="最长等待秒数")
    args = parser.parse_args()

    api_key = os.environ.get("LEAP_API_KEY", "")
    base_url = DEFAULT_BASE_URL

    if not api_key:
        print(json.dumps({
            "status": "error",
            "error_message": (
                "LEAP_API_KEY 未配置。\n"
                "请在 OpenClaw skill 设置界面配置 LEAP_API_KEY 环境变量。"
            )
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    # ── poll 模式：仅轮询已有任务 ──
    if args.mode == "poll":
        if not args.result_id:
            print("错误: poll 模式必须提供 --result-id", file=sys.stderr)
            sys.exit(1)
        _poll_until_done(base_url, api_key, args.result_id, args.interval, args.max_wait)
        return

    # ── classify / customs 模式：提交 + 轮询 ──
    payload = {}
    if args.mode == "classify":
        if not args.file_id:
            print("错误: 分类模式必须提供至少一个 --file-id", file=sys.stderr)
            sys.exit(1)
        payload["output"] = "classify_fast"
        payload["params"] = {
            "files": [{"file_id": fid} for fid in args.file_id]
        }
        payload["force_reprocess"] = True
    elif args.mode == "customs":
        if not args.json_data:
            print("错误: 报关模式必须提供 --json-data", file=sys.stderr)
            sys.exit(1)
        try:
            params_data = json.loads(args.json_data)
        except json.JSONDecodeError as e:
            print(f"错误: --json-data 格式不合法 - {e}", file=sys.stderr)
            sys.exit(1)

        payload["output"] = "customs"
        # 允许用户直接传整个 params，或者只传 {"files": [...]}
        if "files" in params_data:
            payload["params"] = params_data
        else:
            payload["params"] = {"files": params_data}
        payload["force_reprocess"] = True

    # 提交任务
    submit_url = f"{base_url}/api/v1/process"
    try:
        submit_resp = _request("POST", submit_url, api_key, json_body=payload)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "stage": "submit",
            "error_message": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    result_id = submit_resp.get("result_id")
    if not result_id:
        print(json.dumps({
            "status": "error",
            "stage": "submit",
            "error_message": "未从提交接口返回 result_id"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    print(json.dumps({"stage": "submitted", "result_id": result_id}, ensure_ascii=False), file=sys.stderr)

    # 同步轮询
    _poll_until_done(base_url, api_key, result_id, args.interval, args.max_wait)

if __name__ == "__main__":
    main()
