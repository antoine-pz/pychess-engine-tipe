import chess
import random
from opening_dict import OUVERTURES

def historique(board):
    # Genere un tuple de chaines UCI correspondant exactement aux cles de opening_dict
    return tuple(move.uci() for move in board.move_stack)

def coup_ouverture(board):
    hist = historique(board)
    
    # Si la suite de coups actuelle est dans le dictionnaire d'ouvertures
    if hist in OUVERTURES:
        coups_possibles = OUVERTURES[hist]
        
        if coups_possibles:
            # Choisit un coup au hasard parmi les coups theoriques valides
            coup_choisi_uci = random.choice(coups_possibles)
            coup_legal = chess.Move.from_uci(coup_choisi_uci)
            
            # Securite : on verifie que le coup du dictionnaire est bien legal dans cette position
            if coup_legal in board.legal_moves:
                print(f"[OUVERTURE] Coup théorique trouvé : {coup_choisi_uci} (Option choisie parmi {len(coups_possibles)} possibilité(s))")
                return coup_legal
            else:
                print(f"[OUVERTURE] Alerte : Le coup théorique {coup_choisi_uci} n'est pas légal !")
    
    # Si on est sorti du dictionnaire (Book break), on renvoie None pour laisser le bot reflechir
    return None