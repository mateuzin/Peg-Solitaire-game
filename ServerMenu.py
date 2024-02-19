import threading
import socket
import tkinter as tk
import sys


def get_local_addrees():
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


ip, port = get_local_addrees()

print(ip)
print(port)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen()

    clients = []
    nicknames = []

    def broadcast(message):
        for client in clients:
            client.send(message)

    def handle(client):
        while (True):
            try:
                message = client.recv(2048)
                broadcast(message)
            except:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'{nickname}: Saiu do Jogo!'.encode('utf-8'))
                nicknames.remove(nickname)
                break

    def receive():
        while True:
            client, address = server.accept()
            print("Conectado com " + str(address))

            client.send("NOME".encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)

            print("Nome do Cliente: " + str(nickname))

            broadcast(f'{nickname} Entrou na Partida\n'.encode('utf-8'))
            client.send('**Conectado com servidor**'.encode('utf-8'))

            thread = threading.Thread(target=handle, args=(client,))
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
