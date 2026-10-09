import socket
import json

def start_server():
    try:
        # Create a socket object
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the server's IP and port
        server_socket.bind(('0.0.0.0', 8080))  # Listen on all available interfaces on port 8080
        
        # Listen for incoming connections (up to 1 client at a time)
        server_socket.listen(1)
        print("Server listening on port 8080...")
        
        while True:
            # Accept a new client connection
            client_socket, client_address = server_socket.accept()
            print(f"Connection received from {client_address}")

            try:
                # Receive the data in chunks (maximum 1024 bytes at a time)
                data = client_socket.recv(1024)

                if data:
                    # Decode the received data (JSON format)
                    json_data = data.decode('utf-8')

                    # Parse the JSON data
                    entry = json.loads(json_data)

                    # Extract and print the received values
                    print("Received data:")
                    print(f"Raspberry Pi ID: {entry.get('raspberry_pi_id')}")
                    print(f"Raspberry Pi IP: {entry.get('raspberry_pi_ip')}")
                    print(f"Class of Animal: {entry.get('class_of_animal')}")
                    print(f"Timestamp: {entry.get('time_stamp')}")
                    print(f"Location: {entry.get('location')}")
                else:
                    print("No data received from client.")

            except Exception as e:
                print(f"Failed to process data: {e}")
            
            # Close the connection with the client
            client_socket.close()

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        # Close the server socket
        server_socket.close()

if __name__ == "__main__":
    start_server()
