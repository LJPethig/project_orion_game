// frontend/static/js/core/constants.js
// Frontend constants — mirrors config.py on the backend.
// Change values here to affect behaviour throughout the game.

const CONSTANTS = {
    DOOR_IMAGE_DISPLAY_MS:      4000,   // How long door/hatch images display before reverting to room
    REPAIR_COMPONENT_PAUSE_MS:  3000,   // Pause between component repairs so player can read message
    REST_SHIP_HOURS:            8,      // Ship hours that pass during rest — must match config.py REST_SHIP_HOURS
    EVENT_RESOLVED_LINGER_MS:   20000,   // Time event resolution message stays visible after blinking stops
};