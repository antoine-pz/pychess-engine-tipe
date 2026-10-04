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

# PST pour le milieu de jeu (Midgame)
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

# PST pour la finale (Endgame)
PAWN_TABLE_ENDGAME = [
    0,  0,  0,  0,  0,  0,  0,  0,
    10, 10, 10, 10, 10, 10, 10, 10,
    20, 20, 20, 20, 20, 20, 20, 20,
    40, 40, 40, 40, 40, 40, 40, 40,
    80, 80, 80, 80, 80, 80, 80, 80,
    150, 150, 150, 150, 150, 150, 150, 150,
    300, 300, 300, 300, 300, 300, 300, 300,
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

# AMELIORATION : Le Roi doit être encourage a se centraliser en finale
KING_TABLE_ENDGAME = [
    -50,-30,-30,-30,-30,-30,-30,-50,
    -30,-10,  0,  0,  0,  0,-10,-30,
    -30,  0, 20, 30, 30, 20,  0,-30,
    -30,  0, 30, 40, 40, 30,  0,-30,
    -30,  0, 30, 40, 40, 30,  0,-30,
    -30,  0, 20, 30, 30, 20,  0,-30,
    -30,-10,  0,  0,  0,  0,-10,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

table_transposition = {}
compteur_noeuds = 0

def evaluation_globale(board):
    if board.is_checkmate():
        score_mat = 1000000  
        return -score_mat if board.turn == chess.WHITE else score_mat
    
    if board.is_stalemate() or board.is_insufficient_material() or board.is_repetition(3):
        return 0

    score_mg = 0    #score milieu_de_jeu
    score_eg = 0    #score endgame

    for case, piece in board.piece_map().items():
        valeur_base = VALEURS_PIECES[piece.piece_type]

        table_mg = None
        table_eg = None

        if piece.piece_type == chess.PAWN:
            table_mg = PAWN_TABLE
            table_eg = PAWN_TABLE_ENDGAME
        elif piece.piece_type == chess.KNIGHT:
            table_mg = KNIGHT_TABLE
            table_eg = KNIGHT_TABLE
        elif piece.piece_type == chess.BISHOP:
            table_mg = BISHOP_TABLE
            table_eg = BISHOP_TABLE
        elif piece.piece_type == chess.ROOK:
            table_mg = ROOK_TABLE
            table_eg = ROOK_TABLE
        elif piece.piece_type == chess.QUEEN:
            table_mg = QUEEN_TABLE
            table_eg = QUEEN_TABLE
        elif piece.piece_type == chess.KING:
            table_mg = KING_TABLE
            table_eg = KING_TABLE_ENDGAME

        bonus_mg = 0
        bonus_eg = 0

        if piece.color == chess.WHITE:  #si Blancs
            if table_mg is not None: bonus_mg = table_mg[case]
            if table_eg is not None: bonus_eg = table_eg[case]
            score_mg += (valeur_base + bonus_mg)
            score_eg += (valeur_base + bonus_eg)
        else:                           #si Noirs
            if table_mg is not None: bonus_mg = table_mg[chess.square_mirror(case)]
            if table_eg is not None: bonus_eg = table_eg[chess.square_mirror(case)]
            score_mg -= (valeur_base + bonus_mg)
            score_eg -= (valeur_base + bonus_eg)

    if board.is_repetition(2):
        penalite = (-30 if board.turn == chess.WHITE else 30)
        score_mg += penalite
        score_eg += penalite

    # Mop-up / poussee du roi adverse
    score_eg = evaluation_finale(board, score_eg)

    # --- CORRECTION WIKI CHESS : CALCUL DE LA PHASE ---
    phase = 0
    # on calcule le materiel lourd restant pour savoir a quel stade de la partie on est
    # cavalier/fou = 1 point de phase
    phase += (len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK))) * 1
    phase += (len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK))) * 1
    # tour = 2 points de phase
    phase += (len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK))) * 2
    # dame = 4 points de phase
    phase += (len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))) * 4

    # 24 est le max theorique
    if phase > 24:
        phase = 24

    # Interpolation lineaire dynamique entre le score de milieu de jeu et de finale
    # si phase = 24 (debut), score_eg est annule (multiplie par 0)
    # si phase = 0 (finale pure), score_mg est annule
    # entre les deux, on fait une moyenne ponderee pour avoir une transition fluide
    score_total = int(((score_mg * phase) + (score_eg * (24 - phase))) / 24)

    return score_total

def evaluation_finale(board, score_materiel):
    score = score_materiel

    # on determine quel camp a l'avantage materiel
    if score_materiel > 0: 
        roi_gagnant = board.king(chess.WHITE)
        roi_perdant = board.king(chess.BLACK)
    else: 
        roi_gagnant = board.king(chess.BLACK)
        roi_perdant = board.king(chess.WHITE)

    file_p, rank_p = chess.square_file(roi_perdant), chess.square_rank(roi_perdant)

    # forcer le roi perdant vers les bords pour le mater
    dist_centre_f = max(3 - file_p, file_p - 4)
    dist_centre_r = max(3 - rank_p, rank_p - 4)
    score += (dist_centre_f + dist_centre_r) * 10

    dist_entre_rois = abs(chess.square_file(roi_gagnant) - file_p) + abs(chess.square_rank(roi_gagnant) - rank_p)
    score += (14 - dist_entre_rois) * 5

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
            
        nb_pieces_lourdes = (
            len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK)) +
            len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
        )
        est_quasi_finale = nb_pieces_lourdes <= 2

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
        if board.gives_check(coup) and not est_quasi_finale:
            score += 50 
        return score 
    return sorted(board.legal_moves, key=score_coup, reverse=True)

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

    cle_zobrist = chess.polyglot.zobrist_hash(echiquier)
    coup_hash = None
    if cle_zobrist in table_transposition:
        coup_hash = table_transposition[cle_zobrist].get('meilleur_coup')

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