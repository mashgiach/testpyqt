"""Window chrome styling that sits on top of the Fluent dark theme."""
from ..core import theme as c

STYLE_SHEET = f"""
MainWindow {{
    background-color: {c.BASE};
}}
LauncherTitleBar {{
    background-color: {c.INK};
}}
#gameRail {{
    background-color: {c.INK};
    border-right: 1px solid {c.LINE};
}}
#homePage, #homeHolder, #libraryPage, #settingsPage {{
    background-color: {c.BASE};
}}
#statusBar {{
    background-color: {c.INK};
    border-top: 1px solid {c.LINE};
}}
"""
