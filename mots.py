# mots.py
import random
from pathlib import Path

DOSSIER_MOTS = Path("mots")


def fichier_pour(theme, difficulte):
    nom_fichier = f"{theme.lower()}_{difficulte.lower()}.txt"
    return DOSSIER_MOTS / nom_fichier


def charger_mots(nom_fichier):
    mots = []
    with open(nom_fichier, "r", encoding="utf-8") as f:
        for ligne in f:
            mot = ligne.strip()
            if mot:
                mots.append(mot)
    return mots


def choisir_mot(theme="animaux", difficulte="normal"):
    chemin = fichier_pour(theme, difficulte)
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier de mots introuvable : {chemin}")

    mots = charger_mots(chemin)
    if not mots:
        raise ValueError(f"Aucun mot dans : {chemin}")

    return random.choice(mots)
