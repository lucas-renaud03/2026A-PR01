# ======================== game.py ========================

import pygame
import random
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRAVITY, JUMP_VELOCITY, SPRING_JUMP_VELOCITY,
    DOODLE_SPEED, DOODLE_WIDTH, DOODLE_HEIGHT, PLATFORM_WIDTH,
    MIN_PLATFORM_GAP, MAX_PLATFORM_GAP, CAMERA_SCROLL_THRESHOLD,
    PLATFORMS, doodle_dict, DOODLE_START_X, DOODLE_START_Y, LIVES
)
from platforms import create_platform, choose_platform_type
from doodle import doodle_left_img, doodle_right_img
from window import generate_initial_platforms


# ======================== PARTIE 3.1 ========================
def apply_gravity():
    doodle_dict["vel_y"] += GRAVITY
    doodle_dict["y"] += doodle_dict["vel_y"]
    return
    """
    Applique la gravité au Doodle en augmentant progressivement sa vitesse verticale (vel_y).
    Met à jour la position verticale (y) du Doodle.
    """
    # TODO : Mettez à jour la vitesse verticale puis la position verticale
    # du Doodle à partir de GRAVITY.

    return

# ===========================================================


# ======================== PARTIE 1.2 ========================
def move_doodle():
    """
    Gère le déplacement horizontal du Doodle selon les touches pressées (Flèches ou A/D).
    Implémente le passage fluide d'un côté de l'écran à l'autre (Screen Wrap).
    """
    keys = pygame.key.get_pressed()
    # TODO : Gérez les déplacements gauche/droite et mettez à jour
    # simultanément la direction et l'image du Doodle.
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        doodle_dict["x"] -= DOODLE_SPEED
        doodle_dict["direction"] = "left"
        doodle_dict["image"] = doodle_left_img
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        doodle_dict["x"] += DOODLE_SPEED
        doodle_dict["direction"] = "right"
        doodle_dict["image"] = doodle_right_img

    # TODO : Implémentez le Screen Wrap pour qu'une partie du Doodle puisse
    # sortir d'un côté avant de réapparaître de l'autre.
    # N'utilisez pas de dimensions numériques écrites directement.
    if doodle_dict["x"] >= SCREEN_WIDTH:
        doodle_dict["x"] = -DOODLE_WIDTH
    elif doodle_dict["x"] <= -DOODLE_WIDTH:
        doodle_dict["x"] = SCREEN_WIDTH


    return

# ===========================================================


# ======================== PARTIE 2.3 ========================
def move_platforms():
    """
    Déplace horizontalement les plateformes mobiles ("blue").
    Fait rebondir les plateformes lorsqu'elles atteignent les bords de la fenêtre.
    """

    for platform in PLATFORMS:
        if platform["type"] == "blue" and platform["active"]:

            platform["x"] += platform["vx"]

            # Bord droit
            if platform["x"] + platform["width"] >= SCREEN_WIDTH:
                platform["x"] = SCREEN_WIDTH - platform["width"]
                platform["vx"] *= -1

            # Bord gauche
            elif platform["x"] <= 0:
                platform["x"] = 0
                platform["vx"] *= -1

    return

# ===========================================================


# ======================== PARTIE 3.2 ========================
def check_platform_collisions():
    """
    Détecte si le Doodle atterrit sur une plateforme.
    Le rebond ne se produit QUE lorsque le Doodle descend (vel_y > 0)
    et qu'il arrive sur le dessus d'une plateforme.
    """

    # Aucun rebond pendant la montée ou lorsque le Doodle ne bouge pas vers le bas.
    if doodle_dict["vel_y"] <= 0:
        return

    doodle_rect = (
        doodle_dict["x"],
        doodle_dict["y"],
        DOODLE_WIDTH,
        DOODLE_HEIGHT
    )

    # Position approximative des pieds du Doodle à l'image précédente.
    previous_feet_y = (
        doodle_dict["y"]
        + DOODLE_HEIGHT
        - doodle_dict["vel_y"]
    )

    current_feet_y = doodle_dict["y"] + DOODLE_HEIGHT

    for platform in PLATFORMS:

        # Ignorer les plateformes inactives.
        if not platform["active"]:
            continue

        platform_rect = (
            platform["x"],
            platform["y"],
            PLATFORM_WIDTH,
            platform["height"]
        )

        # Il doit d'abord y avoir un chevauchement entre les rectangles.
        if not rects_collide(doodle_rect, platform_rect):
            continue

        # Vérifier que le Doodle arrive sur le dessus de la plateforme.
        # Une tolérance de 14 pixels est autorisée.
        if (
            previous_feet_y <= platform["y"] + 14
            and current_feet_y >= platform["y"]
        ):
            # Déterminer la puissance du rebond.
            if platform["type"] == "spring":
                doodle_dict["vel_y"] = SPRING_JUMP_VELOCITY
            else:
                doodle_dict["vel_y"] = JUMP_VELOCITY

            # Une plateforme brown devient inactive après utilisation.
            if platform["type"] == "brown":
                platform["active"] = False

            # Un seul rebond par appel.
            return

# ===========================================================


# ======================== PARTIE 3.3 ========================
def scroll_camera():
    """
    Fait défiler le monde lorsque le Doodle dépasse CAMERA_SCROLL_THRESHOLD.
    Met à jour le score et maintient les plateformes visibles.
    """

    if doodle_dict["y"] <= CAMERA_SCROLL_THRESHOLD:

        scroll = CAMERA_SCROLL_THRESHOLD - doodle_dict["y"]

        doodle_dict["y"] = CAMERA_SCROLL_THRESHOLD

        

        for platform in PLATFORMS:
            platform["y"] += scroll

            


        doodle_dict["score"] += scroll
        if doodle_dict["score"] > doodle_dict["high_score"]:
            doodle_dict["high_score"] = doodle_dict["score"]

        PLATFORMS[:] = [p for p in PLATFORMS if p["y"] <= SCREEN_HEIGHT]

        generate_new_platforms()

    # TODO : Lorsque le Doodle dépasse le seuil de caméra, il doit rester
    # visuellement au seuil pendant que les plateformes sont déplacées vers
    # le bas de la même distance.
    #
    # Le score doit représenter la distance verticale ainsi parcourue et le
    # meilleur score doit être mis à jour. Les plateformes sorties sous
    # l'écran doivent être retirées, puis de nouvelles plateformes générées.

    return

# ===========================================================


# ======================== PARTIE 3.4 ========================
def generate_new_platforms():
    """
    Génère de nouvelles plateformes au-dessus du haut de l'écran pour maintenir
    un flux continu lorsque la caméra défile.
    """

    # Si aucune plateforme n'existe, on ne peut pas déterminer
    # laquelle est actuellement la plus haute.
    if not PLATFORMS:
        return

    # La plateforme ayant le plus petit y est la plus haute.
    highest_platform = min(PLATFORMS, key=lambda platform: platform["y"])

    # Position de départ pour la prochaine plateforme.
    next_y = highest_platform["y"]

    # Continuer à générer des plateformes tant qu'il n'y en a pas
    # suffisamment au-dessus de l'écran.
    while next_y > -SCREEN_HEIGHT:
        gap = random.randint(MIN_PLATFORM_GAP, MAX_PLATFORM_GAP)
        next_y -= gap

        # Position horizontale valide.
        x = random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH)

        # 55 % green, 20 % blue, 13 % spring.
        # Le 12 % restant correspond automatiquement à brown.
        platform_type = choose_platform_type(0.55, 0.20, 0.13)

        platform = create_platform(x, next_y, platform_type)
        PLATFORMS.append(platform)

# ===========================================================


def check_game_over():
    """
    Vérifie si le Doodle tombe sous le bas de l'écran.
    Si oui, réduit les vies.
    Retourne True si la partie est terminée.
    """
    if doodle_dict["y"] > SCREEN_HEIGHT:
        doodle_dict["lives"] -= 1
        return True
    return False


def restart_game():
    """
    Réinitialise la partie : position du Doodle, vitesse, score et plateformes.
    """
    doodle_dict["x"] = DOODLE_START_X
    doodle_dict["y"] = DOODLE_START_Y
    doodle_dict["vel_y"] = 0.0
    doodle_dict["direction"] = "right"
    doodle_dict["image"] = doodle_right_img
    doodle_dict["score"] = 0
    doodle_dict["lives"] = LIVES

    generate_initial_platforms()


def rects_collide(r1, r2):
    """
    Vérifie si deux rectangles (x, y, largeur, hauteur) se chevauchent.
    Cette fonction est fournie et ne doit pas être modifiée.
    """
    return not (
        r1[0] + r1[2] <= r2[0] or r1[0] >= r2[0] + r2[2] or
        r1[1] + r1[3] <= r2[1] or r1[1] >= r2[1] + r2[3]
    )
