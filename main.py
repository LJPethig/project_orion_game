# main.py
# Flask entry point for Project Orion

from flask import Flask, render_template
from backend.api.game import game_bp
from backend.api.command import command_bp
import logging

resolver_logger = logging.getLogger('resolver')
resolver_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('resolver_debug.log')
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
resolver_logger.addHandler(handler)

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# Register blueprints
app.register_blueprint(game_bp,     url_prefix="/api/game")
app.register_blueprint(command_bp,  url_prefix="/api/command")


# ── Page routes ──────────────────────────────────────────────

@app.route("/")
def splash():
    """Splash screen — entry point."""
    return render_template("splash.html")


@app.route("/game")
def game():
    """Main game screen."""
    return render_template("game.html")


if __name__ == "__main__":
    import webbrowser
    from config import DEBUG, PORT
    webbrowser.open(f"http://localhost:{PORT}")
    app.run(debug=DEBUG, port=PORT)