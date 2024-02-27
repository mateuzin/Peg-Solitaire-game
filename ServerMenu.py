import threading
import socket
import tkinter as tk
import sys


def get_local_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.255.255.255', 1))
        ip_local = s.getsockname()[0]
        port_local = s.getsockname()[1]
    except:
        ip_local = '127.0.0.1'
        port_local = '8080'
    finally:
        s.close()
    return ip_local, port_local


ip, port = get_local_address()

port = 55555

print(ip)
print(port)

first_client_connected = False
second_client_connected = False

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen()

    clients = []
    nicknames = []

    def broadcast(message, sender=None):
        for client in clients:
            if client != sender and client.fileno() != -1:
                try:
                    client.send(message)
                except:
                    continue

    def handle(client, nickname):
        while True:
            try:
                message = client.recv(4096)
                if not message:
                    break
                broadcast(message, client)
            except:
                break

        index = clients.index(client)
        clients.remove(client)
        client.close()
        nickname = nicknames[index]
        broadcast(f'{nickname} saiu do jogo.'.encode('utf-8'))

    def receive():
        global first_client_connected, second_client_connected
        while True:
            client, address = server.accept()

            if not first_client_connected:
                first_client_connected = True
                print("O primeiro cliente conectou.")
                client.send('FIRST_CLIENTMOVE'.encode('utf-8'))

            elif not second_client_connected:
                second_client_connected = True
                print("O segundo cliente conectou.")
                client.send('MOVE'.encode('utf-8'))

            else:
                print("Outro cliente tentou se conectar, mas o jogo já começou.")
                break

            print("Conectado com " + str(address))

            nickname = client.recv(4096).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)

            thread = threading.Thread(target=handle, args=(client, nickname))
            thread.start()

    print("Servidor Ligado")
    receive()


# Criando a janela principal
root = tk.Tk()
root.title("Servidor Chat")

# EXIBIR IP E PORTA
ip_label = tk.Label(root, text="IP do Servidor: " + ip)
ip_label.pack()

port_label = tk.Label(root, text="Porta do Servidor: " + str(port))
port_label.pack()

start_button = tk.Button(root, text="Iniciar Servidor", command=start_server)
start_button.pack()


def on_closing():
    root.destroy()
    sys.exit()


root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
