import threading
import socket
import pygame_menu
import pygame
import sys


class Game_Server:
    def __init__(self):
        self.menu = None
        self.first_client_connected = False
        self.second_client_connected = False
        self.clients = []
        self.nicknames = []
        self.font_color = (128, 128, 128)
        self.server_state = "Ligar servidor"
        self.server_title_state = "OFF"
        self.on_off = self.start_server

        self.ip, self.port = self.get_local_address()
        self.port = 55555  # TESTE RETIRAR

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen()

        pygame.init()
        clock = pygame.time.Clock()

        surface = pygame.display.set_mode((350, 440))
        pygame.display.set_caption('RESTA UM - MENU')

        self.mytheme = pygame_menu.themes.Theme(background_color=(0, 0, 0, 0),
                                                title_background_color=(14, 36, 23),
                                                cursor_selection_color=(222, 252, 221),
                                                title_font_shadow=True,
                                                widget_padding=25,
                                                )
        self.create_menu()

        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.menu.update(events)
            surface.fill((14, 36, 23))
            self.menu.draw(surface)

            pygame.display.flip()
            clock.tick(30)

    def create_menu(self):
        self.menu = pygame_menu.Menu(f"SERVIDOR - {self.server_title_state}", 350, 440, theme=self.mytheme)

        self.menu.add.label(f'IP: {self.ip}', font_size=30, margin=(0, 0), font_color=self.font_color)
        self.menu.add.label(f'PORTA: {self.port}', font_size=30, margin=(0, 0), font_color=self.font_color)
        self.menu.add.button(self.server_state, self.on_off)
        self.menu.add.button('Sair', pygame_menu.events.EXIT)

    @staticmethod
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

    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(message)
                except:
                    continue

    def handle(self, client, nickname):
        while True:
            try:
                message = client.recv(4096)
                if not message:
                    break
                self.broadcast(message, client)
            except:
                break

        index = self.clients.index(client)
        self.clients.remove(client)
        client.close()
        nickname = self.nicknames[index]
        self.broadcast(f'{nickname} saiu do jogo.'.encode('utf-8'))

    def receive(self):
        while True:
            client, address = self.server.accept()

            if not self.first_client_connected:
                self.first_client_connected = True
                print("O primeiro cliente conectou.")
                client.send('FIRST_CLIENTMOVE'.encode('utf-8'))

            elif not self.second_client_connected:
                self.second_client_connected = True
                print("O segundo cliente conectou.")
                client.send('MOVE'.encode('utf-8'))

            else:
                print("Outro cliente tentou se conectar, mas o jogo já começou.")
                break

            print("Conectado com " + str(address))

            nickname = client.recv(4096).decode('utf-8')
            self.nicknames.append(nickname)
            self.clients.append(client)

            thread = threading.Thread(target=self.handle, args=(client, nickname))
            thread.start()

    def start_server(self):
        self.font_color = (136, 236, 36)
        self.server_state = "Desligar servidor"
        self.server_title_state = "ON"
        self.on_off = self.on_closing
        self.menu.disable()
        self.create_menu()
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        print("Servidor Ligado")

    def on_closing(self):
        for client in self.clients:
            try:
                client.close()
            except:
                continue
        self.server.close()
        Game_Server()


if __name__ == "__main__":
    server = Game_Server()
