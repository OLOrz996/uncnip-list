#!/usr/bin/env python3
"""Generate CN and non-CN IPv4 CIDR lists from chnroutes2 data."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import pathlib
import urllib.request


CHNROUTES2_URL = "https://raw.githubusercontent.com/misakaio/chnroutes2/master/chnroutes.txt"


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "uncnip-list-generator/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


def parse_cn_ipv4_networks(routes_text: str) -> list[ipaddress.IPv4Network]:
    networks: list[ipaddress.IPv4Network] = []

    for line in routes_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        network = ipaddress.ip_network(line, strict=False)
        if network.version != 4:
            continue
        networks.append(network)

    return list(ipaddress.collapse_addresses(networks))


def invert_ipv4_networks(
    networks: list[ipaddress.IPv4Network],
) -> list[ipaddress.IPv4Network]:
    remaining = [ipaddress.IPv4Network("0.0.0.0/0")]

    for network in networks:
        next_remaining: list[ipaddress.IPv4Network] = []
        for candidate in remaining:
            if not candidate.overlaps(network):
                next_remaining.append(candidate)
            elif network.subnet_of(candidate):
                next_remaining.extend(candidate.address_exclude(network))
            elif candidate.subnet_of(network):
                continue
            else:
                next_remaining.append(candidate)
        remaining = next_remaining

    return list(ipaddress.collapse_addresses(remaining))


def write_networks(path: pathlib.Path, networks: list[ipaddress.IPv4Network]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(f"{network}\n" for network in networks)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_metadata(
    path: pathlib.Path,
    source_url: str,
    cn_networks: list[ipaddress.IPv4Network],
    uncn_networks: list[ipaddress.IPv4Network],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cn_content = "".join(f"{network}\n" for network in cn_networks)
    metadata = {
        "source": "misakaio/chnroutes2",
        "source_url": source_url,
        "cn_routes_sha256": hashlib.sha256(cn_content.encode("utf-8")).hexdigest(),
        "cn_ipv4_count": len(cn_networks),
        "non_cn_ipv4_count": len(uncn_networks),
    }
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CN and non-CN IPv4 CIDR lists.")
    parser.add_argument("--source-url", default=CHNROUTES2_URL)
    parser.add_argument("--cn-output", default="dist/cnip.txt")
    parser.add_argument("--uncn-output", default="dist/uncnip.txt")
    parser.add_argument("--metadata-output", default="dist/source.json")
    args = parser.parse_args()

    routes_text = fetch_text(args.source_url)
    cn_networks = parse_cn_ipv4_networks(routes_text)
    uncn_networks = invert_ipv4_networks(cn_networks)

    write_networks(pathlib.Path(args.cn_output), cn_networks)
    write_networks(pathlib.Path(args.uncn_output), uncn_networks)
    write_metadata(
        pathlib.Path(args.metadata_output),
        args.source_url,
        cn_networks,
        uncn_networks,
    )

    print(f"CN IPv4 networks: {len(cn_networks)}")
    print(f"Non-CN IPv4 networks: {len(uncn_networks)}")
    print(f"Wrote {args.cn_output}")
    print(f"Wrote {args.uncn_output}")
    print(f"Wrote {args.metadata_output}")


if __name__ == "__main__":
    main()
