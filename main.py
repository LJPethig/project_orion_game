# main.py
# Flask entry point for Project Orion

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
    """Main game screen — placeholder until Phase 7."""
    return "<h1 style='color:lime;background:#000;font-family:monospace;padding:40px'>Game screen coming in Phase 7</h1>"


if __name__ == "__main__":
    from config import DEBUG, PORT
    app.run(debug=DEBUG, port=PORT)
