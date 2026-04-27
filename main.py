# main.py
# Flask entry point for Project Orion

from flask import Flask, render_template
from backend.api.game import game_bp
from backend.api.command import command_bp
from backend.api.systems import systems_bp
from backend.api.events import events_bp
from backend.models.game_manager import game_manager


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
def splash():
    """Splash screen — entry point."""
    return render_template("splash.html")


@app.route("/details")
def details():
    """Ship details screen — shown after New Game or Continue, before entering the game."""
    return render_template("details.html")


@app.route("/game")
def game():
    """Main game screen."""
    return render_template("game.html")


if __name__ == "__main__":
    import webbrowser
    from config import DEBUG, PORT
    webbrowser.open(f"http://localhost:{PORT}")
    app.run(debug=DEBUG, port=PORT)