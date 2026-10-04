import chess

VALEURS_PIECES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# indice 0 pour la case a1 donc pour les Blancs
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

def evaluation_globale(board, profondeur_restante):
    if board.is_checkmate():
        score_mat = 1000000 + profondeur_restante   #plus le prof_rest est grande plus le mat est proche
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

def captures_ordonnees(board):
    def score_capture(coup):
        piece_victime = board.piece_at(coup.to_square)
        piece_attaquant = board.piece_at(coup.from_square)
        if piece_victime:
            return (VALEURS_PIECES.get(piece_victime.piece_type, 0) * 10) - VALEURS_PIECES.get(piece_attaquant.piece_type, 0)
        return 10  # Cas de la prise en passant (Pion vs Pion)
        
    return sorted(board.generate_legal_captures(), key=score_capture, reverse=True)

'''QUIESCENCE SEARCH'''
def quiescence(echiquier, alpha, beta, maximisant):
    global compteur_noeuds
    compteur_noeuds += 1

    score_actuel = evaluation_globale(echiquier, 0)

    if maximisant:  #ici on modifie alpha
        if score_actuel >= beta:
            return beta
        if score_actuel > alpha:
            alpha = score_actuel

        # On ne regarde QUE les coups qui sont des captures
        for coup in captures_ordonnees(echiquier):
                echiquier.push(coup)
                score = quiescence(echiquier, alpha, beta, False)
                echiquier.pop()
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha
    
    else: #ici on modifie beta
        if score_actuel <= alpha:
            return alpha
        if score_actuel < beta:
            beta = score_actuel
        
        for coup in captures_ordonnees(echiquier):
                echiquier.push(coup)
                score = quiescence(echiquier, alpha, beta, True)
                echiquier.pop()
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score
        return beta

def coups_ordonnes(board):
    def score_coup(coup):
        score = 0
        if board.is_capture(coup):
            piece_victime = board.piece_at(coup.to_square)
            piece_attaquant = board.piece_at(coup.from_square)
            if piece_victime:
                score += (VALEURS_PIECES.get(piece_victime.piece_type, 0) * 10) - VALEURS_PIECES.get(piece_attaquant.piece_type, 0)
            else:
                score += 10  # Prise en passant
        if coup.promotion:    
            score += 800 
        if board.gives_check(coup):
            score += 50 
        return score 
        
    return sorted(board.legal_moves, key=score_coup, reverse=True)

'''Elagage Alpha-Beta'''
def elagage_alpha_beta(echiquier, profondeur, alpha, beta, maximisant):
    global compteur_noeuds
    compteur_noeuds += 1

    if echiquier.is_game_over():
        return evaluation_globale(echiquier, profondeur)
    
    # appel a la fonction de quiescence search
    if profondeur == 0:
        return quiescence(echiquier, alpha, beta, maximisant)
    
    if maximisant:
        max_eval = float('-inf')
        for coup in coups_ordonnes(echiquier):  #on regarde dans la liste des coups
            echiquier.push(coup)
            eval = elagage_alpha_beta(echiquier, profondeur - 1, alpha, beta, False)   #maximisant=False veut dire qu'on minimise
            echiquier.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:   #decoupage alpha
                break
        return max_eval
    
    else:
        min_eval = float('inf')
        for coup in coups_ordonnes(echiquier):
            echiquier.push(coup)
            eval = elagage_alpha_beta(echiquier, profondeur - 1, alpha, beta, True)
            echiquier.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:   #decoupage beta
                break
        return min_eval
    
def meilleur_coup(echiquier, prof, couleur):
    global compteur_noeuds
    compteur_noeuds = 0 #remise a zero a chaque coup du bot

    meilleur_coup = None

    bot_est_blanc = (couleur == chess.WHITE)

    alpha = float("-inf")
    beta = float("inf")
    meilleur_score = float("-inf") if bot_est_blanc else float("inf")

    for coup in coups_ordonnes(echiquier):  #on a trie les coups que l'on va considerer donc l'elagage est bien plus efficace

        compteur_noeuds += 1 #le premier niveau compte comme un noeud

        echiquier.push(coup)
        score = elagage_alpha_beta(echiquier, prof-1, alpha=alpha, beta=beta, maximisant=not bot_est_blanc) #True si bot est NOIR False si bot est BLANC
        echiquier.pop()

        if bot_est_blanc:
            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
            alpha = max(alpha, meilleur_score)  #mise a jour de alpha
        else:
            if score < meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
            beta = min(beta, meilleur_score)    #mise a jour de beta

    return meilleur_coup, compteur_noeuds