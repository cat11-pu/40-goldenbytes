"""check_http.py：起服务、按脚本走一圈，打印验收面。"""
import json
import sys
import threading
import urllib.error
import urllib.request

from server import serve


def call(method, url, body=None):
    request = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def parse(text):
    try:
        return json.loads(text)
    except Exception:
        return {"_raw": (text or "")[:60]}


def main() -> int:
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "sample/numbers.json", encoding="utf-8"))
    server = serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % server.server_port
    packed = parse(call("POST", base + "/pack_delta", json.dumps({"numbers": spec["numbers"]}).encode())[1])
    unpacked = parse(call("POST", base + "/unpack_delta",
                          json.dumps({"hex": packed.get("hex") or ""}).encode())[1])
    fixed = parse(call("POST", base + "/pack", json.dumps({"numbers": spec["numbers"]}).encode())[1])
    resynced = parse(call("POST", base + "/resync", json.dumps({"hex": spec["truncated_hex"]}).encode())[1])
    stats = parse(call("GET", base + "/stats")[1])
    print("变长差分编码（hex） =", packed.get("hex"))
    print("解回来的数 =", unpacked.get("numbers"))
    print("固定宽度编码（hex） =", fixed.get("hex"))
    print("固定宽度字节数 =", len(fixed.get("hex") or "") // 2)
    print("变长字节数 =", len(packed.get("hex") or "") // 2)
    print("压缩比（变长 / 固定） =", spec["ratio"])
    print("截断流恢复的条数 =", resynced.get("recovered"))
    print("截断流的断点偏移 =", resynced.get("offset"))
    print("版本兼容（version=1 仍可解） =", parse(call("POST", base + "/unpack_delta",
                                               json.dumps({"hex": spec["v1_hex"]}).encode())[1]).get("numbers"))
    print("不变量（往返一致） =", spec["roundtrip_ok"])
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
