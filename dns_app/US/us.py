import socket
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

PORT = 8080


def query_as(hostname, as_ip, as_port):
    message = f"TYPE=A\nNAME={hostname}\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    try:
        sock.sendto(
            message.encode("utf-8"),
            (as_ip, int(as_port))
        )
        response, _ = sock.recvfrom(4096)
        response = response.decode("utf-8")
        print(f"AS DNS response:\n{response}")

        for line in response.strip().split("\n"):
            parts = line.strip().split()
            for part in parts:
                if part.startswith("VALUE="):
                    return part.split("=", 1)[1]
        return None
    except Exception as e:
        print(f"Error querying AS: {e}")
        return None
    finally:
        sock.close()


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Bad Request: missing parameters", 400

    fs_ip = query_as(hostname, as_ip, as_port)

    if not fs_ip:
        return "Could not resolve hostname via AS", 500

    try:
        fs_url = (
            f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
        )
        print(f"Calling FS at: {fs_url}")
        response = requests.get(fs_url, timeout=5)

        if response.status_code == 200:
            return response.json(), 200
        else:
            return response.text, response.status_code

    except Exception as e:
        print(f"Error calling FS: {e}")
        return "Error contacting Fibonacci Server", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
