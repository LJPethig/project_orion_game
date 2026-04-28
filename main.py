# main.py
# Flask entry point for Project Orion

from flask import Flask, render_template
from backend.api.game import game_bp
from backend.api.command import command_bp
from backend.api.systems import systems_bp
from backend.api.events import events_bp


app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# Register blueprints
app.register_blueprint(game_bp,     url_prefix="/api/game")
app.register_blueprint(command_bp,  url_prefix="/api/command")
app.register_blueprint(systems_bp,  url_prefix="/api/systems")
app.register_blueprint(events_bp,   url_prefix="/api/events")


# ── Page routes ──────────────────────────────────────────────

@app.route("/")
def start_screen():
    """start-screen screen — entry point."""
    return render_template("start_screen.html")


@app.route("/game_detail")
def game_detail():
    """Ship details screen — shown after New Game or Continue, before entering the game."""
    return render_template("game_detail.html")


@app.route("/game")
def game():
    """Main game screen."""
    return render_template("game.html")


if __name__ == "__main__":
    import webbrowser
    from config import DEBUG, PORT
    webbrowser.open(f"http://localhost:{PORT}")
    app.run(debug=DEBUG, port=PORT)