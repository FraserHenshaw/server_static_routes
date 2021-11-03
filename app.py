import ipaddress
import logging
from logging import handlers, log
import json
from pathlib import Path
from utils import (
    build_windows_route,
    get_next_hop_ip,
    is_ip_in_network,
    is_valid_ip_interface,
    open_workbook,
    save_routes,
    set_active_sheet,
)

logging_handler = handlers.RotatingFileHandler(
    filename="output.log",
    mode="a",
    maxBytes=5 * 1024 * 1024,
    backupCount=2,
    encoding=None,
    delay=0,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
    handlers=[logging_handler],
)

logger = logging.getLogger("runner")

sheet_name = "Sheet1"

col_mapping = {
    "hostname": 0,
    "domain": 1,
    "ip_address": 2,
    "destination": 11,
    "mask": 15,
    "metric": 16,
    "nexthop": 22,
}

skipped_names = ["NULL", "LOCALHOST"]

skipped_ips = ["NULL"]

skipped_routes = [
    "127.0.0.0",
    "127.0.0.1",
    "224.0.0.0",
    "255.255.255.255",
    "127.255.255.255",
]

nexthop_check = "0.0.0.0"


def main():
    servers = {}
    next_hops = []

    next_hop_pathlist = Path("next_hops").glob("**/*.txt")
    logger.info("Looping over files in folder 'next_hops' and adding as next hops")
    for next_hop_path in next_hop_pathlist:
        logger.debug(f"Opening file at path {next_hop_path}")
        with open(next_hop_path, "r") as file:
            next_hops.extend(
                [is_valid_ip_interface(ip.strip("\n")) for ip in file.readlines()]
            )

    pathlist = Path("input").glob("**/*.xlsx")
    logger.info("Looping over files in folder 'input'")
    for path in pathlist:
        logger.debug(f"Opening file at path {path}")
        workbook = open_workbook(path)
        worksheet = set_active_sheet(workbook, sheet_name)

        logger.info("Interating over file.")
        for index, row in enumerate(
            worksheet.iter_rows(min_row=2, values_only=True, max_col=25), start=2
        ):

            logger.info(f"Parsing row {index}")
            hostname = row[col_mapping["hostname"]]
            domain = row[col_mapping["domain"]]
            ip_address = row[col_mapping["ip_address"]].split(",")[0]
            mask = row[col_mapping["mask"]]
            next_hop = row[col_mapping["nexthop"]]
            destination = row[col_mapping["destination"]]
            metric = row[col_mapping["metric"]]

            if hostname in skipped_names:
                logger.debug(
                    f"skipping row as hostname: {hostname} in {','.join(skipped_names)}"
                )
                continue

            logger.info(f"Hostname: {hostname}")
            # Skip if IP address is NULL
            if ip_address in skipped_ips:
                logger.debug(
                    f"skipping row as ip_address: {ip_address} in {','.join(skipped_ips)}"
                )
                continue

            # Skip if Destination is in skipped destinations
            if destination in skipped_routes:
                logger.debug(
                    f"skipping row as route: {destination} in {','.join(skipped_routes)}"
                )
                continue

            # Skip if IP address not in part of any migration gateways
            if not is_ip_in_network(ip_address, next_hops):
                logger.debug(
                    f"skipping row as IP: {ip_address} in any of the gateway networks"
                )
                continue

            # Create server in servers dict if not present
            created = servers.get(hostname, False)
            if not created:
                servers.update({hostname: {"domain": domain, "config": []}})
            logger.info("Validating route and building new config")
            # Get next_hop ip address
            logger.info("Getting next hop IP")
            new_next_hop = get_next_hop_ip(ip_address, next_hops)
            if new_next_hop is None:
                logger.error("No valid next hop found.")
                pass
            else:
                logger.info(
                    f"Building new configuration for route {destination}/{mask}"
                )
                route = build_windows_route(destination, mask, new_next_hop, metric)
                if route is not None:
                    servers[hostname]["config"].append(route)

    logger.info("Saving Routes")
    save_routes(servers)


if __name__ == "__main__":
    main()
