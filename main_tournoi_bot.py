import chess
import time
import datetime
import random
from engines import naif
from engines import minimax
from engines import minimax_elagage
from engines import minimax_elagage_quiescence
from engines import minimax_elagage_quiescence_memo
from engines import minimax_elagage_quiescence_endgame
import dico_ouvertures

# --- CONFIGURATION DU MATCH ---
NOMBRE_DE_PARTIES = 50

# "NAIF", "MINIMAX", "ELAGAGE", "QUIESCENCE", "MEMO", "ENDGAME"
TYPE_BOT_BLANC = "MEMO"
TYPE_BOT_NOIR = "QUIESCENCE"

# Profondeurs respectives
PROF_MINIMAX = 3
PROF_ELAGAGE = 4
PROF_QUIESCENCE = 4
PROF_MEMO = 5
PROF_ENDGAME = 5

# Utilisation des ouvertures
UTILISER_OUVERTURES = True

def obtenir_coup_bot(board, type_bot, couleur):
    """Gere la logique de selection du coup selon le bot choisi"""
    debut_coup = time.time()
    coup = None
    est_ouverture = False
    noeuds = 0

    if UTILISER_OUVERTURES:
        try:
            coup = dico_ouvertures.coup_ouverture(board)
            if coup is not None:
                est_ouverture = True
                noeuds = 0
        except:
            pass

    if coup is None:
        if type_bot == "NAIF":
            coups_legaux = list(board.legal_moves)
            if coups_legaux:
                scores = naif.score_capture(board, coups_legaux)
                meilleurs = naif.meilleurs_coups(scores)
                limite = max(1, round((len(meilleurs)+4)/8))
                coup = random.choice(meilleurs[:limite])
                noeuds = len(coups_legaux)

        elif type_bot == "MINIMAX":
            coup, noeuds = minimax.meilleur_coup(board, prof=PROF_MINIMAX, couleur=couleur)

        elif type_bot == "ELAGAGE":
            coup, noeuds = minimax_elagage.meilleur_coup(board, prof=PROF_ELAGAGE, couleur=couleur)

        elif type_bot == "QUIESCENCE":
            coup, noeuds = minimax_elagage_quiescence.meilleur_coup(board, prof=PROF_QUIESCENCE, couleur=couleur)

        elif type_bot == "MEMO":
            coup, noeuds = minimax_elagage_quiescence_memo.meilleur_coup(board, prof=PROF_MEMO, couleur=couleur)

        elif type_bot == "ENDGAME":
            coup, noeuds = minimax_elagage_quiescence_endgame.meilleur_coup(board, prof=PROF_ENDGAME, couleur=couleur)

    temps_reflexion = time.time() - debut_coup
    return coup, est_ouverture, temps_reflexion, noeuds

def formater_pgn_san(stats_partie):
    """Transforme une liste de coups SAN en une chaîne formatee standard PGN (1. e4 e5 2. Nf3...)"""
    liste_coups = [s['san'] for s in stats_partie]
    pgn_liste = []
    for i in range(0, len(liste_coups), 2):
        num_coup = (i // 2) + 1
        coup_blanc = liste_coups[i]
        if i + 1 < len(liste_coups):
            coup_noir = liste_coups[i+1]
            pgn_liste.append(f"{num_coup}. {coup_blanc} {coup_noir}")
        else:
            pgn_liste.append(f"{num_coup}. {coup_blanc}")
    return " ".join(pgn_liste)

def simulation():
    """Joue exactement UNE partie et renvoie les statistiques"""
    echiquier = chess.Board()
    
    stats_partie = []
    debut_partie = time.time()

    while not echiquier.is_game_over():
        tour_blanc = echiquier.turn == chess.WHITE
        type_actuel = TYPE_BOT_BLANC if tour_blanc else TYPE_BOT_NOIR
        couleur_actuelle = chess.WHITE if tour_blanc else chess.BLACK

        coup, est_ouv, t_calc, n_noeuds = obtenir_coup_bot(echiquier, type_actuel, couleur_actuelle)

        if coup is None: break

        san_coup = echiquier.san(coup)
        stats_partie.append({
            'bot': "Blanc" if tour_blanc else "Noir",
            't': t_calc,
            'noeuds' : n_noeuds,
            'san': san_coup
        })
        
        echiquier.push(coup)
    
    san_complet = formater_pgn_san(stats_partie)
    duree_totale = time.time() - debut_partie

    # Au lieu d'ecrire le fichier, on renvoie un dictionnaire avec toutes les infos
    return {
        'resultat': echiquier.result(),
        'duree': duree_totale,
        'stats': stats_partie,
        'san_complet': san_complet
    }
def lancer_tournoi():
    nom_fichier = datetime.datetime.now().strftime("tournoi_%Hh%Mm%Ss.txt")
    
    globs = {
        "Blanc": {"victoires": 0, "t_total": 0.0, "n_total": 0, "c_total": 0},
        "Noir": {"victoires": 0, "t_total": 0.0, "n_total": 0, "c_total": 0},
        "Nulles": 0
    }

    print(f"--- DÉBUT DU TOURNOI : {NOMBRE_DE_PARTIES} PARTIES ---")
    
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(f"TOURNOI : {TYPE_BOT_BLANC} vs {TYPE_BOT_NOIR}\n\n")

        for i in range(1, NOMBRE_DE_PARTIES + 1):
            res_partie = simulation()
            
            r = res_partie['resultat']
            if r == "1-0": globs["Blanc"]["victoires"] += 1
            elif r == "0-1": globs["Noir"]["victoires"] += 1
            else: globs["Nulles"] += 1

            f.write(f"### PARTIE {i} | Résultat : {r} ###\n")
            f.write(f"{'Coup':<5} | {'Bot':<6} | {'Temps':<8} | {'Noeuds':<10} | {'SAN'}\n")
            
            for idx, s in enumerate(res_partie['stats']):
                bot = s['bot']
                f.write(f"{(idx//2)+1:<5} | {bot:<6} | {s['t']:<8.3f}s | {s['noeuds']:<10} | {s['san']}\n")
                
                if s['noeuds'] > 0: 
                    globs[bot]["t_total"] += s['t']
                    globs[bot]["n_total"] += s['noeuds']
                    globs[bot]["c_total"] += 1
            
            # Affichage de la suite de coups au format standard Lichess
            f.write("\nSUITE DE COUPS FORMATÉE (Copier-coller dans Lichess) :\n")
            f.write(res_partie['san_complet'] + " " + r + "\n\n")
            f.write("-" * 60 + "\n\n")

        # --- BILAN FINAL ---
        f.write("="*60 + "\n")
        f.write("BILAN STATISTIQUE DU TOURNOI\n")
        f.write("="*60 + "\n")
        
        for side in ["Blanc", "Noir"]:
            bot_name = TYPE_BOT_BLANC if side == "Blanc" else TYPE_BOT_NOIR
            t_moyen = globs[side]["t_total"] / max(1, globs[side]["c_total"])
            n_moyen = globs[side]["n_total"] / max(1, globs[side]["c_total"])
            nps = globs[side]["n_total"] / max(0.001, globs[side]["t_total"])
            
            f.write(f"BOT {side.upper()} ({bot_name}) :\n")
            f.write(f"- Victoires : {globs[side]['victoires']}\n")
            f.write(f"- Temps moyen / coup  : {t_moyen:.4f} s\n")
            f.write(f"- Noeuds moyens / coup : {int(n_moyen)}\n")
            f.write(f"- Noeuds par seconde   : {int(nps)} NPS\n\n")

    print(f"Rapport généré : {nom_fichier}")

lancer_tournoi()