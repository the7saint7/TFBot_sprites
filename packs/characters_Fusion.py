import os

# Bot name from environment, defaults to "Syn" for backwards compatibility
BOT_NAME = os.getenv("TFBOT_NAME", "Syn").strip() or "Syn"

# Helper function to replace bot name placeholder in messages
def _format_message(message: str) -> str:
    """Replace {BOT_NAME} placeholder with actual bot name."""
    return message.replace("{BOT_NAME}", BOT_NAME)

TF_CHARACTERS = [

    ##ST - Scenarios - Fusion

    {
        "name": "Allene (Fusion)",
        "avatar_path": "avatars/irene_allison.png",
        "folder": "allene",
        "message": " saw Allison and Irene high-five as they stepped on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "Anuja/Michelle (Fusion)",
        "avatar_path": "avatars/anuja_michelle.png",
        "folder": "anuja_michelle",
        "message": " dropped their notebook as John and Zoey crossed their path and accidentally activated on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "Eric/Brad (Fusion)",
        "avatar_path": "avatars/eric_brad.png",
        "folder": "eric_brad",
        "message": " dropped their notebook as John and Zoey crossed their path and accidentally activated on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "Joey (Fusion)",
        "avatar_path": "avatars/joey.png",
        "folder": "joey",
        "message": " dropped their notebook as John and Zoey crossed their path and accidentally activated on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "John/Kiyoshi (Fusion)",
        "avatar_path": "avatars/johnKiyoshi.png",
        "folder": "johnKiyoshi",
        "message": " dropped their notebook as John and Zoey crossed their path and accidentally activated on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "Jori (Fusion)",
        "avatar_path": "avatars/jori.png",
        "folder": "jori",
        "message": " picked up a strange ring. After putting it on, their bodies began to change. It was another prank by {BOT_NAME}. Quickly they become a sort of fusion of John and Tori Vegas."
    },

    {
        "name": "Jori2 (Fusion)",
        "avatar_path": "avatars/jori2.png",
        "folder": "jori2",
        "message": " accidentally sat on a magic trap! Soon, their bodies began to change. their bodies developed into the lustful form of Tori Vegas, but to everyone's shock, they have John's head!"
    },

    {
        "name": "Katrina/Kyoko (Fusion)",
        "avatar_path": "avatars/katrina_kyoko.png",
        "folder": "katrina_kyoko",
        "message": " dropped their notebook as John and Zoey crossed their path and accidentally activated on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "Riley/Gabriel (Fusion)",
        "avatar_path": "avatars/riley_gabriel.png",
        "folder": "riley_gabriel",
        "message": " dropped their notebook as John and Zoey crossed their path and accidentally activated on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "Riyaka (Fusion)",
        "avatar_path": "avatars/riyaka.png",
        "folder": "riyaka",
        "message": " intervened in an argument between Sayaka and Rita and accidentally activated on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "Yuvia (yuvia) (Fusion)",
        "avatar_path": "avatars/yuvia.png",
        "folder": "yuvia",
        "message": " dropped their notebook as John and Zoey crossed their path and accidentally activated on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },

    {
        "name": "Zoel (Fusion)",
        "avatar_path": "avatars/zoel.png",
        "folder": "zoel",
        "message": " saw Mel and Zoey high-five as they stepped on one of {BOT_NAME}'s magical trap. Soon their 3 bodies merge with them in full control of the resulting amalgam!"
    },


]


