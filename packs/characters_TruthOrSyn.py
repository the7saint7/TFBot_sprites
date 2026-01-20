import os

# Bot name from environment, defaults to "Syn" for backwards compatibility
BOT_NAME = os.getenv("TFBOT_NAME", "Syn").strip() or "Syn"

# Helper function to replace bot name placeholder in messages
def _format_message(message: str) -> str:
    """Replace {BOT_NAME} placeholder with actual bot name."""
    return message.replace("{BOT_NAME}", BOT_NAME)

TF_CHARACTERS = [

    ##Truth or Syn

    {
        "name": "Ayato (Truth or Syn)",
        "folder": "ayato"
    },

    {
        "name": "Catherine (Truth or Syn)",
        "folder": "catherine"
    },

    {
        "name": "Cecile (Truth or Syn)",
        "folder": "cecile"
    },

    {
        "name": "Chisa (Truth or Syn)",
        "folder": "chisa"
    },

    {
        "name": "Ciriel (Truth or Syn)",
        "folder": "ciriel"
    },

    {
        "name": "Cloe (Truth or Syn)",
        "folder": "cloe"
    },

    {
        "name": "Corina (Truth or Syn)",
        "folder": "corina"
    },

    {
        "name": "Faye (Truth or Syn)",
        "folder": "faye"
    },

    {
        "name": "Ghost (Truth or Syn)",
        "folder": "ghost"
    },

    {
        "name": "Gu (Truth or Syn)",
        "folder": "gu"
    },

    {
        "name": "Haru (Truth or Syn)",
        "folder": "haru"
    },

    {
        "name": "Hasumi (Truth or Syn)",
        "folder": "hasumi"
    },

    {
        "name": "Inori (Truth or Syn)",
        "folder": "inori"
    },

    {
        "name": "Jenna (Truth or Syn)",
        "folder": "jenna"
    },

    {
        "name": "Johngb Girly (Truth or Syn)",
        "folder": "johnGB_Girly"
    },

    {
        "name": "Johngb3",
        "gender": "female",
        "genderswap": None,
        "age": "teen",
        "type": "human",
        "avatar_path": "avatars/johngb3.png",
        "folder": "johnGB3",
        "message": " stepped on a trap left by {BOT_NAME} and were transported in an alternate universe where they became a different version of John."
    },
    
    {
        "name": "Johnshrink (Truth or Syn)",
        "folder": "johnShrink"
    },

    {
        "name": "Julie (Truth or Syn)",
        "folder": "julie"
    },

    {
        "name": "Katrina (Truth or Syn)",
        "folder": "katrinaS"
    },

    {
        "name": "Kirika (Truth or Syn)",
        "folder": "kirika"
    },

    {
        "name": "Kokoro (Truth or Syn)",
        "folder": "kokoro"
    },

    {
        "name": "Kotaru (Truth or Syn)",
        "folder": "kotaru"
    },

    {
        "name": "Kyoko Hano (Truth or Syn)",
        "folder": "kyokoAP"
    },

    {
        "name": "Kyouka (Truth or Syn)",
        "folder": "kyouka"
    },

    {
        "name": "Line (Truth or Syn)",
        "folder": "line"
    },

    {
        "name": "Maria Full (Truth or Syn)",
        "folder": "maria_full"
    },

    {
        "name": "Mark (Truth or Syn)",
        "folder": "mark"
    },

    {
        "name": "Masika (Truth or Syn)",
        "folder": "masika"
    },

    {
        "name": "Meika (Truth or Syn)",
        "folder": "meika"
    },

    {
        "name": "Melisa (Truth or Syn)",
        "folder": "melisa"
    },

    {
        "name": "Miharu (Truth or Syn)",
        "folder": "miharu"
    },

    {
        "name": "Miki (Truth or Syn)",
        "folder": "miki"
    },

    {
        "name": "Miria (Truth or Syn)",
        "folder": "miria"
    },

    {
        "name": "Miriel (Truth or Syn)",
        "folder": "miriel"
    },

    {
        "name": "Mirra (Truth or Syn)",
        "folder": "mirra"
    },

    {
        "name": "Misao (Truth or Syn)",
        "folder": "misao"
    },

    {
        "name": "Mitsuki (Truth or Syn)",
        "folder": "mitsuki"
    },

    {
        "name": "Nanao (Truth or Syn)",
        "folder": "nanao"
    },

    {
        "name": "Narume (Truth or Syn)",
        "folder": "Narume"
    },

    {
        "name": "Rachel (Truth or Syn)",
        "folder": "rachelAR"
    },

    {
        "name": "Reika (Truth or Syn)",
        "folder": "reika1"
    },

    {
        "name": "Riru (Truth or Syn)",
        "folder": "riru"
    },

    {
        "name": "Risa (Truth or Syn)",
        "folder": "risa"
    },

    {
        "name": "Ruri (Truth or Syn)",
        "folder": "ruri"
    },

    {
        "name": "Sally (Truth or Syn)",
        "folder": "sally"
    },

    {
        "name": "Sana (Truth or Syn)",
        "folder": "sana"
    },

    {
        "name": "Mom (Truth or Syn)",
        "folder": "sandra1"
    },

    {
        "name": "Saya (Truth or Syn)",
        "folder": "saya"
    },

    {
        "name": "Sayaka (Truth or Syn)",
        "folder": "sayakaAR"
    },

    {
        "name": "Scott (Truth or Syn)",
        "folder": "scott"
    },

    {
        "name": "Seira (Truth or Syn)",
        "folder": "seira"
    },

    {
        "name": "Shizume (Truth or Syn)",
        "folder": "shizume"
    },

    {
        "name": "Souko (Truth or Syn)",
        "folder": "souko"
    },

    {
        "name": "Line (Truth or Syn)",
        "folder": "spica"
    },

    {
        "name": "Suzune (Truth or Syn)",
        "folder": "suzune"
    },

    {
        "name": "Tori (Truth or Syn)",
        "folder": "tori"
    },

    {
        "name": "Tsubasa (Truth or Syn)",
        "folder": "tsubasa"
    },

    {
        "name": "Uya2 (Truth or Syn)",
        "folder": "uya"
    },


    {
        "name": "Yui (Truth or Syn)",
        "folder": "yui"
    },

    {
        "name": "Yuisuccubus (Truth or Syn)",
        "folder": "yuiSuccubus"
    },

    {
        "name": "Yura (Truth or Syn)",
        "folder": "yura"
    },

    {
        "name": "Yuria (Truth or Syn)",
        "folder": "yuria"
    },

    {
        "name": "Yuuna Yamashita (Truth or Syn)",
        "folder": "yuuna"
    },


]
