# Lab 3 
# Anushka Gangal
# NYU ID: AG10464

import socket
import os

DB_FILE = "dns_records.txt"
PORT = 53533


def save_record(name, value, type_, ttl):
    records = load_all_records()
    records[name] = {"value": value, "type": type_, "ttl": ttl}
    with open(DB_FILE, "w") as f:
        for n, data in records.items():
            f.write(
                f"{data['type']} {n} {data['value']} {data['ttl']}\n"
            )


def load_all_records():
    records = {}
    if not os.path.exists(DB_FILE):
        return records
    with open(DB_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 4:
                type_, name, value, ttl = parts
                records[name] = {
                    "type": type_,
                    "value": value,
                    "ttl": ttl,
                }
    return records


def parse_message(message):
    lines = message.strip().split("\n")
    data = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "=" in line:
            parts = line.split()
            for part in parts:
                if "=" in part:
                    key, val = part.split("=", 1)
                    data[key.strip()] = val.strip()
    return data


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))
    print(f"AS listening on UDP port {PORT}...")

    while True:
        message, addr = sock.recvfrom(4096)
        message = message.decode("utf-8")
        print(f"Received from {addr}:\n{message}")

        data = parse_message(message)

        if "VALUE" in data:
            name = data.get("NAME")
            value = data.get("VALUE")
            type_ = data.get("TYPE")
            ttl = data.get("TTL", "10")

            if name and value and type_:
                save_record(name, value, type_, ttl)
                response = "Registration successful"
                print(f"Registered: {name} -> {value}")
            else:
                response = "Bad registration request"

            sock.sendto(response.encode("utf-8"), addr)

        else:
            name = data.get("NAME")
            type_ = data.get("TYPE")
            records = load_all_records()

            if name and name in records:
                record = records[name]
                response = (
                    f"TYPE={record['type']}\n"
                    f"NAME={name} "
                    f"VALUE={record['value']} "
                    f"TTL={record['ttl']}\n"
                )
                print(f"Responding to query for {name}: {record['value']}")
            else:
                response = "Record not found"
                print(f"No record found for {name}")

            sock.sendto(response.encode("utf-8"), addr)


if __name__ == "__main__":
    main()
