from flask import Flask, render_template, request, redirect, session, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_session import Session
import json
import random

# Flask setup
app = Flask(__name__)
app.secret_key = 'cs50_final_secret_key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# setup of Database
DATABASE = "users.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

# to avoid memory leaks


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# Load the players
with open("data/players.json") as f:
    all_players = json.load(f)

# the different routes

# registering user


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hash_pw = generate_password_hash(password)

        db = get_db()
        try:
            db.execute("INSERT INTO users (username, hash, wins) VALUES (?, ?, 0)", (username, hash_pw))
            db.commit()
        except:
            return "Username already taken."
        return redirect("/login")
    return render_template("register.html")

# logging in


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")
        return "Invalid credentials"
    return render_template("login.html")

# logout linked to button


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# code for leaderboard (top 10)


@app.route("/")
def index():
    wins = 0
    username = None
    leaderboard = []

    db = get_db()

    if "user_id" in session:
        result = db.execute("SELECT username, wins FROM users WHERE id = ?",
                            (session["user_id"],)).fetchone()
        if result:
            username = result["username"]
            wins = result["wins"]

    leaderboard = db.execute(
        "SELECT username, wins FROM users ORDER BY wins DESC LIMIT 10"
    ).fetchall()

    return render_template("index.html", wins=wins, username=username, leaderboard=leaderboard)

# code for drafting players


@app.route("/draft", methods=["GET", "POST"])
def draft():
    if request.method == "POST":
        selected_names = {
            "PG": request.form.get("PG"),
            "SG": request.form.get("SG"),
            "SF": request.form.get("SF"),
            "PF": request.form.get("PF"),
            "C": request.form.get("C"),
        }

        user_team = {}
        for pos, name in selected_names.items():
            for player in all_players[pos]:
                if player["name"] == name:
                    user_team[pos] = player
                    break

        ai_team = {pos: random.choice(all_players[pos]) for pos in all_players}

        def calculate_score(team):
            return sum(player["pts"] + player["reb"] + player["ast"] for player in team.values())

        user_score = calculate_score(user_team)
        ai_score = calculate_score(ai_team)

        winner = "You Win!" if user_score > ai_score else "You Lose!" if user_score < ai_score else "It's a Tie!"

        if user_score > ai_score and "user_id" in session:
            db = get_db()
            db.execute("UPDATE users SET wins = wins + 1 WHERE id = ?", (session["user_id"],))
            db.commit()

        return render_template("result.html",
                               user_team=user_team,
                               ai_team=ai_team,
                               user_score=user_score,
                               ai_score=ai_score,
                               winner=winner)

    draft_pool = {pos: random.sample(players, 3) for pos, players in all_players.items()}
    return render_template("draft.html", draft_pool=draft_pool)

# Makes the website run locally for testing


if __name__ == "__main__":
    app.run(debug=True)
