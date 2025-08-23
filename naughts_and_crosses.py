# naughts_and_crosses.py

import random

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

def print_board(board, N):
    symbols = {0: "O", 1: "X", "$": " "}
    for i in range(N):
        row = "|".join(symbols[board[i*N + j]] for j in range(N))
        print(row)

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

# ---------- Main ----------

def main():
    N = int(next(n for n in iter(lambda: input("Enter board size N (e.g., 3 for 3x3): ") or print("Invalid input. Please enter a positive integer.") or None, None) if n and n.isdigit() and int(n) > 0))
    board = ["$"] * (N ** 2)
    player = 0 # 0 = O, 1 = X
    symbols = {0: "O", 1: "X"}
    player_bitboards = [0, 0]
    winning_masks = generate_winning_masks(N)

    while True:
        print_board(board, N)
        loc = input_location(board, symbols[player], N)
        board[loc] = player
        player_bitboards[player] |= 1 << loc
        
        if check_winner(player_bitboards[player], winning_masks):
            print_board(board, N)
            print(f"Congratulations, Player {player + 1} ({symbols[player]}), you won!")
            break
        
        if "$" not in board:
            print_board(board, N)
            print("It's a draw!")
            break
        
        player = 1 - player

if __name__ == "__main__":
    main()
