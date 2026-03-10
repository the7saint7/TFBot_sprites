import os

# Bot name from environment, defaults to "Syn" for backwards compatibility
BOT_NAME = os.getenv("TFBOT_NAME", "Syn").strip() or "Syn"

# Helper function to replace bot name placeholder in messages
def _format_message(message: str) -> str:
    """Replace {BOT_NAME} placeholder with actual bot name."""
    return message.replace("{BOT_NAME}", BOT_NAME)

TF_CHARACTERS = [

    ##Treats of Summer

    {
        "name": "Johngbbimbo 1 (Treats of Summer)",
        "folder": "johnGBBimbo_1"
    },

    {
        "name": "Johngbbimbo 2 (Treats of Summer)",
        "folder": "johnGBBimbo_2"
    },

    {
        "name": "Johngbbimbo 3 (Treats of Summer)",
        "folder": "johnGBBimbo_3"
    },

    {
        "name": "Katrinabe (Treats of Summer)",
        "folder": "katrinaBE1"
    },

    {
        "name": "Kiyoshi (Treats of Summer)",
        "folder": "kiyoshiMILF"
    },

    {
        "name": "Kiyoshishortstack (Treats of Summer)",
        "folder": "kiyoshiShortStack"
    },

    {
        "name": "Shin2 (Treats of Summer)",
        "folder": "shin"
    },


]
