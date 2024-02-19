import tkinter as tk
from tkinter import simpledialog
import threading
import socket
import sys

class Cliente:
    def __init__(self, ip, port, nickname):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, port))

        self.receive_thread = threading.Thread(target=self.receive)
        self.write_thread = threading.Thread(target=self.write)

        self.nickname = nickname

        self.receive_thread.start()
        self.write_thread.start()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NOME':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    print(message)
            except:
                print('Erro ao conectar')
                self.client.close()

    def write(self):
        while True:
            message = f'{self.nickname}: {input("")}'
            self.client.send(message.encode('utf-8'))

class Servidor:
    def __init__(self):
        self.ip , self.port = self.get_local_addrees()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen()

        self.clients = []
        self.nicknames = []

        print("Servidor Ligado")
        print(self.ip)
        print(self.port)
        self.receive()

    def get_local_addrees(self):
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

    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle(self, client):
        while True:
            try:
                message = client.recv(2048)
                self.broadcast(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast(f'{nickname}: Saiu do Jogo!'.encode('utf-8'))
                self.nicknames.remove(nickname)
                break

    def receive(self):
        while True:
            client, address = self.server.accept()
            print("Conectado com " + str(address))

            client.send("NOME".encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            self.nicknames.append(nickname)
            self.clients.append(client)

            print("Nome do Cliente:" + str(nickname))

            self.broadcast(f'{nickname} Entrou na Partida\n'.encode('utf-8'))
            client.send('Conectado com Servidor'.encode('utf-8'))

            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()

class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Menu Principal")

        servidor_button = tk.Button(root, text="Servidor", command=self.iniciar_servidor)
        servidor_button.pack(pady=20)

        cliente_button = tk.Button(root, text="Cliente", command=self.iniciar_cliente)
        cliente_button.pack(pady=20)

    def iniciar_servidor(self):
        root = tk.Tk()
        root.title("Servidor Chat")

        servidor = Servidor()

        ip_label = tk.Label(root, text="IP do Servidor: " + servidor.ip)
        ip_label.pack()

        port_label = tk.Label(root, text="Porta do Servidor: " + str(servidor.port))
        port_label.pack()

        start_button = tk.Button(root, text="Iniciar Servidor", command=servidor.receive)
        start_button.pack()

        def on_closing():
            root.destroy()
            sys.exit()
        root.protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()

    def iniciar_cliente(self):
        root = tk.Tk()
        root.title("Cliente Menu")

        ip_label = tk.Label(root, text="IP:")
        ip_label.grid(row=0, column=0)
        ip_entry = tk.Entry(root)
        ip_entry.grid(row=0, column=1)

        port_label = tk.Label(root, text="Porta:")
        port_label.grid(row=1, column=0)
        port_entry = tk.Entry(root)
        port_entry.grid(row=1, column=1)

        nickname_label = tk.Label(root, text="Nome:")
        nickname_label.grid(row=2, column=0)
        nickname_entry = tk.Entry(root)
        nickname_entry.grid(row=2, column=1)

        connect_button = tk.Button(root, text="Conectar", command=lambda: Cliente(ip_entry.get(), int(port_entry.get()), nickname_entry.get()))
        connect_button.grid(row=3, column=0, columnspan=2)

        root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    menu_principal = MenuPrincipal(root)
    root.mainloop()
