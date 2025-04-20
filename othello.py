import pygame

# Pygameの初期化
pygame.init()

# ゲームウィンドウの設定
screen = pygame.display.set_mode((600, 600))  # 600x600ピクセルのウィンドウ
pygame.display.set_caption('Othello Game')  # ウィンドウのタイトル

# ゲーム盤の設定
board_color = (0, 128, 0)  # 緑色（オセロの盤の色）
line_color = (0, 0, 0)     # 黒色（線の色）
board_size = 8
cell_size = 75

# 盤面の初期設定（中央に黒と白のコマを配置）
board = [['' for _ in range(board_size)] for _ in range(board_size)]
board[3][3] = 'white'
board[3][4] = 'black'
board[4][3] = 'black'
board[4][4] = 'white'

# 現在のゲーム状態を保存
game_started = False  # ゲームが始まったかどうかのフラグ

# プレイヤーのムーブ完了時刻（AIの待機用）
last_human_move_time = None

# ゲーム盤の描画
def draw_board():
    # ゲーム盤の背景
    screen.fill(board_color)
    
    # グリッド線を描画
    for i in range(board_size + 1):
        pygame.draw.line(screen, line_color, (i * cell_size, 0), (i * cell_size, 600), 2)
        pygame.draw.line(screen, line_color, (0, i * cell_size), (600, i * cell_size), 2)
    
    # コマを描画（黒と白）
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] == 'black':
                pygame.draw.circle(screen, (0, 0, 0), (col * cell_size + cell_size // 2, row * cell_size + cell_size // 2), cell_size // 3)
            elif board[row][col] == 'white':
                pygame.draw.circle(screen, (255, 255, 255), (col * cell_size + cell_size // 2, row * cell_size + cell_size // 2), cell_size // 3)

    # ターン表示
    font = pygame.font.Font(None, 24)
    turn_text = f"Turn: {'Black (Computer)' if turn == 'black' else 'White (You)'}"
    text = font.render(turn_text, True, (255, 255, 255))
    screen.blit(text, (10, 10))

# ターン管理
turn = 'white'  # 白（人間）からスタート

# ひっくり返すべきコマを探すための関数
def flip_direction(row, col, d_row, d_col, player_color):
    flip_positions = []
    r, c = row + d_row, col + d_col
    
    # 最初に相手のコマがあるか確認
    if not (0 <= r < board_size and 0 <= c < board_size):
        return []
    
    opponent_color = 'white' if player_color == 'black' else 'black'
    if board[r][c] != opponent_color:
        return []
        
    flip_positions.append((r, c))
    r += d_row
    c += d_col
    
    while 0 <= r < board_size and 0 <= c < board_size:
        if board[r][c] == '':
            return []  # 空のマスがある場合、ひっくり返せない
        if board[r][c] == player_color:
            return flip_positions  # 自分のコマに到達したらひっくり返せる
        flip_positions.append((r, c))
        r += d_row
        c += d_col
    
    return []  # 盤の端に達した場合

# 有効な手かどうか確認する関数
def is_valid_move(row, col, player_color):
    if not (0 <= row < board_size and 0 <= col < board_size):
        return False
        
    if board[row][col] != '':  # 既にコマがある場合は無効
        return False
        
    # 8方向をチェック
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for d_row, d_col in directions:
        if flip_direction(row, col, d_row, d_col, player_color):
            return True
    
    return False

# コマをひっくり返す処理
def flip_captured(row, col, player_color):
    # 8方向をチェック
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    flipped = False
    
    for d_row, d_col in directions:
        flip_positions = flip_direction(row, col, d_row, d_col, player_color)
        for r, c in flip_positions:
            board[r][c] = player_color  # ひっくり返すコマを置く
            flipped = True
            
    return flipped

# マウスクリックでコマを置き、ひっくり返す
def handle_click():
    global turn, game_started, last_human_move_time
    x, y = pygame.mouse.get_pos()
    row = y // cell_size
    col = x // cell_size
    
    if 0 <= row < board_size and 0 <= col < board_size and is_valid_move(row, col, turn):
        game_started = True  # ゲームを開始
        board[row][col] = turn
        flip_captured(row, col, turn)
        turn = 'black'  # コンピュータのターンに切り替え
        last_human_move_time = pygame.time.get_ticks()  # 人間のムーブ後の時刻を記録
        
        # 次のプレイヤーが置ける場所がない場合はスキップ
        if not can_place_piece(turn):
            turn = 'white'  # 人間のターンに戻す

# 盤面が埋まったか確認
def is_board_full():
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] == '':
                return False
    return True

# プレイヤーがコマを置ける場所があるか確認
def can_place_piece(player_color):
    for row in range(board_size):
        for col in range(board_size):
            if is_valid_move(row, col, player_color):
                return True
    return False

# ゲーム終了判定
def check_game_over():
    if is_board_full() or not (can_place_piece('black') or can_place_piece('white')):
        return True
    return False

# ゲーム終了後に勝者を表示
def display_winner():
    black_count = sum(row.count('black') for row in board)
    white_count = sum(row.count('white') for row in board)
    
    if black_count > white_count:
        winner = "Black (Computer)"
    elif white_count > black_count:
        winner = "White (You)"
    else:
        winner = "No one (Draw)"
    
    result_text = f"Game Over! {winner} wins! {black_count}-{white_count}"
    
    font = pygame.font.Font(None, 36)
    text = font.render(result_text, True, (255, 255, 255))
    text_rect = text.get_rect(center=(300, 300))
    
    # 半透明の背景を描画
    s = pygame.Surface((600, 100))
    s.set_alpha(200)
    s.fill((0, 0, 0))
    screen.blit(s, (0, 250))
    
    screen.blit(text, text_rect)

# 評価関数（改良版）
def evaluate_board(board):
    # コーナーは価値が高い
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    # 辺も比較的価値が高い
    edges = [(0, i) for i in range(1, 7)] + [(7, i) for i in range(1, 7)] + \
            [(i, 0) for i in range(1, 7)] + [(i, 7) for i in range(1, 7)]
    
    black_count = sum(row.count('black') for row in board)
    white_count = sum(row.count('white') for row in board)
    
    # コーナーの評価
    corner_value = 10
    corner_score = 0
    for row, col in corners:
        if board[row][col] == 'black':
            corner_score += corner_value
        elif board[row][col] == 'white':
            corner_score -= corner_value
    
    # 辺の評価
    edge_value = 3
    edge_score = 0
    for row, col in edges:
        if board[row][col] == 'black':
            edge_score += edge_value
        elif board[row][col] == 'white':
            edge_score -= edge_value
    
    # 通常のコマの数の差
    piece_diff = black_count - white_count
    
    # ゲーム終盤では単純にコマの数が重要になる
    total_pieces = black_count + white_count
    if total_pieces > 50:  # ゲーム終盤
        weight_piece_diff = 3
    else:  # ゲーム序盤から中盤
        weight_piece_diff = 1
    
    return edge_score + corner_score + (piece_diff * weight_piece_diff)

# ボードをコピーする関数
def copy_board(board):
    return [row[:] for row in board]

# ミニマックスアルゴリズム（アルファ・ベータ枝刈りつき）
def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or check_game_over():
        return evaluate_board(board)
    
    if maximizing_player:  # 黒（AIプレイヤー）のターン
        max_eval = float('-inf')
        for row in range(board_size):
            for col in range(board_size):
                if is_valid_move(row, col, 'black'):
                    # ボードのコピーを作成
                    board_copy = copy_board(board)
                    
                    # 手を実行
                    board[row][col] = 'black'
                    flip_captured(row, col, 'black')
                    
                    # ミニマックスを再帰的に呼び出し
                    eval = minimax(board, depth - 1, alpha, beta, False)
                    
                    # ボードの状態を元に戻す
                    for r in range(board_size):
                        for c in range(board_size):
                            board[r][c] = board_copy[r][c]
                    
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:  # 白（人間プレイヤー）のターン
        min_eval = float('inf')
        for row in range(board_size):
            for col in range(board_size):
                if is_valid_move(row, col, 'white'):
                    # ボードのコピーを作成
                    board_copy = copy_board(board)
                    
                    # 手を実行
                    board[row][col] = 'white'
                    flip_captured(row, col, 'white')
                    
                    # ミニマックスを再帰的に呼び出し
                    eval = minimax(board, depth - 1, alpha, beta, True)
                    
                    # ボードの状態を元に戻す
                    for r in range(board_size):
                        for c in range(board_size):
                            board[r][c] = board_copy[r][c]
                    
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval

# 最適な手を選ぶ
def best_move():
    best_score = float('-inf')
    best_pos = None
    
    # ボードのバックアップを作成
    original_board = copy_board(board)
    
    for row in range(board_size):
        for col in range(board_size):
            if is_valid_move(row, col, 'black'):
                # 手を実行
                board[row][col] = 'black'
                flip_captured(row, col, 'black')
                
                # 評価（深さ2で探索）
                score = minimax(board, 2, float('-inf'), float('inf'), False)
                
                # ボードの状態を元に戻す
                for r in range(board_size):
                    for c in range(board_size):
                        board[r][c] = original_board[r][c]
                
                if score > best_score:
                    best_score = score
                    best_pos = (row, col)
    
    return best_pos

# コンピュータのターン処理
def computer_turn():
    global turn
    
    # 有効な手があるか確認
    if can_place_piece('black'):
        move = best_move()  # 最適な手を選ぶ
        if move:
            row, col = move
            board[row][col] = 'black'
            flip_captured(row, col, 'black')
    
    turn = 'white'  # ターンを切り替え
    
    # 次のプレイヤーが置ける場所がない場合はスキップ
    if not can_place_piece('white'):
        if can_place_piece('black'):  # 黒がまだ置ける場合
            turn = 'black'
        else:
            # どちらも置けない場合はゲーム終了
            return True
    
    return False

# メインループ内でクリックイベントを処理
running = True
game_over = False

# 初期描画
draw_board()
pygame.display.flip()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if turn == 'white':  # プレイヤーのターンのみ処理
                handle_click()  # クリックした位置にコマを置く
    
    # コンピュータのターンを実行（プレイヤーのムーブ後から5秒待機）
    if turn == 'black' and not game_over and game_started and last_human_move_time is not None:
        if pygame.time.get_ticks() - last_human_move_time >= 1000:
            game_over = computer_turn()
            last_human_move_time = None
    
    # ゲーム盤を描画
    draw_board()
    
    # ゲーム終了判定と表示
    if check_game_over():
        game_over = True
        display_winner()
    
    # ウィンドウの更新
    pygame.display.flip()

# ゲーム終了
pygame.quit()
