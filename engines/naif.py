import chess

VALEURS_PIECES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 1000
}

def score_capture(board, coups):
    score = []
    for coup in coups:
        if board.is_capture(coup):
            victime = board.piece_at(coup.to_square)
            valeur_victime = VALEURS_PIECES.get(victime.piece_type, 0)
            score.append((10 + valeur_victime, coup))
        else:   #le coup n'est pas une capture
            score.append((0, coup))
    return score

#tri a bulles decroissant
def tri_decroissant(liste_coups):
    n = len(liste_coups)
    for i in range(n):
        for j in range(0, n-i-1):
            if liste_coups[j][0] < liste_coups[j+1][0]:
                liste_coups[j], liste_coups[j+1] = liste_coups[j+1], liste_coups[j]
    return liste_coups

def tri_efficace(liste_coups):
    #trie la liste de tuples (score, coup) par le score (index 0)
    def extraire_score(un_couple):
        return un_couple[0]
    return sorted(liste_coups, key=extraire_score, reverse=True)

def uniquement_coups(liste_coups_tries):
    return [coup for _, coup in liste_coups_tries]

'''Version naive, heuristique de gain'''
def meilleurs_coups(score):
    meilleurs_coups = []
    meilleure_valeur = float("-inf")
    for valeur, coup in score:
        if valeur > meilleure_valeur:
            meilleure_valeur = valeur
            meilleurs_coups.append((valeur, coup))
        elif valeur == meilleure_valeur:
            meilleurs_coups.append((valeur, coup))
    meilleurs_coups = tri_efficace(meilleurs_coups)  #on trie
    meilleurs_coups = uniquement_coups(meilleurs_coups) #on enleve les valeurs
    return meilleurs_coups  #on ne garde que les coups