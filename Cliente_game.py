import pygame
import sys
import threading
import socket
import pickle

class RestaUm:
    def __init__(self):
        pygame.init()

        # Constantes
        self.WIDTH, self.HEIGHT = 1000, 600
        self.BOARD_WIDTH = 605  # Largura do tabuleiro
        self.ROW_COUNT, self.COL_COUNT = 7, 7
        self.CELL_SIZE = self.BOARD_WIDTH // self.COL_COUNT
        self.FPS = 60

        # Variáveis
        self.selected_ball = None
        self.is_local_turn = False
        self.send_movement = None

        # Cores e imagens
        self.BLACK = (0, 0, 0)
        self.LIGHT_GREEN = (222, 252, 221)
        self.DARK_GREEN = (14, 36, 23)
        self.font = pygame.font.Font(None, 36)

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

        self.ip = "192.168.15.100"
        self.port = 55555
        self.nickname = "Andre"
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
                                 and self.board[self.selected_ball[0] - (self.selected_ball[0] - row) // 2][col] == 1)
                                or
                                (abs(self.selected_ball[1] - col) == 2 and self.selected_ball[0] == row
                                 and self.board[row][self.selected_ball[1] - (self.selected_ball[1] - col) // 2] == 1)
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
                (self.selected_ball[1] * self.CELL_SIZE + self.CELL_SIZE // 2, self.selected_ball[0] * self.CELL_SIZE + self.CELL_SIZE // 2),
                self.CELL_SIZE // 3,
                50,
            )

    def valid_move(self, src_row, src_col, row, col):
        # Realiza a movimentação
        if (
                abs(src_row - row) == 2
                and src_col == col
                and self.board[src_row - (src_row - row) // 2][col] == 1
        ) or (
                abs(src_col - col) == 2
                and src_row == row
                and self.board[row][src_col - (src_col - col) // 2] == 1
        ):
            # Move a peça
            self.board[row][col] = 1
            self.board[src_row][src_col] = 0

            # Remove a peça pulada
            jumped_row, jumped_col = ((src_row + row) // 2, (src_col + col) // 2,)
            self.board[jumped_row][jumped_col] = 0

            self.selected_ball = None


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
            pygame.draw.line(self.screen, self.DARK_GREEN, (0, i * self.CELL_SIZE), (self.BOARD_WIDTH - 10, i * self.CELL_SIZE))
        for j in range(self.COL_COUNT):
            pygame.draw.line(self.screen, self.DARK_GREEN, (j * self.CELL_SIZE - 1, 0), (j * self.CELL_SIZE, self.BOARD_WIDTH))

    def start_client(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.ip, self.port))
        except Exception as e:
            print(f'Erro ao conectar ao servidor: {e}')
            sys.exit()

        def receive():
            while True:
                try:
                    move = self.client.recv(4096)
                    match move:
                        case b'FIRST_CLIENTMOVE':
                            print("Você é o primeiro cliente. Aguarde a jogada do outro jogador.")
                            self.is_local_turn = True
                            self.turn_event.set()
                            self.client.send(self.nickname.encode('utf-8'))
                        case b'MOVE':
                            self.client.send(self.nickname.encode('utf-8'))
                            print(f"{self.nickname}, é a sua vez de jogar.")
                            self.is_local_turn = True
                            self.turn_event.set()
                        case default:
                            move_data = pickle.loads(move)
                            print(f"MOVE DATA{move_data}")
                            src_row = move_data['src_row']
                            src_col = move_data['src_col']
                            row = move_data['row']
                            col = move_data['col']

                            received_moves = [(src_row, src_col, row, col)]
                            self.updateBoard(received_moves)

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
                        print(f"\nMOVE DENTRO DO WRITE: {move}")
                        self.client.send(move)
                        self.send_movement = None
                    else:
                        print(f"ELSE: {self.send_movement}")
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
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    col = event.pos[0] // self.CELL_SIZE
                    row = event.pos[1] // self.CELL_SIZE

                    if self.is_local_turn == True: #Se for a vez do cliente
                        print("Sua vez")
                        # Movimentos
                        if 0 <= row < self.ROW_COUNT and 0 <= col < self.COL_COUNT:
                            if self.selected_ball is None and self.board[row][col] == 1:
                                self.selected_ball = (row, col)
                            elif self.selected_ball is not None and self.board[row][col] == 1:
                                self.selected_ball = (row, col)
                            elif self.selected_ball is not None and self.board[row][col] == 0:
                                src_row, src_col = self.selected_ball
                                self.valid_move(src_row, src_col, row, col)
                                self.send_movement = src_row, src_col, row, col
                                print(self.send_movement)
                                self.is_local_turn = False

                    else:
                        self.turn_event.wait()
                        self.turn_event.clear()

                        text = self.font.render(f"Sua vez, {self.nickname}", True, self.BLACK)
                        self.screen.blit(text, (self.BOARD_WIDTH + 10, self.HEIGHT // 2 - text.get_height() // 2))
                        pygame.display.flip()
                        received_moves = []
                        self.updateBoard(received_moves)

            self.draw_board()
            self.draw_grid()
            self.selected_piece()

            # FIM DE JOGO
            if not self.check_available_moves():
                text = self.font.render(f"Game Over Player {self.nickname}", True, self.BLACK)
                self.screen.blit(text, (self.BOARD_WIDTH + 10, self.HEIGHT // 2 - text.get_height() // 2))

            pygame.display.flip()

            self.clock.tick(self.FPS)

        pygame.quit()


if __name__ == "__main__":
    game = RestaUm()
    game.run()

