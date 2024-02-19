import pygame

# Constantes
WIDTH, HEIGHT = 1000, 600
BOARD_WIDTH = 605  # Largura do tabuleiro
ROW_COUNT, COL_COUNT = 7, 7
CELL_SIZE = BOARD_WIDTH // COL_COUNT

FPS = 60

# Variáveis
selected_ball = None
PLAYER_1 = 1
PLAYER_2 = 2
current_player = PLAYER_1  # Começa com o Jogador 1

# Cores e imagens
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
DARK_GREEN = (14, 36, 23)
LIGHT_GREEN = (222, 252, 221)

# Inicializa a tela
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RESTA UM")
clock = pygame.time.Clock()

# Cria o tabuleiro
board = [
    [-1, -1, 1, 1, 1, -1, -1],
    [-1, -1, 1, 1, 1, -1, -1],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [-1, -1, 1, 1, 1, -1, -1],
    [-1, -1, 1, 1, 1, -1, -1],
]

font = pygame.font.Font(None, 36)

def draw_board():
    # Desenha o tabuleiro
    screen.fill(LIGHT_GREEN)
    for row in range(ROW_COUNT):
        for col in range(COL_COUNT):
            if board[row][col] == 1:
                pygame.draw.circle(
                    screen,
                    DARK_GREEN,
                    (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2),
                    CELL_SIZE // 3,
                )
            elif selected_ball is not None and (
                    board[row][col] == 0
                    and (
                            (abs(selected_ball[0] - row) == 2 and selected_ball[1] == col
                             and board[selected_ball[0] - (selected_ball[0] - row) // 2][col] == 1)
                            or
                            (abs(selected_ball[1] - col) == 2 and selected_ball[0] == row
                             and board[row][selected_ball[1] - (selected_ball[1] - col) // 2] == 1)
                    )
            ):
                pygame.draw.circle(
                    screen,
                    LIGHT_GRAY,
                    (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2),
                    CELL_SIZE // 3,
                )
            elif board[row][col] == -1:
                pygame.draw.rect(
                    screen,
                    DARK_GREEN,
                    (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )

def selected_piece():
    # Destaca a peça selecionada
    if selected_ball is not None:
        pygame.draw.circle(
            screen,
            (74, 96, 83),
            (selected_ball[1] * CELL_SIZE + CELL_SIZE // 2, selected_ball[0] * CELL_SIZE + CELL_SIZE // 2),
            CELL_SIZE // 3,
            50,
        )

def valid_move(src_row, src_col, row, col):
    # Realiza a movimentação
    global selected_ball
    global current_player

    if (
            abs(src_row - row) == 2
            and src_col == col
            and board[src_row - (src_row - row) // 2][col] == 1
    ) or (
            abs(src_col - col) == 2
            and src_row == row
            and board[row][src_col - (src_col - col) // 2] == 1
    ):
        # Move a peça
        board[row][col] = 1
        board[src_row][src_col] = 0

        # Remove a peça pulada
        jumped_row, jumped_col = ((src_row + row) // 2, (src_col + col) // 2,)
        board[jumped_row][jumped_col] = 0

        selected_ball = None

        # Troca para o turno do outro jogador
        current_player = PLAYER_2 if current_player == PLAYER_1 else PLAYER_1
        print(src_row, src_col, row, col)
def check_available_moves():
    # Verifica movimentos disponíveis
    for row in range(ROW_COUNT):
        for col in range(COL_COUNT):
            if board[row][col] == 1:
                # Verifica possíveis movimentos para cada peça
                for delta_row, delta_col in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    new_row, new_col = row + delta_row, col + delta_col
                    jump_row, jump_col = row + delta_row // 2, col + delta_col // 2

                    # Verifica se o movimento é válido
                    if (
                            0 <= new_row < ROW_COUNT
                            and 0 <= new_col < COL_COUNT
                            and board[new_row][new_col] == 0
                            and board[jump_row][jump_col] == 1
                    ):
                        return True  # Pelo menos um movimento disponível

    return False  # Nenhum movimento disponível

def draw_grid():
    # Desenha as linhas do grid
    for i in range(ROW_COUNT):
        pygame.draw.line(screen, DARK_GREEN, (0, i * CELL_SIZE), (BOARD_WIDTH-10, i * CELL_SIZE))
    for j in range(COL_COUNT):
        pygame.draw.line(screen, DARK_GREEN, (j * CELL_SIZE-1, 0), (j * CELL_SIZE, BOARD_WIDTH))


def main():
    global selected_ball
    global current_player

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                col = event.pos[0] // CELL_SIZE
                row = event.pos[1] // CELL_SIZE

                # Movimentos
                if 0 <= row < ROW_COUNT and 0 <= col < COL_COUNT:  # A peça está dentro dos limites do tabuleiro
                    if selected_ball is None and board[row][col] == 1:  # A peça selecionada é válida
                        selected_ball = (row, col)
                    elif selected_ball is not None and board[row][col] == 1:  # Uma peça já está selecionada
                        selected_ball = (row, col)
                    elif selected_ball is not None and board[row][col] == 0:  # Faz o movimento, verifica se uma peça está selecionada e se o espaço está vazio
                        src_row, src_col = selected_ball

                        valid_move(src_row, src_col, row, col)

        draw_board()
        draw_grid()
        selected_piece()

        # FIM DE JOGO
        if not check_available_moves():
            # Adiciona bloco de texto à direita
            text = font.render(f"Game Over Player{current_player}", True, BLACK)
            screen.blit(text, (BOARD_WIDTH + 10, HEIGHT // 2 - text.get_height() // 2))

        # Atualiza a tela
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
