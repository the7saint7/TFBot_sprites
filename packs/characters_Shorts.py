import os

# Bot name from environment, defaults to "Syn" for backwards compatibility
BOT_NAME = os.getenv("TFBOT_NAME", "Syn").strip() or "Syn"

# Helper function to replace bot name placeholder in messages
def _format_message(message: str) -> str:
    """Replace {BOT_NAME} placeholder with actual bot name."""
    return message.replace("{BOT_NAME}", BOT_NAME)

TF_CHARACTERS = [

    ##ST - Scenarios - Shorts

    {
        "name": "CorneliaGB (Shorts)",
        "gender": "male",
        "genderswap": "characters_ST/cornelia",
        "ageswap": "characters_STVariants/CorneliaAP",
        "gender_age_swap": None,
        "age": "teen",
        "type": "human",
        "avatar_path": "avatars/corneliaGB_shorts.png",
        "folder": "corneliaGB_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms.",
    },

    {
        "name": "Hinano (Shorts)",
        "avatar_path": "avatars/hinano_shorts.png",
        "folder": "hinano_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms."
    },

    {
        "name": "JackGB (Shorts)",
        "avatar_path": "avatars/jackGB_shorts.png",
        "folder": "jackGB_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms."
    },

    {
        "name": "John OneEye (Shorts)",
        "avatar_path": "avatars/john_oneEye.png",
        "folder": "johnOneEye_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms."
    },

    {
        "name": "John Styled (Shorts)",
        "avatar_path": "avatars/john_styled_shorts.png",
        "folder": "johnStyled_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms."
    },

    {
        "name": "KatrinaBimbo (Shorts)",
        "avatar_path": "avatars/katrinaBimbo_shorts.png",
        "folder": "katrinaBimbo_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms."
    },

    {
        "name": "Kutsumi (Shorts)",
        "avatar_path": "avatars/kutsumi_shorts.png",
        "folder": "kutsumi_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms."
    },

    {
        "name": "Reika (Shorts)",
        "avatar_path": "avatars/reika_shorts.png",
        "folder": "reika_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms."
    },

    {
        "name": "Sera (Shorts)",
        "avatar_path": "avatars/sera_shorts.png",
        "folder": "serena_shorts",
        "message": " finds one of {BOT_NAME}'s trap and becomes transforms."
    },



]


