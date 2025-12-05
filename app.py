# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from jeu import Pendu
from mots import choisir_mot

app = Flask(__name__)
app.secret_key = "change-moi-en-cle-secrete"


THEMES_DISPONIBLES = ["animaux", "nourriture", "informatique", "sport", "geo"]
DIFFICULTES = ["facile", "normal", "difficile"]


def get_scores():
    """
    scores = {
        "solo": {"parties": 0, "victoires": 0, "defaites": 0},
        "duo": {"joueur1": {"nom": "...", "score": 0},
                "joueur2": {"nom": "...", "score": 0}}
    }
    """
    if "scores" not in session:
        session["scores"] = {
            "solo": {"parties": 0, "victoires": 0, "defaites": 0},
            "duo": {
                "joueur1": {"nom": "Joueur 1", "score": 0},
                "joueur2": {"nom": "Joueur 2", "score": 0},
            },
        }
    return session["scores"]


@app.route("/", methods=["GET", "POST"])
def index():
    scores = get_scores()

    if request.method == "POST":
        mode = request.form.get("mode", "solo")

        session["mode"] = mode
        session["game_scored"] = False  # pour ne pas compter deux fois la même partie

        if mode == "solo":
            theme = request.form.get("theme", "animaux")
            difficulte = request.form.get("difficulte", "normal")

            if theme not in THEMES_DISPONIBLES:
                theme = "animaux"
            if difficulte not in DIFFICULTES:
                difficulte = "normal"

            session["theme"] = theme
            session["difficulte"] = difficulte

            mot = choisir_mot(theme, difficulte)
            essais_max = 10 if difficulte == "facile" else 8 if difficulte == "normal" else 6

            jeu = Pendu(mot, essais_max=essais_max)
            session["game"] = jeu.to_dict()

            return redirect(url_for("game"))

        else:  # mode deux joueurs
            joueur1 = request.form.get("joueur1", "Joueur 1") or "Joueur 1"
            joueur2 = request.form.get("joueur2", "Joueur 2") or "Joueur 2"
            session["joueur1"] = joueur1
            session["joueur2"] = joueur2

            return redirect(url_for("secret_word"))

    return render_template(
        "index.html",
        themes=THEMES_DISPONIBLES,
        difficultes=DIFFICULTES,
        scores=get_scores(),
    )


@app.route("/secret", methods=["GET", "POST"])
def secret_word():
    """
    Page où le Joueur 1 tape le mot secret (mode deux joueurs).
    """
    if session.get("mode") != "duo":
        return redirect(url_for("index"))

    if request.method == "POST":
        mot_secret = request.form.get("mot_secret", "").strip()
        if not mot_secret.isalpha() or len(mot_secret) < 3:
            message = "Le mot doit contenir au moins 3 lettres et uniquement des lettres."
            return render_template(
                "secret.html",
                message=message,
                joueur1=session.get("joueur1", "Joueur 1"),
                joueur2=session.get("joueur2", "Joueur 2"),
            )

        essais_max = 8
        jeu = Pendu(mot_secret, essais_max=essais_max)
        session["game"] = jeu.to_dict()
        session["game_scored"] = False

        return redirect(url_for("game"))

    return render_template(
        "secret.html",
        joueur1=session.get("joueur1", "Joueur 1"),
        joueur2=session.get("joueur2", "Joueur 2"),
    )


@app.route("/game", methods=["GET", "POST"])
def game():
    if "game" not in session:
        return redirect(url_for("index"))

    scores = get_scores()
    mode = session.get("mode", "solo")
    jeu = Pendu.from_dict(session["game"])
    message = ""

    if request.method == "POST" and not (jeu.est_gagne() or jeu.est_perdu()):
        tentative = request.form.get("tentative", "")
        message = jeu.proposer(tentative)
        session["game"] = jeu.to_dict()

    # Gestion du score à la fin de la partie (une seule fois)
    if (jeu.est_gagne() or jeu.est_perdu()) and not session.get("game_scored", False):
        if mode == "solo":
            scores["solo"]["parties"] += 1
            if jeu.est_gagne():
                scores["solo"]["victoires"] += 1
            else:
                scores["solo"]["defaites"] += 1
        else:
            # Dans ce mode, Joueur 2 devine le mot
            if jeu.est_gagne():
                scores["duo"]["joueur2"]["score"] += 1
            else:
                scores["duo"]["joueur1"]["score"] += 1

        session["scores"] = scores
        session["game_scored"] = True

    return render_template(
        "game.html",
        jeu=jeu,
        message=message,
        mode=mode,
        scores=scores,
        theme=session.get("theme"),
        difficulte=session.get("difficulte"),
        joueur1=session.get("joueur1"),
        joueur2=session.get("joueur2"),
    )


@app.route("/nouvelle-partie")
def nouvelle_partie():
    mode = session.get("mode", "solo")

    if mode == "solo":
        theme = session.get("theme", "animaux")
        difficulte = session.get("difficulte", "normal")
        mot = choisir_mot(theme, difficulte)
        essais_max = 10 if difficulte == "facile" else 8 if difficulte == "normal" else 6
        jeu = Pendu(mot, essais_max=essais_max)
        session["game"] = jeu.to_dict()
        session["game_scored"] = False
        return redirect(url_for("game"))
    else:
        # On redemande un mot secret au Joueur 1
        session["game_scored"] = False
        return redirect(url_for("secret_word"))


@app.route("/reset-scores")
def reset_scores():
    session.pop("scores", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
