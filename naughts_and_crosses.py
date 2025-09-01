# naughts_and_crosses.py

import random
import os

# ---------- UI / I/O ----------

def input_location(board, player_symbol, N):
    while True:
        loc = input(f"Where do you want to place your {player_symbol} (1-{N**2}): ")   
        if not loc.isdigit() or not 1 <= int(loc) <= N**2:
            print(f"Invalid input. Enter a number between 1 and {N**2}.")
            continue
        loc = int(loc) - 1
        if board[loc] != "$":
            print("That spot is already filled.")
            continue
        return loc

def print_board(board, N, highlight=None, last_move=None):
    symbols = {0: "O", 1: "X", "$": " "}
    for i in range(N):
        print("|".join(f"\033[92m{symbols[board[i*N+j]]}\033[0m" if highlight and i*N+j in highlight else f"\033[91m{symbols[board[i*N+j]]}\033[0m" if last_move is not None and i*N+j == last_move else symbols[board[i*N+j]] for j in range(N)))

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

# ---------- Bitwise Helpers ----------
        
def generate_winning_masks(N):
    masks = []

    # rows
    for i in range(N):
        mask = 0
        for j in range(N):
            mask |= 1 << (i*N + j)
        masks.append(mask)

    # columns
    for j in range(N):
        mask = 0
        for i in range(N):
            mask |= 1 << (i*N + j)
        masks.append(mask)

    # diagonal \
    mask = 0
    for i in range(N):
        mask |= 1 << (i*N + i)
    masks.append(mask)

    # diagonal /
    mask = 0
    for i in range(N):
        mask |= 1 << (i*N + (N-1-i))
    masks.append(mask)

    return masks

def check_winner(player_bitboard, winning_masks):
    return any(player_bitboard & mask == mask for mask in winning_masks)

def legal_moves(board):
    return [i for i, v in enumerate(board) if v == "$"]

winning_cells = lambda board, pb, masks: next(([i for i in range(len(board)) if (m >> i) & 1] for m in masks if pb & m == m), [])

# ---------- Heuristic Evaluation (for N >= 4) ----------

def line_potential_score(bit_me, bit_opp, winning_masks):
    my_score = 0
    opp_score = 0
    for m in winning_masks:
        opp_in_line = (bit_opp & m) != 0
        me_in_line = (bit_me & m) != 0
        if not opp_in_line:
            my_score += 2 if me_in_line else 1
        if not me_in_line:
            opp_score += 2 if opp_in_line else 1
    return my_score - opp_score

# ---------- Minimax (for N = 3) ----------

def minimax(bit_me, bit_opp, free_spots, winning_masks, maximising, memo):
    key = (bit_me, bit_opp, tuple(free_spots), maximising)
    if key in memo:
        return memo[key]
    
    if check_winner(bit_me, winning_masks):
        return 1, None
    if check_winner(bit_opp, winning_masks):
        return -1, None
    if not free_spots:
        return 0, None
    
    best_move = None
    if maximising:
        best_val = -2
        for mv in free_spots:
            new_me = bit_me | (1 << mv)
            remaining = [x for x in free_spots if x != mv]
            val, _ = minimax(bit_opp, new_me, remaining, winning_masks, False, memo)
            val = -val
            if val > best_val:
                best_val, best_move = val, mv
                if best_val == 1:
                    break
    else:
        best_val = -2
        for mv in free_spots:
            new_me = bit_me | (1 << mv)
            remaining = [x for x in free_spots if x != mv]
            val, _ = minimax(bit_opp, new_me, remaining, winning_masks, True, memo)
            val = -val
            if val > best_val:
                best_val, best_move = val, mv
                if best_val == 1:
                    break
    
    memo[key] = (best_val, best_move)
    return memo[key]

# ---------- CPU Policies ----------

def cpu_move_easy(board):
    return random.choice(legal_moves(board))

def cpu_move_hard(board, N, cpu_id, player_bitboards, winning_masks):
    bits_me = player_bitboards[cpu_id]
    bits_opp = player_bitboards[1 - cpu_id]
    moves = legal_moves(board)

    for mv in moves:
        if check_winner(bits_me | (1 << mv), winning_masks):
            return mv
        
    for mv in moves:
        if check_winner(bits_opp | (1 << mv), winning_masks):
            return mv
        
    if N == 3:
        memo = {}
        val, best = minimax(bits_me, bits_opp, moves, winning_masks, True, memo)
        if best is not None:
            return best
    
    center = (N * N) // 2 if N % 2 == 1 else None
    if center is not None and board[center] == "$":
        return center
    
    corners = [0, N - 1, N * (N - 1), N * N - 1]
    random.shuffle(corners)
    for c in corners:
        if 0 <= c < N * N and board[c] == "$":
            return c
        
    best_mv = None
    best_sc = -10**9
    random.shuffle(moves)
    for mv in moves:
        new_me = bits_me | (1 << mv)
        sc = line_potential_score(new_me, bits_opp, winning_masks)
        if sc > best_sc:
            best_sc, best_mv = sc, mv
    return best_mv if best_mv is not None else random.choice(moves)

# ---------- Main ----------

def main():
    N = int(next(n for n in iter(lambda: input("Enter board size N (e.g., 3 for 3x3): ").strip(), None) if n.isdigit() and int(n) > 0))
    vs_cpu = next(m for m in iter(lambda: input("Play vs CPU? (y/n): ").strip().lower(), None) if m in ("y","n")) == "y"

    human_is = 0
    if vs_cpu:
        human_is = 0 if next(s for s in iter(lambda: input("Do you want to be O or X? (O goes first) [O/X]: ").strip().lower(), None) if s in ("o","x")) == "o" else 1
        cpu_difficulty = next(d for d in iter(lambda: input("CPU difficulty [easy/hard] (default hard): ").strip().lower() or "hard", None) if d in ("easy","hard"))

    board = ["$"] * (N ** 2)
    player = 0
    symbols = {0: "O", 1: "X"}
    player_bitboards = [0, 0]
    winning_masks = generate_winning_masks(N)

    last_move = None
    while True:
        clear_console()
        highlight = winning_cells(board, player_bitboards[player], winning_masks)
        print_board(board, N, highlight if highlight else None, last_move=last_move)

        if vs_cpu and player != human_is:
            if cpu_difficulty == "easy":
                mv = cpu_move_easy(board)
            else:
                mv = cpu_move_hard(board, N, player, player_bitboards, winning_masks)
            print(f"CPU ({symbols[player]}) plays: {mv + 1}")
        else:
            mv = input_location(board, symbols[player], N)
        
        board[mv] = player
        player_bitboards[player] |= 1 << mv
        last_move = mv
        
        if check_winner(player_bitboards[player], winning_masks):
            clear_console()
            highlight = winning_cells(board, player_bitboards[player], winning_masks)
            print_board(board, N, highlight if highlight else None)
            if not vs_cpu or player == human_is:
                print(f"Congratulations, Player {player + 1} ({symbols[player]}), you won!")
            else:
                print(f"Unlucky, CPU ({symbols[player]}) won.")
            break
        
        if "$" not in board:
            clear_console()
            print_board(board, N)
            print("It's a draw!")
            break
        
        player = 1 - player

if __name__ == "__main__":
    main()
