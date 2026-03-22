import os

# Bot name from environment, defaults to "Syn" for backwards compatibility
BOT_NAME = os.getenv("TFBOT_NAME", "Syn").strip() or "Syn"

# Helper function to replace bot name placeholder in messages
def _format_message(message: str) -> str:
    """Replace {BOT_NAME} placeholder with actual bot name."""
    return message.replace("{BOT_NAME}", BOT_NAME)

TF_CHARACTERS = [

    ##ST - Scenarios - Other

    {
        "name": "Catrina",
        "gender": "female",
        "genderswap": None,
        "age": "teen",
        "type": "hybrid",
        "avatar_path": "avatars/catrina.png",
        "folder": "catrina",
        "message": "triggers one of {BOT_NAME}'s weirder pranksâ€”a charm meant for 'feline agility training.' A puff of magic later, their balance is flawless, ears twitch at every sound, and they can't shake the urge to chase anything that moves."
    },
    
    {
        "name": "Yui Gyaru",
        "folder": "yuiGyaru",
        "message": " finds one of {BOT_NAME}'s trap and transforms."
    },

    {
        "name": "Claus Gyaru",
        "folder": "clausgyaru",
        "message": " finds one of {BOT_NAME}'s trap and transforms."
    },

    {
        "name": "RitaBE",
        "folder": "rita_be",
        "message": " finds one of {BOT_NAME}'s trap and transforms."
    },
    {
        "name": "JohnGB Mannequin",
        "folder": "johnGB_mannequin",
        "message": " finds one of {BOT_NAME}'s trap and transforms."
    },
    {
        "name": "KiyoshiGB Mannequin",
        "folder": "kiyoshiGB_mannequin",
        "message": " finds one of {BOT_NAME}'s trap and transforms."
    },
    {
        "name": "Katrina Mannequin",
        "folder": "katrina_mannequin",
        "message": " finds one of {BOT_NAME}'s trap and transforms."
    },
    {
        "name": "Kyoko Mannequin",
        "folder": "kyoko_mannequin",
        "message": " finds one of {BOT_NAME}'s trap and transforms."
    },


]


