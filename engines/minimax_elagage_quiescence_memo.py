import chess
import chess.polyglot

VALEURS_PIECES = {
    chess.PAWN: 100,    
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

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

EXACT = 0   
LOWERBOUND = 1  
UPPERBOUND = 2 

table_transposition = {}

def evaluation_globale(board):
    if board.is_checkmate():
        score_mat = 1000000 
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
            if piece.color == chess.WHITE:  
                bonus_positionnel += table[case]
            else:   
                bonus_positionnel += table[chess.square_mirror(case)]

        valeur_totale = valeur_base + bonus_positionnel

        if piece.color == chess.WHITE:  
            score += valeur_totale
        else:   
            score -= valeur_totale

    if board.is_repetition(2):
        score += (-30 if board.turn == chess.WHITE else 30)

    return score

def captures_ordonnees(board):
    def score_capture(coup):
        piece_victime = board.piece_at(coup.to_square)
        piece_attaquant = board.piece_at(coup.from_square)
        if piece_victime:
            return (VALEURS_PIECES.get(piece_victime.piece_type, 0) * 10) - VALEURS_PIECES.get(piece_attaquant.piece_type, 0)
        return 10  
        
    return sorted(board.generate_legal_captures(), key=score_capture, reverse=True)

def quiescence(echiquier, alpha, beta, maximisant):
    global compteur_noeuds
    compteur_noeuds += 1

    score_actuel = evaluation_globale(echiquier)

    if maximisant:  
        if score_actuel >= beta:
            return beta
        if score_actuel > alpha:
            alpha = score_actuel

        for coup in captures_ordonnees(echiquier):
            echiquier.push(coup)
            score = quiescence(echiquier, alpha, beta, False)
            echiquier.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    
    else: 
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

def coups_ordonnes(board, coup_hash=None):
    def score_coup(coup):
        if coup_hash and coup == coup_hash:
            return 100000
        score = 0
        if board.is_capture(coup):
            piece_victime = board.piece_at(coup.to_square)
            piece_attaquant = board.piece_at(coup.from_square)
            if piece_victime:
                score += (VALEURS_PIECES.get(piece_victime.piece_type, 0) * 10) - VALEURS_PIECES.get(piece_attaquant.piece_type, 0)
            else:
                score += 10  
        if coup.promotion:    
            score += 800
        if board.gives_check(coup):
            score += 50
        return score
        
    return sorted(board.legal_moves, key=score_coup, reverse=True)

'''MEMOISATION (avec des cles de Zobrist)'''
def elagage_alpha_beta(echiquier, profondeur, alpha, beta, maximisant):
    global compteur_noeuds
    
    cle_zobrist = chess.polyglot.zobrist_hash(echiquier)
    coup_hash = None

    if cle_zobrist in table_transposition:
        entree = table_transposition[cle_zobrist]
        coup_hash = entree.get('meilleur_coup') 

        if entree['profondeur'] >= profondeur:
            if entree['flag'] == EXACT:
                return entree['valeur']
            elif entree['flag'] == LOWERBOUND:
                alpha = max(alpha, entree['valeur'])
            elif entree['flag'] == UPPERBOUND:
                beta = min(beta, entree['valeur'])
            
            if alpha >= beta:
                return entree['valeur']

    compteur_noeuds += 1

    if echiquier.is_game_over():
        return evaluation_globale(echiquier)
    
    if profondeur == 0:
        return quiescence(echiquier, alpha, beta, maximisant)
    
    alpha_original = alpha
    beta_original = beta
    coup_local = None   
    
    if maximisant:
        max_eval = float('-inf')
        for coup in coups_ordonnes(echiquier, coup_hash=coup_hash):
            echiquier.push(coup)
            eval = elagage_alpha_beta(echiquier, profondeur - 1, alpha, beta, False)
            echiquier.pop()
            
            if eval > max_eval:
                max_eval = eval
                coup_local = coup   
            alpha = max(alpha, eval)

            if beta <= alpha:  
                break
                
        flag = EXACT
        if max_eval <= alpha_original:
            flag = UPPERBOUND  
        elif max_eval >= beta_original:
            flag = LOWERBOUND  
            
        table_transposition[cle_zobrist] = {
            'valeur': max_eval,
            'profondeur': profondeur,
            'flag': flag,
            'meilleur_coup': coup_local 
        }
        
        return max_eval
    
    else:
        min_eval = float('inf')
        for coup in coups_ordonnes(echiquier, coup_hash=coup_hash):
            echiquier.push(coup)
            eval = elagage_alpha_beta(echiquier, profondeur - 1, alpha, beta, True)
            echiquier.pop()

            if eval < min_eval:
                min_eval = eval
                coup_local = coup
            beta = min(beta, eval)

            if beta <= alpha:  
                break
                
        flag = EXACT
        if min_eval >= beta_original:
            flag = LOWERBOUND  
        elif min_eval <= alpha_original:
            flag = UPPERBOUND  
            
        table_transposition[cle_zobrist] = {
            'valeur': min_eval,
            'profondeur': profondeur,
            'flag': flag,
            'meilleur_coup': coup_local
        }
        
        return min_eval
    
def meilleur_coup(echiquier, prof, couleur):
    global compteur_noeuds
    compteur_noeuds = 0 
    
    meilleur_coup = None
    bot_est_blanc = (couleur == chess.WHITE)

    alpha = float("-inf")
    beta = float("inf")
    meilleur_score = float("-inf") if bot_est_blanc else float("inf")

    # CORRECTION : Ajout de la recherche du coup_hash a la racine pour transpo
    cle_zobrist = chess.polyglot.zobrist_hash(echiquier)
    coup_hash = None
    if cle_zobrist in table_transposition:
        coup_hash = table_transposition[cle_zobrist].get('meilleur_coup') #on recupere le meilleur coup present dans la table

    for coup in coups_ordonnes(echiquier, coup_hash=coup_hash):  

        compteur_noeuds += 1 

        echiquier.push(coup)
        score = elagage_alpha_beta(echiquier, prof-1, alpha=alpha, beta=beta, maximisant=not bot_est_blanc) 
        echiquier.pop()

        if bot_est_blanc:
            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
            alpha = max(alpha, meilleur_score)  
        else:
            if score < meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
            beta = min(beta, meilleur_score)    

    return meilleur_coup, compteur_noeuds