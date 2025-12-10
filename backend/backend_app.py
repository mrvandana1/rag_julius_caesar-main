from flask import Flask, request, jsonify
from calculator import sqrt, factorial, ln, power

app = Flask(__name__)

@app.get("/")
def health():
    return {"status": "calculator backend running"}, 200

@app.post("/compute")
def compute():
    data = request.json
    op = data.get("operation")

    try:
        if op == "sqrt":
            result = sqrt(data["x"])
        elif op == "factorial":
            result = factorial(data["n"])
        elif op == "ln":
            result = ln(data["x"])
        elif op == "power":
            result = power(data["x"], data["b"])
        else:
            return jsonify({"error": "unknown operation"}), 400

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

app.run(host="0.0.0.0", port=8000)
