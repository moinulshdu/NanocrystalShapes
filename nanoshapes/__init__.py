"""Nanocrystal Shapes - translucent 3D figures of common nanocrystal shapes."""
__version__ = "2.2"
__date__ = "November 2026"
__author__ = "moinulshdu"
__email__ = "moinulshdu@gmail.com"

# Who made what. Shown in Help > About and in the README.
__concept__ = (
    "The idea, features and design of Nanocrystal Shapes are by moinulshdu, "
    "who directed its development step by step, tested every version and "
    "decided what the app should do."
)
__ai_assistance__ = (
    "The code and documentation were written with the help of Claude, "
    "an AI assistant made by Anthropic (model: Claude Opus 5.5, "
    "\"claude-opus-5-5\"), following moinulshdu's instructions, "
    "November 10-11, 2026."
)
__license_note__ = (
    "Nanocrystal Shapes is free for anyone to use, share and build upon. "
    "If it helps your work, a kind acknowledgment of the developer would be warmly "
    "appreciated. Questions, ideas and feedback are always welcome by email."
)


def acknowledgment():
    """Ready-made line for papers, posters and slides."""
    return ("Figures made with Nanocrystal Shapes %s by %s (%s)."
            % (__version__, __author__, __email__))
