# main.py
# Flask entry point for Project Orion

import webbrowser
from flask import Flask, render_template
from backend.api.game import game_bp

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

# Register blueprints
app.register_blueprint(game_bp, url_prefix="/api/game")


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
    from config import DEBUG, PORT
    webbrowser.open(f"http://localhost:{PORT}")
    app.run(debug=DEBUG, port=PORT)
