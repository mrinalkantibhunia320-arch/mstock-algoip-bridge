import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "AlgoIP m.Stock Bridge is Live!", 200

@app.route("/mstock-proxy", methods=["POST"])
def mstock_proxy():
    data = request.get_json(force=True)
    method = str(data.get("method", "POST")).upper()
    target_url = data.get("target_url", "")
    headers = data.get("headers") or {}
    body = data.get("body", "")

    host = data.get("algoip_host", "")
    port = str(data.get("algoip_port", "443"))
    user = data.get("algoip_user", "")
    passwd = data.get("algoip_pass", "")

    schemes = ["https", "http"] if port == "443" else ["http"]
    last_err = ""

    for scheme in schemes:
        proxy_url = f"{scheme}://{user}:{passwd}@{host}:{port}"
        proxies = {"http": proxy_url, "https": proxy_url}
        try:
            resp = requests.request(
                method=method,
                url=target_url,
                headers=headers,
                data=body if method != "GET" else None,
                proxies=proxies,
                timeout=25,
            )
            return jsonify({
                "http_code": resp.status_code,
                "body": resp.text,
                "egress_ip": host
            }), 200
        except Exception as e:
            last_err = str(e)

    return jsonify({"http_code": 502, "body": f"Proxy Error: {last_err}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
