import sys
import threading
import socket
import tkinter as tk
from tkinter import simpledialog

def start_client(ip, port, nickname):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

    def receive():
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message == 'NOME':
                    client.send(nickname.encode('utf-8'))
                else:
                    print(message)
            except:
                print('Erro ao conectar')
                client.close()
                sys.exit()

    def write():
        while True:
            message = f'{nickname}: {input("")}'
            client.send(message.encode('utf-8'))

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()

# Função chamada quando o botão de conexão é clicado
def connect_button_clicked(ip_entry, port_entry, nickname_entry):
    ip = ip_entry.get()
    port = int(port_entry.get())
    nickname = nickname_entry.get()

    start_client(ip, port, nickname)
    root.destroy()  # Fecha a janela após a conexão

# Criando a interface de menu para o cliente
root = tk.Tk()
root.title("Cliente Menu")

# Componentes da interface
tk.Label(root, text="IP:").grid(row=0, column=0)
ip_entry = tk.Entry(root)
ip_entry.grid(row=0, column=1)

tk.Label(root, text="Porta:").grid(row=1, column=0)
port_entry = tk.Entry(root)
port_entry.grid(row=1, column=1)

tk.Label(root, text="Nome:").grid(row=2, column=0)
nickname_entry = tk.Entry(root)
nickname_entry.grid(row=2, column=1)

connect_button = tk.Button(root, text="Conectar", command=lambda: connect_button_clicked(ip_entry, port_entry, nickname_entry))
connect_button.grid(row=3, column=0, columnspan=2)

root.mainloop()
