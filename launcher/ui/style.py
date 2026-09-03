"""Window chrome styling that sits on top of the Fluent dark theme."""
from ..core import theme as c

STYLE_SHEET = f"""
MainWindow {{
    background-color: {c.BASE_LOW};
}}
LauncherTitleBar {{
    background-color: {c.INK};
}}
#homePage, #homeHolder, #libraryPage, #settingsPage {{
    background-color: {c.BASE_LOW};
}}
#statusBar {{
    background-color: {c.INK};
    border-top: 1px solid {c.LINE};
}}
"""
