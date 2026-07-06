# Theme registry for the clinic app.

# A theme is a set of colour tokens plus a light/dark mode flag. Every colour in
# the GUI comes from the active theme, so switching themes recolours the whole
# application at once.

# To add a new theme: copy any entry in THEMES, rename it, and change the values.
# It must have the same keys as the others (bg, card, field, fg, muted, accent,
# danger, error, mode, and a roles dict). Nothing else needs to change --
# it will appear in the theme picker automatically.

THEMES = {
    "Slate Dark": {
        "mode": "dark",
        "bg": "#15171c",
        "card": "#1f232b",
        "field": "#2a2f39",
        "fg": "#e6e6e6",
        "muted": "#8a909c",
        "accent": "#5B9BF7",
        "danger": "#B4504F",
        "error": "#E05555",
    },

    "Clinical Light": {
        "mode": "light",
        "bg": "#eef1f5",       # soft grey-blue, so white cards stand out
        "card": "#ffffff",     # white panels
        "field": "#e8ecf2",    # subtly inset input fields
        "fg": "#1f2933",        # dark slate text (softer than pure black)
        "muted": "#6b7280",    # grey secondary text
        "accent": "#2563EB",   # confident medical blue
        "danger": "#D64545",
        "error": "#C0392B",
    },

    "Calm Teal": {
        "mode": "dark",
        "bg": "#12201e",
        "card": "#172a27",
        "field": "#1f3833",
        "fg": "#dfe8e5",
        "muted": "#7d938d",
        "accent": "#2DBFA8",
        "danger": "#C0605C",
        "error": "#E07A6E",
    },

    "Soft Modern": {
        "mode": "light",
        "bg": "#f5f6fa",
        "card": "#ffffff",
        "field": "#eef0f6",
        "fg": "#2d2f3a",
        "muted": "#8b8fa3",
        "accent": "#7C6FF0",   # soft indigo
        "danger": "#E06C75",
        "error": "#D1495B",
    },
}

DEFAULT_THEME = "Soft Modern"
_active = DEFAULT_THEME

#All theme names, for the picker.
def names(): 
    return list(THEMES.keys())

#The currently active theme (a dict of tokens).
def get():    
    return THEMES[_active]


def current_name():
    return _active

#Switch the active theme. Returns the new active theme.
def apply(name):
    global _active
    if name in THEMES:
        _active = name
    return get()
