import os.path
import socket
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
database_name = os.path.join(BASE_DIR, "DATABASE.db")
# database_name = "book_database.db"



def get_ip_address():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a remote server, in this case, Google's DNS server
        s.connect(('8.8.8.8', 80))
        # Get the local IP address connected to the remote server
        ip_address = s.getsockname()[0]
        # Close the socket
        s.close()
        return ip_address
    except socket.error:
        return "Unable to retrieve IP address"

# Example usage
PORT = "5001"
IP = get_ip_address()
IP_ADDRESS = 'http://'+get_ip_address()+":"+PORT
