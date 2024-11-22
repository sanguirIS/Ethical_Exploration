import socket

def port_scanner(target, ports):
    print(f"Scanning target: {target}")
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        if result == 0:
            print(f"Port {port} is open")
        sock.close()

# Example usage
target = "example.com"
ports = [21, 22, 80, 443, 8080]
port_scanner(target, ports)