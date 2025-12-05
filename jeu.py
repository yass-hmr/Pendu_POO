# jeu.py

ETAPES_PENDU = [
    """
    
    
    
    
    """,
    """
    
    
    
    
      ___
    """,
    """
      |
      |
      |
      |
      ___
    """,
    """
      ______
      |
      |
      |
      |
      ___
    """,
    """
      ______
      |    |
      |    O
      |
      |
      ___
    """,
    """
      ______
      |    |
      |    O
      |   /|\\
      |
      ___
    """,
    """
      ______
      |    |
      |    O
      |   /|\\
      |   / \\
      ___
    """
]


class Pendu:
    def __init__(self, mot, essais_max=8):
        self.mot_a_deviner = mot.upper()
        self.essais_max = essais_max
        self.essais_restants = essais_max
        self.lettres_trouvees = set()
        self.lettres_proposees = set()

    # ---------- LOGIQUE DU JEU ----------

    def afficher_mot(self):
        affichage = ""
        for lettre in self.mot_a_deviner:
            if lettre in self.lettres_trouvees:
                affichage += lettre + " "
            else:
                affichage += "_ "
        return affichage.strip()

    def proposer_lettre(self, lettre):
        lettre = lettre.upper()

        if len(lettre) != 1 or not lettre.isalpha():
            return "Entrée invalide. Propose une seule lettre."

        if lettre in self.lettres_proposees:
            return f"Tu as déjà proposé {lettre}."

        self.lettres_proposees.add(lettre)

        if lettre in self.mot_a_deviner:
            self.lettres_trouvees.add(lettre)
            return f"Bien joué ! {lettre} est dans le mot."
        else:
            self.essais_restants -= 1
            return f"Raté... {lettre} n'est pas dans le mot."

    def proposer(self, tentative):
        tentative = tentative.upper().strip()

        if not tentative:
            return "Tu n'as rien entré."

        # Mot entier
        if len(tentative) > 1:
            if not tentative.isalpha():
                return "Le mot contient des caractères invalides."

            if tentative == self.mot_a_deviner:
                self.lettres_trouvees.update(set(self.mot_a_deviner))
                return "Incroyable ! Tu as deviné le mot entier !"
            else:
                self.essais_restants -= 1
                return "Raté... Ce n'était pas le bon mot."
        # Lettre
        return self.proposer_lettre(tentative)

    def est_gagne(self):
        return all(l in self.lettres_trouvees for l in self.mot_a_deviner)

    def est_perdu(self):
        return self.essais_restants <= 0

    def etat_pendu_ascii(self):
        erreurs = self.essais_max - self.essais_restants
        index = min(erreurs, len(ETAPES_PENDU) - 1)
        return ETAPES_PENDU[index]

    # ---------- SÉRIALISATION POUR LA SESSION ----------

    def to_dict(self):
        return {
            "mot_a_deviner": self.mot_a_deviner,
            "essais_max": self.essais_max,
            "essais_restants": self.essais_restants,
            "lettres_trouvees": list(self.lettres_trouvees),
            "lettres_proposees": list(self.lettres_proposees),
        }

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(data["mot_a_deviner"], data["essais_max"])
        obj.essais_restants = data["essais_restants"]
        obj.lettres_trouvees = set(data["lettres_trouvees"])
        obj.lettres_proposees = set(data["lettres_proposees"])
        return obj
