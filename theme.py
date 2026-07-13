# Theme registry for the clinic app.

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
        "bg": "#eef1f5",       
        "card": "#ffffff",     
        "field": "#e8ecf2",    
        "fg": "#1f2933",        
        "muted": "#6b7280",    
        "accent": "#2563EB",   
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
        "accent": "#7B79E0",   
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
