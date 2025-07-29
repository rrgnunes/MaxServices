import socket

def listener():
    print('Iniciando Servidor')
    ip_server = '177.153.69.3'
    port = 3307
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip_server, port))
    server.listen()

    print(f'Escutando na porta: {port}')

    while True:
        client_socket, client_address = server.accept()

        print(f'Conexão recebida de: {client_address}')

        receiv = client_socket.recv(1024).decode('utf-8')

        client_socket.send(b'')

        client_socket.close()

if __name__ == '__main__':
    listener()
