#!/usr/bin/env python3
"""Check whether IP addresses belong to generated CN or non-CN lists."""

from __future__ import annotations

import argparse
import ipaddress
import pathlib


def load_networks(path: pathlib.Path) -> list[ipaddress._BaseNetwork]:
    networks: list[ipaddress._BaseNetwork] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        networks.append(ipaddress.ip_network(line))
    return networks


def find_match(
    ip: ipaddress._BaseAddress,
    networks: list[ipaddress._BaseNetwork],
) -> ipaddress._BaseNetwork | None:
    for network in networks:
        if ip.version == network.version and ip in network:
            return network
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Check generated IP list membership.")
    parser.add_argument("ips", nargs="+", help="IP addresses to check.")
    parser.add_argument("--cn-list", default="dist/cnip.txt")
    parser.add_argument("--uncn-list", default="dist/uncnip.txt")
    args = parser.parse_args()

    cn_networks = load_networks(pathlib.Path(args.cn_list))
    uncn_networks = load_networks(pathlib.Path(args.uncn_list))

    for value in args.ips:
        ip = ipaddress.ip_address(value)
        cn_match = find_match(ip, cn_networks)
        uncn_match = find_match(ip, uncn_networks)

        if cn_match and uncn_match:
            print(f"{ip}: conflict cnip={cn_match} uncnip={uncn_match}")
        elif cn_match:
            print(f"{ip}: cnip {cn_match}")
        elif uncn_match:
            print(f"{ip}: uncnip {uncn_match}")
        else:
            print(f"{ip}: not found")


if __name__ == "__main__":
    main()
