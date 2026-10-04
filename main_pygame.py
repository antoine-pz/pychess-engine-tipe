import pygame
import chess
import chess.pgn  #pour la gestion du PGN
import chess.polyglot
import random   #pour choisir un coup random du bot naif
import threading #pour que Pygame ne bug pas quand on fait les calculs avec minimax
from engines import naif #code avec le bot naif
from engines import minimax  #code avec le bot minimax
from engines import minimax_elagage #code avec le bot minimax booste a l'elagage alpha-beta
from engines import minimax_elagage_quiescence_endgame   #contient egalement des tables de transpositions

import dico_ouvertures

#taille et fps
TAILLE_ECHIQUIER = 1000 #echiquier carre
TAILLE_CASE = TAILLE_ECHIQUIER // 8
FPS = 30

#couleur du bot
BOT_COULEUR = chess.BLACK #il joue les noirs par defaut
JOUEUR_COULEUR = chess.WHITE   #chess.WHITE est de type booleen

'''_________________BOT NAIF_________________'''
BOT_NAIF_ACTIF = False
'''__________________________________________'''

'''_________BOT MINMAX (sans elagage)________'''
BOT_MINIMAX_ACTIF = False
'''__________________________________________'''

'''_________BOT MINMAX (avec elagage)________'''
BOT_MINIMAX_ELAG_ACTIF = False
'''__________________________________________'''

'''______________BOT ENDGAME_________________'''
BOT_ENDGAME_ACTIF = True
'''__________________________________________'''

#couleurs (en rgb)
COULEUR_CASES_CLAIRES = (255, 255, 255)
COULEUR_CASES_SOMBRES = (105, 146, 62)
COULEUR_SELECTION = (226, 0, 0, 255)  #rgb-a pour la transparence
COULEUR_COUP_LEGAL = (166, 0, 0, 230)
COULEUR_TEXTE = (10, 10, 10)

#transparence lorsqu'on selectionne
transparence_selection = pygame.Surface((TAILLE_CASE, TAILLE_CASE), pygame.SRCALPHA)
transparence_coup_legal = pygame.Surface((TAILLE_CASE, TAILLE_CASE), pygame.SRCALPHA)

#police d'ecriture (pour le design des pieces)
POLICE_ECRITURE = "./police_ecriture/pecita.ttf"

#initialisation de pygame
pygame.init()
ecran = pygame.display.set_mode((TAILLE_ECHIQUIER, TAILLE_ECHIQUIER))
pygame.display.set_caption("Echiquier")
clock = pygame.time.Clock() #utile pour gerer les fps et utile plus tard pour limiter le temps pour chaque coup
police = pygame.font.Font(POLICE_ECRITURE, TAILLE_CASE - 8)

#echiquier de depart
echiquier = chess.Board()

#affichage coups legaux
case_selection = None #0 a 63 ou None
piece_selection = None    #chess.Piece ou None
case_avant_selection = None #pour remettre la piece a sa place si elle est lachee
coups_legaux_selection = []    #liste des coups legaux pour piece_selection
place_mode = False  #si False alors on ne bouge pas, si True on place la piece (si legal)
place_piece_type = chess.PAWN   #type de la piece a deplacer
place_piece_couleur = chess.WHITE #les blancs commencent en deplacant la premiere piece

#couleurs echiquier, pour verifier les coups legaux
couleur_claire = COULEUR_CASES_CLAIRES
couleur_sombre = COULEUR_CASES_SOMBRES

#variable de controle pour eviter de spammer les Threads en tache de fond
bot_en_calcul = False

def case_souris(pos):
    """Recupere la position de la souris et renvoie la case sur laquelle on est"""
    x, y = pos
    col, ligne = x // TAILLE_CASE, y // TAILLE_CASE
    if JOUEUR_COULEUR == chess.BLACK:
        case_cliquee = chess.square(7 - col, ligne)
    else:
        case_cliquee = chess.square(col, 7 - ligne)
    return case_cliquee  #pygame (0,0) = haut a gauche donc aux echecs la case a8 = 0

def dessiner_cases(case):
    """Calcule la position d'une case selon la perspective du joueur"""
    if JOUEUR_COULEUR == chess.BLACK:
        col = 7 - chess.square_file(case)   
        ligne = chess.square_rank(case) 
    else:
        col = chess.square_file(case)   
        ligne = 7 - chess.square_rank(case) 
    return pygame.Rect(col*TAILLE_CASE, ligne*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)

def dessiner_echiquier():
    """Fonction la plus importante, gere l'affichage de l'echiquier et des pieces, et la selection de coup"""
    for ligne in range(8):
        for col in range(8):
            x = col * TAILLE_CASE
            y = ligne * TAILLE_CASE
            if ((ligne + col) % 2 == 0): couleur = couleur_claire
            else: couleur = couleur_sombre  #on alterne clair et sombre
            pygame.draw.rect(ecran, couleur, (x, y, TAILLE_CASE, TAILLE_CASE)) #on dessine l'echiquier

    #si aucune piece n'est selectionnee
    if case_selection is not None:
        rect = dessiner_cases(case_selection)  #on recupere le carre sur lequel on se trouve
        transparence_selection.fill((0, 0, 0, 0))   #on efface l'ancienne couleur
        transparence_selection.fill((COULEUR_SELECTION[0], COULEUR_SELECTION[1], COULEUR_SELECTION[2], COULEUR_SELECTION[3]))
        ecran.blit(transparence_selection, rect.topleft)    #on superpose au bon endroit

    #on dessine les coups legaux
    for coup in coups_legaux_selection:
        rect = dessiner_cases(coup)
        transparence_coup_legal.fill((0,0,0,0))
        transparence_coup_legal.fill((COULEUR_COUP_LEGAL[0], COULEUR_COUP_LEGAL[1], COULEUR_COUP_LEGAL[2], COULEUR_COUP_LEGAL[3]))
        ecran.blit(transparence_coup_legal, rect.topleft)   #on superpose de la meme maniere (avec un indice de transparence moins grand)

    #on dessine toutes les pieces non selectionnees
    for case in chess.SQUARES:
        piece = echiquier.piece_at(case)    #on recupere la piece sur la case (case = a8)
        if piece is None:
            continue
        if case_avant_selection is not None and case == case_avant_selection:
            continue    #si la piece n'a pas ete selectionnee ou qu'elle a deja ete deplacee
        rect = dessiner_cases(case)
        symbole = piece.unicode_symbol()    #on recupere le symbole de la piece a afficher
        rendu_piece = police.render(symbole, True, COULEUR_TEXTE)  #True pour lisser les bords et on met la couleur
        centre_piece = rendu_piece.get_rect(center = rect.center)   #pour centrer le symbole au milieu de la case
        ecran.blit(rendu_piece, centre_piece)   #on affiche les symboles des pieces

    #on dessine la piece selectionnee
    if piece_selection is not None:
        mx, my = pygame.mouse.get_pos() #on recupere la position de la souris
        symbole = piece_selection.unicode_symbol()  #on recupere le symbole de la piece
        rendu_piece = police.render(symbole, True, COULEUR_TEXTE)
        centre_piece = rendu_piece.get_rect(center = (mx, my))  #on centre la piece sur la souris
        ecran.blit(rendu_piece, centre_piece)

def liste_coups_legaux_selection(case):
    """Retourne la liste des coups legaux depuis la piece selectionnee"""
    coups = []
    for coup in echiquier.legal_moves:  #on regarde dans les coups autorises
        if coup.from_square == case:    #si la case de depart est bien la case selectionnee
            coups.append(coup.to_square)    #on l'ajoute dans la liste des coups
    return coups

def deplacements(case_depart, case_arrivee):
    """Teste un coup, le joue si legal, gere la promotion si besoin (juste en dame pour l'instant)"""
    #promotion si pion atteint la derniere rangee
    piece = echiquier.piece_at(case_depart)
    promo_piece_type = None
    if piece and piece.piece_type == chess.PAWN:    #seuls les pions peuvent etre promus
        ligne_arrivee = chess.square_rank(case_arrivee)
        if (piece.color == chess.WHITE and ligne_arrivee == 7) or (piece.color == chess.BLACK and ligne_arrivee == 0):
            #promotion (pour l'instant Dame par defaut)
            promo_piece_type = chess.QUEEN

    coup = chess.Move(case_depart, case_arrivee, promotion = promo_piece_type)
    if coup in echiquier.legal_moves: #si le coup est legal
        echiquier.push(coup)  #on le joue
        return True #on indique que le coup a ete joue
    return False    #on indique que le coup n'etait pas legal

def apparaitre_piece(case, type_piece, couleur):
    echiquier.set_piece_at(case, chess.Piece(type_piece, couleur))

#main
running = True
while running:
    #on recupere toutes les entrees de touches et les mouvements/clics de la souris
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:  #si on ferme la fenetre
            running = False

        #si le bot reflechit alors on evite de laisser l'humain cliquer partout
        if bot_en_calcul:
            continue

        #si c'est une touche
        elif ev.type == pygame.KEYDOWN:
            #on vide la case sous la piece selectionnee
            if ev.key == pygame.K_d:
                mx, my = pygame.mouse.get_pos()
                case = case_souris((mx,my))
                echiquier.remove_piece_at(case)

            #on reset la partie
            elif ev.key == pygame.K_r:
                echiquier.reset()

            #on reset le dernier coup
            elif ev.key == pygame.K_u:
                if echiquier.move_stack:
                    echiquier.pop()

        #si c'est un clic (enfoncement)
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            case = case_souris((mx,my))
            piece = echiquier.piece_at(case)

            if place_mode:
                #placer la piece choisie (la remplace si deja presente)
                apparaitre_piece(case, place_piece_type, place_piece_couleur)
                #on rafraichit l'affichage
                case_selection = None
                coups_legaux_selection = []
                piece_selection = None
                case_avant_selection = None
            else:
                #si on clique sur une de nos pieces, alors affichage des coups legaux
                if piece and piece.color == JOUEUR_COULEUR: #securite : le joueur ne peut cliquer que sur ses pieces
                    case_selection = case
                    piece_selection = piece
                    case_avant_selection = case
                    coups_legaux_selection = liste_coups_legaux_selection(case)
                else:
                    #si on clique sur case vide, alors on essaye de s'y deplacer
                    if case_selection is not None:  #si on n'avait pas selectionne de piece avant alors rien
                        coup = deplacements(case_selection, case)   #renvoie un booleen et joue
                        if coup:
                            #si coup legal alors joue et on remet tout a vide
                            case_selection = None
                            coups_legaux_selection = []
                            piece_selection = None
                            case_avant_selection = None
                        else:
                            #si coup interdit, alors on remet tout a vide
                            case_selection = None
                            coups_legaux_selection = []
                            piece_selection = None
                            case_avant_selection = None

        #si c'est un clic (relachement)
        elif ev.type == pygame.MOUSEBUTTONUP:
            #lorsqu'on relache, on teste la case sous la position de la souris
            if piece_selection is not None and not place_mode and case_avant_selection is not None:
                mx, my = ev.pos
                case = case_souris((mx,my))
                coup = deplacements(case_avant_selection, case)
                #on lache la piece qu'on tenait
                case_selection = None
                piece_selection = None
                case_avant_selection = None
                coups_legaux_selection = []

    #hors de la boucle d'evenements Pygame
    #le robot joue des que c'est son tour
    if not echiquier.is_game_over() and echiquier.turn == BOT_COULEUR:
        
        # On ne traite le tour du bot que s'il n'est pas déjà en train de calculer en tâche de fond
        if not bot_en_calcul:
            
            # --- AJOUT DE LA LOGIQUE D'OUVERTURE (de main_tournoi_bot) ---
            coup_ouverture = None
            try:
                # Cherche un coup dans le dictionnaire (qui inclut le choix aléatoire s'il y a plusieurs variantes)
                coup_ouverture = dico_ouvertures.coup_ouverture(echiquier)
            except Exception as e:
                print(f"[ERREUR DICO OUVERTURE] : {e}")
            
            # Si un coup d'ouverture valide est disponible, on le joue directement (pas besoin de thread)
            if coup_ouverture is not None:
                echiquier.push(coup_ouverture)
            else:
                # Sinon (le dictionnaire ne renvoie rien), on bascule sur la recherche classique du bot actif
                
                '''_________________BOT NAIF_________________'''
                if BOT_NAIF_ACTIF:
                    coups_legaux = list(echiquier.legal_moves)
                    if coups_legaux != []:
                        scores = naif.score_capture(echiquier, coups_legaux)
                        meilleurs = naif.meilleurs_coups(scores)
                        n = len(meilleurs)
                        choix = [i for i in range(round((n+4)/8))]
                        choisi = random.choice(choix)
                        coup_bot = meilleurs[choisi]
                        echiquier.push(coup_bot)
                '''__________________________________________'''

                '''_________BOT MINMAX (sans elagage)________'''
                if BOT_MINIMAX_ACTIF:
                    bot_en_calcul = True
                    def jouer_coup_bot_se():
                        global bot_en_calcul
                        coups_legaux = list(echiquier.legal_moves)
                        if coups_legaux != []:
                            meilleur, noeuds = minimax.meilleur_coup(echiquier, prof=3, couleur=BOT_COULEUR)
                            echiquier.push(meilleur)
                        bot_en_calcul = False #libere le verrou apres le calcul
                        
                    threading.Thread(target=jouer_coup_bot_se).start()
                '''__________________________________________'''

                '''_________BOT MINMAX (avec elagage)________'''
                if BOT_MINIMAX_ELAG_ACTIF:
                    bot_en_calcul = True
                    def jouer_coup_bot_e():
                        global bot_en_calcul
                        coups_legaux = list(echiquier.legal_moves)
                        if coups_legaux != []:
                            meilleur, noeuds = minimax_elagage.meilleur_coup(echiquier, prof=4, couleur=BOT_COULEUR)
                            echiquier.push(meilleur)
                        bot_en_calcul = False
                        
                    threading.Thread(target=jouer_coup_bot_e).start()
                '''__________________________________________'''

                '''_______________BOT ENDGAME________________'''
                if BOT_ENDGAME_ACTIF:
                    bot_en_calcul = True
                    def jouer_coup_bot_end():
                        global bot_en_calcul
                        coups_legaux = list(echiquier.legal_moves)
                        if coups_legaux != []:
                            meilleur, noeuds = minimax_elagage_quiescence_endgame.meilleur_coup(echiquier, prof=4, couleur=BOT_COULEUR)
                            echiquier.push(meilleur)
                        bot_en_calcul = False
                        
                    threading.Thread(target=jouer_coup_bot_end).start()
                '''__________________________________________'''

    #verification de fin de partie
    if not bot_en_calcul and echiquier.is_game_over():
        if echiquier.is_stalemate():
            print("Nulle")
        if echiquier.is_checkmate():
            if echiquier.turn == BOT_COULEUR:
                joueur_couleur = "blanc" if JOUEUR_COULEUR == chess.WHITE else "noir"
                print("Victoire ", joueur_couleur)
            else:
                bot_couleur = "blanc" if BOT_COULEUR == chess.WHITE else "noir"
                print("Victoire ", bot_couleur)
        running = False

    #on dessinne enfin l'ecran avec l'echiquier dessus
    ecran.fill((0,0,0)) #rempli l'ecran en noir
    dessiner_echiquier()    #dessine l'echiquier par dessus

    pygame.display.flip()   #rafraichit tout l'ecran
    clock.tick(FPS) #on rentre dans le while 30 fois par seconde

# PRINTS DU PGN APRES LA SORTIE DE LA BOUCLE
print("\n" + "="*40)
print("             PGN DE LA PARTIE           ")
print("="*40)

partie_pgn = chess.pgn.Game.from_board(echiquier)   #tout simplement, et ca sauvegarde tout

if BOT_COULEUR == chess.WHITE:
    partie_pgn.headers["White"] = "Moteur (Bot)"
    partie_pgn.headers["Black"] = "Joueur (Humain)"
else:
    partie_pgn.headers["White"] = "Joueur (Humain)"
    partie_pgn.headers["Black"] = "Moteur (Bot)"

partie_pgn.headers["Result"] = echiquier.result()

print(partie_pgn)
print("="*40 + "\n")

pygame.quit()