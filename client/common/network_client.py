"""
Network Client
Handles UDP communication with server
"""

import socket
from typing import Optional
from .byte_buffer import ByteBuffer
from .message_types import TIMEOUT_SECONDS, MAX_RETRIES, MAX_BUFFER_SIZE


class NetworkClient:
    """Handles network communication with the server."""
    
    def __init__(self, server_ip: str, server_port: int):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT_SECONDS)
        self.next_request_id = 1
    
    def get_next_request_id(self) -> int:
        """Get the next request ID and increment counter."""
        request_id = self.next_request_id
        self.next_request_id += 1
        return request_id
    
    def send_request(self, request_data: bytes, retries: int = MAX_RETRIES, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Send a request to the server and wait for a response.
        Implements retry logic for at-least-once semantics.
        
        Args:
            request_data: The request data to send
            retries: Number of retry attempts
            timeout: Optional custom timeout in seconds (uses default if None)
        """
        # Save original timeout
        original_timeout = self.sock.gettimeout()
        
        # Set custom timeout if provided
        if timeout is not None:
            self.sock.settimeout(timeout)
        
        try:
            for attempt in range(retries):
                try:
                    # Send request
                    self.sock.sendto(request_data, (self.server_ip, self.server_port))
                    
                    # Wait for response
                    response_data, _ = self.sock.recvfrom(MAX_BUFFER_SIZE)
                    return response_data
                    
                except socket.timeout:
                    if attempt < retries - 1:
                        print(f"Timeout, retrying... (attempt {attempt + 2}/{retries})")
                    else:
                        print("Request timeout after all retries")
                        return None
            
            return None
        finally:
            # Restore original timeout
            if timeout is not None:
                self.sock.settimeout(original_timeout)
    
    def close(self):
        """Close the socket."""
        self.sock.close()
