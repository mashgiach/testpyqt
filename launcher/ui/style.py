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
#homePage, #libraryPage, #settingsPage {{
    background-color: {c.BASE};
}}
#newsFeed {{
    background-color: {c.BASE};
    border-right: 1px solid {c.LINE};
}}
#sidePanel {{
    background-color: {c.SURFACE};
}}
#newsRow {{
    border-radius: 6px;
}}
#newsRow:hover {{
    background-color: {c.SURFACE_HI};
}}
#actionBar {{
    background-color: {c.INK};
    border-top: 1px solid {c.LINE};
}}
"""
