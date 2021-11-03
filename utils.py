import logging
import sys
import os
from ipaddress import ip_interface, ip_address
from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils.exceptions import InvalidFileException

logger = logging.getLogger()


def is_valid_ip_interface(gateway: str) -> str:
    """Validate a string is a valid IP address"""
    try:
        return ip_interface(gateway)
    except ValueError:
        error = f"{gateway} is not a valid IP address"
        logger.error(error)
        sys.exit(error)


def is_ip_in_network(ip: str, interfaces: list) -> bool:
    """Return True is IP is a member of the gateway networks"""
    for interface in interfaces:
        network = interface.network
        server_ip = ip_address(ip)
        if server_ip in network:
            return True
    return False


def get_next_hop_ip(ip: str, interfaces: list):
    """Return Gateway IP if IP is a member of the gateway networks"""
    for interface in interfaces:
        network = interface.network
        server_ip = ip_address(ip)
        if server_ip in network:
            return interface


def is_destination_on_same_network(destination: str, interface: str) -> bool:
    """Return True if destination route exists on same network as interface"""
    destination_address = ip_address(destination)
    network = interface.network
    return destination_address in network


def build_windows_route(destination: str, mask: str, next_hop: str, metric: str) -> str:
    """build string for adding new route to windows server"""

    if is_destination_on_same_network(destination, next_hop):
        logger.info(
            f"Route {destination} is on the same network as the interface and will be skipped."
        )

    else:
        return (
            f"route -p add {destination} mask {mask} {str(next_hop.ip)} metric {metric}"
        )


def open_workbook(location: str) -> Workbook:
    """try to open the workbook"""
    logger.info("Trying to load workbook")
    try:
        return load_workbook(location, read_only=False)
    except FileNotFoundError as exc:
        error = f"Unable to open workbook at location {location}"
        logger.error(error)
        sys.exit(error)
    except InvalidFileException as exc:
        error = f"File {location} is not in the correct format."
        logger.error(error)
        sys.exit(error)
    except Exception as exc:
        error = "Unable to load workbook."
        logger.error(error)
        logger.error(str(exc))
        sys.exit(error)


def set_active_sheet(workbook: Workbook, sheet_name: str) -> Worksheet:
    logger.info(f"Trying to load worksheet {sheet_name}")
    try:
        return workbook[sheet_name]
    except ValueError as exc:
        error = f"Sheet {sheet_name} not found in workbook."
        logger.error(error)
        sys.exit(error)
    except KeyError:
        error = f"Sheet {sheet_name} not found in workbook."
        logger.error(error)
        sys.exit(error)


def save_routes(server_routes: dict) -> None:
    """Save Routes to the output folder"""
    for server_name, server_options in server_routes.items():
        domain = server_options.get("domain", "UNKNOWN")
        routes = server_options.get("config", [])

        # Only create file if there are routes to add.
        if bool(routes):
            filename = f"output/{domain}/{server_name}.txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write("\n".join(routes))
