"""
Port availability checker utility for the backend application.
Provides functions to check if a port is available and find alternative ports.
"""
import socket
from typing import Optional


def is_port_available(port: int, host: str = "localhost") -> bool:
    """
    Check if a port is available for binding.

    Args:
        port: The port number to check
        host: The host to check (default: localhost)

    Returns:
        True if the port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_available_port(starting_port: int, max_attempts: int = 10, host: str = "localhost") -> Optional[int]:
    """
    Find an available port starting from a given port number.

    Args:
        starting_port: The port number to start checking from
        max_attempts: Maximum number of ports to try (default: 10)
        host: The host to check (default: localhost)

    Returns:
        An available port number, or None if no available port is found
    """
    for port in range(starting_port, starting_port + max_attempts):
        if is_port_available(port, host):
            return port
    return None


def get_port_with_fallback(default_port: int = 8000, host: str = "localhost") -> int:
    """
    Get a port that is available, falling back to alternatives if the default is busy.

    Args:
        default_port: The preferred port number (default: 8000)
        host: The host to check (default: localhost)

    Returns:
        An available port number
    """
    if is_port_available(default_port, host):
        return default_port

    # Try to find an alternative port
    alternative_port = find_available_port(default_port + 1, 20, host)
    if alternative_port:
        print(f"Warning: Port {default_port} is not available, using port {alternative_port} instead.")
        return alternative_port
    else:
        # If no alternative found, raise an exception
        raise RuntimeError(f"No available ports found starting from {default_port}")