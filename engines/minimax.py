import chess

VALEURS_PIECES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Pions : On encourage l'avancee vers la 8eme rangee
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10,-20,-20, 10, 10,  5,
    5, -5,-10,  0,  0,-10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0,  0,  0,  0,  0,  0,  0,  0
]

# Cavaliers : On veut le centre, on evite les bords
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

# Fous : Mieux sur les grandes diagonales et au centre
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

# Tours : Mieux sur la 7eme rangee et au centre
ROOK_TABLE = [
    0,  0,  0,  5,  5,  0,  0,  0,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    5, 10, 10, 10, 10, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

# Reine : Similaire au fou et tour, mais moins punitif
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -10,  5,  5,  5,  5,  5,  0,-10,
    0,  0,  5,  5,  5,  5,  0, -5,
    -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

# Roi (Milieu de jeu) : On veut rester cache dans les coins (roque)
KING_TABLE = [
    20, 30, 10,  0,  0, 10, 30, 20,
    20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30
]

def evaluation_globale(board, prof):
    if board.is_checkmate():
        score_mat = 1000000 + prof #pour voir les mats en 1 avant les mats en 2
        return -score_mat if board.turn == chess.WHITE else score_mat
    
    if board.is_stalemate() or board.is_insufficient_material() or board.is_repetition(3):
        return 0

    score = 0
    for case, piece in board.piece_map().items():
        valeur_base = VALEURS_PIECES[piece.piece_type]

        table = None
        if piece.piece_type == chess.PAWN:
            table = PAWN_TABLE
        elif piece.piece_type == chess.KNIGHT:
            table = KNIGHT_TABLE
        elif piece.piece_type == chess.BISHOP:
            table = BISHOP_TABLE
        elif piece.piece_type == chess.ROOK:
            table = ROOK_TABLE
        elif piece.piece_type == chess.QUEEN:
            table = QUEEN_TABLE
        elif piece.piece_type == chess.KING:
            table = KING_TABLE

        bonus_positionnel = 0
        if table is not None:
            if piece.color == chess.WHITE:  #si c'est piece blanche, alors bon sens
                bonus_positionnel += table[case]
            else:   #si noir alors square_mirror (operations bits a bits O(1))
                bonus_positionnel += table[chess.square_mirror(case)]

        valeur_totale = valeur_base + bonus_positionnel

        if piece.color == chess.WHITE:  #si c'est une piece blanche +inf
            score += valeur_totale
        else:   #sinon c'est une piece noire -inf
            score -= valeur_totale

    #on evite les repetitions en mettant un malus
    if board.is_repetition(2):
        score += (-30 if board.turn == chess.WHITE else 30)

    return score

def coups_ordonnes(board):
    def score_coup(coup):
        score = 0
        if board.is_capture(coup):
            piece = board.piece_at(coup.to_square)
            if piece:
                score += VALEURS_PIECES.get(piece.piece_type, 0) + 10
        if coup.promotion:
            score += 800 #car pion = 100 et dame = 900
        if board.gives_check(coup):
            score += 50 #vaut un demi pion car gagne un temps sur l'echec
        return score
    return sorted(board.legal_moves, key=score_coup, reverse=True)    #tri les coups ordre decroissant

'''MiniMax et Maximin sans Elagage Alpha-Beta'''
def minmax(board, prof):
    """C'est le tour du MAXIMISANT (Les Blancs)"""
    global compteur_noeuds
    compteur_noeuds += 1
    if prof == 0 or board.is_game_over():
        return evaluation_globale(board, prof)
    
    max_eval = float("-inf")
    for coup in coups_ordonnes(board):  #on utilise la fonction qui trie les coups, pas tres utile sans alpha-beta
        board.push(coup)
        # Apres un coup des Blancs, c'est au tour du Minimisant
        eval = maxmin(board, prof - 1)
        board.pop()
        max_eval = max(max_eval, eval)
    return max_eval

def maxmin(board, prof):
    """C'est le tour du MINIMISANT (Les Noirs)"""
    global compteur_noeuds
    compteur_noeuds += 1
    if prof == 0 or board.is_game_over():
        return evaluation_globale(board, prof)
    
    min_eval = float("inf")
    for coup in coups_ordonnes(board):
        board.push(coup)
        # Apres un coup des Noirs, c'est au tour du Maximisant
        eval = minmax(board, prof - 1)
        board.pop()
        min_eval = min(min_eval, eval)
    return min_eval

def meilleur_coup(echiquier, prof, couleur):
    global compteur_noeuds
    compteur_noeuds = 0 #remise a zero a chaque coup du bot

    meilleur_coup = None

    if couleur == chess.WHITE:
        score_max = float("-inf")
        for coup in coups_ordonnes(echiquier):

            compteur_noeuds += 1 #le premier niveau compte comme un noeud

            echiquier.push(coup)
            val = maxmin(echiquier, prof -1)
            echiquier.pop()
            if val > score_max:
                score_max = val
                meilleur_coup = coup

    else:
        score_min = float("inf")
        for coup in echiquier.legal_moves:

            compteur_noeuds += 1

            echiquier.push(coup)
            val = minmax(echiquier, prof -1)
            echiquier.pop()
            if val < score_min:
                score_min = val
                meilleur_coup = coup
    return meilleur_coup, compteur_noeuds