from urllib.parse import quote
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "AlgoIP m.Stock Bridge is Live!", 200

@app.route("/mstock-proxy", methods=["POST"])
def mstock_proxy():
    try:
        data = request.get_json(force=True) or {}
        method = str(data.get("method", "POST")).upper()
        target_url = str(data.get("target_url", "")).strip()
        headers = data.get("headers") or {}
        body = data.get("body", "")
        host = str(data.get("algoip_host", "")).strip()
        port = str(data.get("algoip_port", "443")).strip()
        user = quote(str(data.get("algoip_user", "")).strip(), safe="")
        passwd = quote(str(data.get("algoip_pass", "")).strip(), safe="")
        proxy_url = f"http://{user}:{passwd}@{host}:{port}"
        resp = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            data=body if method != "GET" else None,
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=(8, 12),
        )
        return jsonify({"http_code": resp.status_code, "body": resp.text, "egress_ip": host}), 200
    except Exception as e:
        return jsonify({"http_code": 502, "body": str(e)[-130:]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
