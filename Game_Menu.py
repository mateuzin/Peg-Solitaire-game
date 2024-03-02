import pygame
import pygame_menu
import sys
import threading
import time
import pickle
import socket


def login(Erro=None):
    def connect_button_clicked():
        ip = ip_entry.get_value()
        port = int(port_entry.get_value())
        nickname = nickname_entry.get_value()

        start_client(ip, port, nickname)

    pygame.init()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((400, 520))
    pygame.display.set_caption('RESTA UM - MENU')

    mytheme = pygame_menu.themes.Theme(
        background_color=(0, 0, 0, 0),
        title_background_color=(14, 36, 23),
        title_font_shadow=True,
        widget_padding=18,
        widget_alignment=pygame_menu.locals.ALIGN_LEFT
    )

    menu = pygame_menu.Menu('CLIENTE - LOGIN', 400, 520, theme=mytheme)

    if Erro == True:
        menu.add.label('IP ou Porta incorretos, verifique com o servidor', font_size=15, margin=(0, 0), font_color=(255, 0, 0))

    ip_entry = menu.add.text_input('IP: ', default="", maxchar=15, )
    port_entry = menu.add.text_input('Porta: ', default="", maxchar=6, input_type=pygame_menu.locals.INPUT_INT)
    nickname_entry = menu.add.text_input('Nome: ', default="", maxchar=15)

    menu.add.button('Iniciar', connect_button_clicked)
    menu.add.button('Voltar para Menu', main)
    menu.add.button('Sair', pygame_menu.events.EXIT)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        menu.update(events)
        screen.fill((14, 36, 23))
        menu.draw(screen)

        pygame.display.flip()
        clock.tick(30)


def start_client(ip, port, nickname):
    class Game_Client:
        def __init__(self):
            pygame.init()

            # Constantes
            self.WIDTH, self.HEIGHT = 600, 600
            self.BOARD_WIDTH = 605  # Largura do tabuleiro
            self.ROW_COUNT, self.COL_COUNT = 7, 7
            self.CELL_SIZE = self.BOARD_WIDTH // self.COL_COUNT
            self.FPS = 60

            # Variáveis
            self.selected_ball = None
            self.is_local_turn = False
            self.send_movement = None
            self.current_local_play = None

            # Cores e imagens
            self.BLACK = (0, 0, 0)
            self.LIGHT_GREEN = (222, 252, 221)
            self.DARK_GREEN = (14, 36, 23)
            self.font = pygame.font.Font(None, 80)

            # Inicializa a tela
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("RESTA UM")
            self.clock = pygame.time.Clock()

            # Cria o tabuleiro
            self.board = [
                [-1, -1, 1, 1, 1, -1, -1],
                [-1, -1, 1, 1, 1, -1, -1],
                [1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1],
                [-1, -1, 1, 1, 1, -1, -1],
                [-1, -1, 1, 1, 1, -1, -1],
            ]

            # SOCKET e Thread
            self.ip = ip
            self.port = port
            self.nickname = nickname
            self.client = None
            self.turn_event = threading.Event()

        def draw_board(self):
            # Desenha o tabuleiro
            self.screen.fill(self.LIGHT_GREEN)
            for row in range(self.ROW_COUNT):
                for col in range(self.COL_COUNT):
                    if self.board[row][col] == 1:
                        pygame.draw.circle(
                            self.screen,
                            self.DARK_GREEN,
                            (col * self.CELL_SIZE + self.CELL_SIZE // 2, row * self.CELL_SIZE + self.CELL_SIZE // 2),
                            self.CELL_SIZE // 3,
                        )
                    elif self.selected_ball is not None and (
                            self.board[row][col] == 0
                            and (
                                    (abs(self.selected_ball[0] - row) == 2 and self.selected_ball[1] == col
                                     and self.board[self.selected_ball[0] - (self.selected_ball[0] - row) // 2][
                                         col] == 1)
                                    or
                                    (abs(self.selected_ball[1] - col) == 2 and self.selected_ball[0] == row
                                     and self.board[row][
                                         self.selected_ball[1] - (self.selected_ball[1] - col) // 2] == 1)
                            )
                    ):
                        pygame.draw.circle(
                            self.screen,
                            (128, 128, 128),
                            (col * self.CELL_SIZE + self.CELL_SIZE // 2, row * self.CELL_SIZE + self.CELL_SIZE // 2),
                            self.CELL_SIZE // 3,
                        )
                    elif self.board[row][col] == -1:
                        pygame.draw.rect(
                            self.screen,
                            self.DARK_GREEN,
                            (col * self.CELL_SIZE, row * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE),
                        )

        def selected_piece(self):
            # Destaca a peça selecionada
            if self.selected_ball is not None:
                pygame.draw.circle(
                    self.screen,
                    (74, 96, 83),
                    (self.selected_ball[1] * self.CELL_SIZE + self.CELL_SIZE // 2,
                     self.selected_ball[0] * self.CELL_SIZE + self.CELL_SIZE // 2),
                    self.CELL_SIZE // 3,
                    50,
                )

        def valid_move(self, src_row, src_col, row, col):
            # Realiza a movimentação
            if (
                    abs(src_row - row) == 2
                    and src_col == col
                    and self.board[src_row - (src_row - row) // 2][col] == 1
            ):
                # Move a peça
                self.board[row][col] = 1
                self.board[src_row][src_col] = 0

                # Remove a peça pulada
                jumped_row, jumped_col = (src_row - (src_row - row) // 2, col)
                self.board[jumped_row][jumped_col] = 0

                self.selected_ball = None
                return True

            elif (
                    abs(src_col - col) == 2
                    and src_row == row
                    and self.board[row][src_col - (src_col - col) // 2] == 1
            ):
                # Move a peça
                self.board[row][col] = 1
                self.board[src_row][src_col] = 0

                # Remove a peça pulada
                jumped_row, jumped_col = (row, src_col - (src_col - col) // 2)
                self.board[jumped_row][jumped_col] = 0

                self.selected_ball = None
                return True

            return False

        def updateBoard(self, received_moves):
            # Atualiza o tabuleiro com as jogadas recebidas do servidor
            for move in received_moves:
                src_row, src_col, dest_row, dest_col = move
                self.valid_move(src_row, src_col, dest_row, dest_col)

        def check_available_moves(self):
            # Verifica movimentos disponíveis
            for row in range(self.ROW_COUNT):
                for col in range(self.COL_COUNT):
                    if self.board[row][col] == 1:
                        # Verifica possíveis movimentos para cada peça
                        for delta_row, delta_col in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                            new_row, new_col = row + delta_row, col + delta_col
                            jump_row, jump_col = row + delta_row // 2, col + delta_col // 2

                            # Verifica se o movimento é válido
                            if (
                                    0 <= new_row < self.ROW_COUNT
                                    and 0 <= new_col < self.COL_COUNT
                                    and self.board[new_row][new_col] == 0
                                    and self.board[jump_row][jump_col] == 1
                            ):
                                return True  # Pelo menos um movimento disponível

            return False  # Nenhum movimento disponível

        def draw_grid(self):
            # Desenha as linhas do grid
            for i in range(self.ROW_COUNT):
                pygame.draw.line(self.screen, self.DARK_GREEN, (0, i * self.CELL_SIZE),
                                 (self.BOARD_WIDTH - 10, i * self.CELL_SIZE))
            for j in range(self.COL_COUNT):
                pygame.draw.line(self.screen, self.DARK_GREEN, (j * self.CELL_SIZE - 1, 0),
                                 (j * self.CELL_SIZE, self.BOARD_WIDTH - 10))

        def start_client(self):
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client.connect((self.ip, self.port))
            except Exception as e:
                print(f'Erro ao conectar ao servidor: {e}')
                login(True)
                sys.exit()

            def receive():
                while True:
                    try:
                        move = self.client.recv(4096)
                        match move:
                            case b'FIRST_CLIENTMOVE':
                                print("Você é o primeiro a jogar.")
                                self.is_local_turn = True
                                self.turn_event.set()
                                self.client.send(self.nickname.encode('utf-8'))
                            case b'MOVE':
                                self.client.send(self.nickname.encode('utf-8'))
                                print(f"{self.nickname},aguarde o outro jogador.")
                            case default:
                                time.sleep(0.4)
                                move_data = pickle.loads(move)
                                # print(f"MOVE DATA{move_data}")#DEBUG
                                src_row = move_data['src_row']
                                src_col = move_data['src_col']
                                row = move_data['row']
                                col = move_data['col']

                                received_moves = [(src_row, src_col, row, col)]
                                self.updateBoard(received_moves)
                                if self.current_local_play != received_moves:
                                    self.is_local_turn = True

                    except Exception as e:
                        print(f'Erro ao receber do servidor: {e}')
                        self.client.close()
                        sys.exit()

            def write():
                while True:
                    try:
                        if self.send_movement is not None:
                            move_data = {
                                'src_row': self.send_movement[0],
                                'src_col': self.send_movement[1],
                                'row': self.send_movement[2],
                                'col': self.send_movement[3],
                            }
                            move = pickle.dumps(move_data)
                            # print(f"\nMOVE DENTRO DO WRITE: {move}")#DEBUG
                            self.client.send(move)
                            self.send_movement = None
                    except Exception as e:
                        print(f'Erro ao enviar para o servidor: {e}')
                        self.client.close()
                        sys.exit()

            receive_thread = threading.Thread(target=receive)
            receive_thread.start()

            write_thread = threading.Thread(target=write)
            write_thread.start()

        def run(self):
            self.start_client()
            run = True
            while run:
                # print(f"VEZ DO JOGADOR{self.is_local_turn}")#DEBUG
                pygame.event.pump()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_local_turn == True:
                        col = event.pos[0] // self.CELL_SIZE
                        row = event.pos[1] // self.CELL_SIZE

                        if self.is_local_turn == True:  # Se for a vez do cliente
                            print("Sua vez")
                            # Movimentos
                            if 0 <= row < self.ROW_COUNT and 0 <= col < self.COL_COUNT:
                                if self.selected_ball is None and self.board[row][col] == 1:
                                    self.selected_ball = (row, col)
                                elif self.selected_ball is not None and self.board[row][col] == 1:
                                    self.selected_ball = (row, col)
                                elif self.selected_ball is not None and self.board[row][col] == 0:
                                    src_row, src_col = self.selected_ball
                                    if self.valid_move(src_row, src_col, row, col):
                                        self.send_movement = src_row, src_col, row, col
                                        self.current_local_play = src_row, src_col, row, col
                                        print(f"JOGADA FEITA: {self.send_movement}")  # debug
                                        self.is_local_turn = False  # FEZ A JOGADA MUDA TURNO PARA FALSE
                                else:
                                    print("NÃO PODE")  # debug
                        else:
                            self.turn_event.wait()
                            self.turn_event.clear()
                            received_moves = []
                            self.updateBoard(received_moves)

                self.draw_board()
                self.draw_grid()
                self.selected_piece()

                # FIM DE JOGO
                if not self.check_available_moves():
                    text = self.font.render("Game Over Player", True, (255, 0, 0), self.BLACK, )
                    self.screen.blit(text, (self.BOARD_WIDTH // 8, (self.HEIGHT // 2) - 30))

                pygame.display.flip()

                self.clock.tick(self.FPS)

            pygame.quit()

    if __name__ == "__main__":
        game = Game_Client()
        game.run()


def start_server():
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

            scree = pygame.display.set_mode((400, 510))
            pygame.display.set_caption('RESTA UM - MENU')

            self.mytheme = pygame_menu.themes.Theme(background_color=(0, 0, 0, 0),
                                                    title_background_color=(14, 36, 23),
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
                scree.fill((14, 36, 23))
                self.menu.draw(scree)

                pygame.display.flip()
                clock.tick(30)

        def create_menu(self):
            self.menu = pygame_menu.Menu(f"SERVIDOR - {self.server_title_state}", 400, 510, theme=self.mytheme)

            self.menu.add.label(f'IP: {self.ip}', font_size=30, margin=(0, 0), font_color=self.font_color)
            self.menu.add.label(f'PORTA: {self.port}', font_size=30, margin=(0, 0), font_color=self.font_color)
            self.menu.add.button(self.server_state, self.on_off)
            self.menu.add.button('Voltar para Menu', main)
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
            Game_Server()

    if __name__ == "__main__":
        server = Game_Server()


def main():
    pygame.init()
    clock = pygame.time.Clock()

    surface = pygame.display.set_mode((350, 440))
    pygame.display.set_caption('RESTA UM - MENU')

    mytheme = pygame_menu.themes.Theme(background_color=(0, 0, 0, 0),  # transparent background
                                       title_background_color=(14, 36, 23),
                                       cursor_selection_color=(222, 252, 221),
                                       title_font_shadow=True,
                                       widget_padding=25,
                                       )

    menu = pygame_menu.Menu('Resta 1', 350, 440, theme=mytheme)

    menu.add.button('Cliente', login)
    menu.add.button('Servidor', start_server)
    menu.add.button('Sair', pygame_menu.events.EXIT)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        menu.update(events)
        surface.fill((14, 36, 23))
        menu.draw(surface)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
