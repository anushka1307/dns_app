# Lab 3 
# Anushka Gangal
# NYU ID: AG10464

import socket
from flask import Flask, request, jsonify

app = Flask(__name__)

PORT = 9090


def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def register_with_as(hostname, ip, as_ip, as_port):
    message = (
        f"TYPE=A\n"
        f"NAME={hostname} VALUE={ip} TTL=10\n"
    )
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    try:
        sock.sendto(
            message.encode("utf-8"),
            (as_ip, int(as_port))
        )
        response, _ = sock.recvfrom(4096)
        print(f"AS response: {response.decode('utf-8')}")
        return True
    except Exception as e:
        print(f"Error registering with AS: {e}")
        return False
    finally:
        sock.close()


@app.route("/register", methods=["PUT"])
def register():
    body = request.get_json()

    if not body:
        return "Bad Request: missing JSON body", 400

    hostname = body.get("hostname")
    ip = body.get("ip")
    as_ip = body.get("as_ip")
    as_port = body.get("as_port")

    if not all([hostname, ip, as_ip, as_port]):
        return "Bad Request: missing fields", 400

    success = register_with_as(hostname, ip, as_ip, as_port)

    if success:
        return "Registered successfully", 201
    else:
        return "Failed to register with AS", 500


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    number = request.args.get("number")

    if number is None:
        return "Bad Request: missing number parameter", 400

    try:
        n = int(number)
    except ValueError:
        return "Bad Request: number must be an integer", 400

    result = fibonacci(n)
    return jsonify({"fibonacci": result}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
