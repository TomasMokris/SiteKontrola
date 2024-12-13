import psutil
import socket
from tabulate import tabulate
import argparse
import time

def get_network_connections(filter_ip=None, filter_port=None, show_only_active=False):
    connections = psutil.net_connections(kind='inet')
    result = []

    for conn in connections:
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
        status = conn.status
        proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP" if conn.type == socket.SOCK_DGRAM else "Other"

        if show_only_active and status != "ESTABLISHED":
            continue

        if filter_ip and (filter_ip not in laddr and filter_ip not in raddr):
            continue

        if filter_port and (str(filter_port) not in laddr and str(filter_port) not in raddr):
            continue

        result.append([proto, laddr, raddr, status])

    return result

def print_connections_table(connections):
    headers = ["Protocol", "Local Address", "Remote Address", "Status"]
    print(tabulate(connections, headers=headers, tablefmt="grid"))

def log_connections_to_file(connections, filename="network_log.txt"):
    with open(filename, "a") as log_file:
        log_file.write(tabulate(connections, headers=["Protocol", "Local Address", "Remote Address", "Status"], tablefmt="plain"))
        log_file.write("\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sledování a výpis síťové aktivity.")
    parser.add_argument("--filter-ip", help="Filtrovat podle IP adresy.", type=str)
    parser.add_argument("--filter-port", help="Filtrovat podle portu.", type=int)
    parser.add_argument("--show-only-active", help="Zobrazit pouze aktivní připojení.", action="store_true")
    parser.add_argument("--log", help="Logovat síťovou aktivitu do souboru.", action="store_true")
    parser.add_argument("--interval", help="Interval mezi výpisy v sekundách.", type=int, default=0)

    args = parser.parse_args()

    try:
        while True:
            connections = get_network_connections(
                filter_ip=args.filter_ip,
                filter_port=args.filter_port,
                show_only_active=args.show_only_active
            )

            print_connections_table(connections)

            if args.log:
                log_connections_to_file(connections)

            if args.interval > 0:
                time.sleep(args.interval)
            else:
                break
    except KeyboardInterrupt:
        print("\nUkončeno uživatelem.")
