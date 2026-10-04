import chess
import time #pour savoir combien de temps dure chaque partie
import datetime
import random
from engines import naif
from engines import minimax
from engines import minimax_elagage
from engines import minimax_elagage_quiescence
from engines import minimax_elagage_quiescence_endgame
import dico_ouvertures


# --- CONFIGURATION DU MATCH ---
# "NAIF", "MINIMAX", "ELAGAGE", "QUIESCENCE", 'ENDGAME"
TYPE_BOT_BLANC = "ENDGAME"
TYPE_BOT_NOIR = "QUIESCENCE"

# Profondeurs respectives
PROF_MINIMAX = 3
PROF_ELAGAGE = 4
PROF_QUIESCENCE = 4
PROF_ENDGAME = 5

# Utilisation des ouvertures
UTILISER_OUVERTURES = True

def obtenir_coup_bot(board, type_bot, couleur, ouverture_active):
    """Gère la logique de sélection du coup selon le bot choisi"""
    
    # 0. Declenchement du chrono pour chaque coup
    debut_coup = time.time()

    coup = None
    est_ouverture = False

    # 1. Tentative d'ouverture
    if UTILISER_OUVERTURES and ouverture_active:
        try:
            coup = dico_ouvertures.coup_ouverture(board)
            if coup is not None:
                est_ouverture = True
        except:
            pass

    # 2. Logique des bots si pas d'ouverture
    if coup is None:
        if type_bot == "NAIF":
            coups_legaux = list(board.legal_moves)
            if coups_legaux:
                scores = naif.score_capture(board, coups_legaux)
                meilleurs = naif.meilleurs_coups(scores)
                n = len(meilleurs)
                limite = max(1, round((n+4)/8))
                coup = random.choice(meilleurs[:limite])

        elif type_bot == "MINIMAX":
            coup = minimax.meilleur_coup(board, prof=PROF_MINIMAX, couleur=couleur)

        elif type_bot == "ELAGAGE":
            coup = minimax_elagage.meilleur_coup(board, prof=PROF_ELAGAGE, couleur=couleur)

        elif type_bot == "QUIESCENCE":
            coup = minimax_elagage_quiescence.meilleur_coup(board, prof=PROF_QUIESCENCE, couleur=couleur)
    
        elif type_bot == "ENDGAME":
            coup = minimax_elagage_quiescence_endgame.meilleur_coup(board, prof=PROF_ENDGAME, couleur=couleur)

    temps_reflexion = time.time() - debut_coup
    return coup, est_ouverture, temps_reflexion

def simulation():
    echiquier = chess.Board()
    ouvertures_blancs = UTILISER_OUVERTURES
    ouvertures_noirs = UTILISER_OUVERTURES
    
    # Liste pour stocker les stats de la partie
    stats_partie = [] #num_coup, bot, temps, coup_san (san c'est pour l'encodage des coups genre e4 aulieu de mettre Nf3e4 avec le coup precedent)
    debut_partie = time.time()

    # Boucle de jeu
    while not echiquier.is_game_over():
        tour_blanc = echiquier.turn == chess.WHITE
        type_actuel = TYPE_BOT_BLANC if tour_blanc else TYPE_BOT_NOIR
        couleur_actuelle = chess.WHITE if tour_blanc else chess.BLACK
        ouv_active = ouvertures_blancs if tour_blanc else ouvertures_noirs

        coup, est_ouv, t_calc = obtenir_coup_bot(echiquier, type_actuel, couleur_actuelle, ouv_active)

        if coup is None: break

        # Mise à jour des drapeaux d'ouverture
        if tour_blanc: ouvertures_blancs = est_ouv
        else: ouvertures_noirs = est_ouv

        # Enregistrements des stats avant de jouer le coup
        san_coup = echiquier.san(coup)
        num_coup = (len(echiquier.move_stack) // 2) + 1
        stats_partie.append({
            'n': num_coup,
            'bot': "Blanc" if tour_blanc else "Noir",
            't': t_calc,
            'san': san_coup
        })
        
        # Et enfin on joue le coup
        echiquier.push(coup)

    fin_partie = time.time()
    duree_totale = fin_partie - debut_partie

    # --- GENERATION DU RAPPORT TEXTE ---
    nom_fichier = datetime.datetime.now().strftime("rapport_%Hh%Mm%Ss.txt")
    
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write("="*50 + "\n")
        f.write(f"RAPPORT DE MATCH : {TYPE_BOT_BLANC} vs {TYPE_BOT_NOIR}\n")
        f.write(f"PROFONDEURS :\n prof_minimax = {PROF_MINIMAX}\n prof_elagage = {PROF_ELAGAGE}\n prof_quiescence = {PROF_QUIESCENCE}\n prof_ engame = {PROF_ENDGAME}\n")
        f.write("="*50 + "\n")
        f.write(f"Résultat : {echiquier.result()}\n")
        f.write(f"Nombre de coups : {len(stats_partie)}\n")
        f.write(f"Durée totale : {duree_totale:.2f} secondes\n\n")
        
        f.write(f"{'#':<4} | {'Côté':<6} | {'Temps':<10} | {'Coup'}\n")
        f.write("-" * 35 + "\n")
        for s in stats_partie:
            f.write(f"{s['n']:<4} | {s['bot']:<6} | {s['t']:<10.4f}s | {s['san']}\n")
            
        f.write("\nSUITE DE COUPS COMPLETE :\n")
        f.write(" ".join([s['san'] for s in stats_partie]))

    print(f"\nPartie terminée en {duree_totale:.2f}s. Rapport généré : {nom_fichier}")

simulation()