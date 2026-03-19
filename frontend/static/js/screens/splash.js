// frontend/static/js/screens/splash.js
// Splash screen — click anywhere to start a new game and go to the main screen

document.addEventListener('DOMContentLoaded', () => {
    const screen = document.getElementById('splash-screen');

    screen.addEventListener('click', startGame);

    // Also allow Enter key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') startGame();
    });
});

async function startGame() {
    // Prevent double-clicks firing twice
    document.getElementById('splash-screen').removeEventListener('click', startGame);

    try {
        // Tell the backend to initialise a new game
        const response = await fetch('/api/game/new', { method: 'POST' });
        const data = await response.json();

        if (!data.success) {
            console.error('Failed to start new game:', data);
            return;
        }

        // Fade out then redirect to main game screen
        const screen = document.getElementById('splash-screen');
        screen.classList.add('fade-out');

        screen.addEventListener('animationend', () => {
            window.location.href = '/game';
        });

    } catch (err) {
        console.error('Error starting game:', err);
    }
}
