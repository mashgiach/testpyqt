"""Game catalog, news feed and the per-game install state."""
import json
from dataclasses import dataclass, field
from typing import List, Optional

from .config import load_library_state, save_library_state
from .paths import DATA


@dataclass
class Game:
    id: str
    title: str
    subtitle: str
    genre: str
    version: str
    size_gb: float
    patch_gb: float
    icon: str
    banner: str
    banner_focus: float
    accent: str
    state: str
    players: int
    blurb: str
    tags: List[str] = field(default_factory=list)
    installed_version: Optional[str] = None

    @property
    def installed(self) -> bool:
        return self.installed_version is not None

    @property
    def needs_patch(self) -> bool:
        return self.installed and self.installed_version != self.version

    @property
    def download_gb(self) -> float:
        return self.patch_gb if self.needs_patch else self.size_gb

    @property
    def action_label(self) -> str:
        return {"install": "INSTALL", "update": "UPDATE", "maintenance": "UNAVAILABLE"}.get(
            self.state, "START GAME")

    def refresh_state(self):
        if self.state == "maintenance":
            return
        if not self.installed:
            self.state = "install"
        elif self.needs_patch:
            self.state = "update"
        else:
            self.state = "ready"


class Catalog:
    def __init__(self):
        raw = json.loads((DATA / "games.json").read_text())
        self.news = json.loads((DATA / "news.json").read_text())
        self.servers = json.loads((DATA / "servers.json").read_text())

        state = load_library_state()
        self.games: List[Game] = []
        for entry in raw:
            entry = dict(entry)
            saved = state.get(entry["id"])
            if saved is not None:
                entry["installed_version"] = saved.get("installed_version")
            game = Game(**entry)
            game.refresh_state()
            self.games.append(game)

    def get(self, game_id: str) -> Game:
        return next(g for g in self.games if g.id == game_id)

    def news_for(self, game_id: str) -> List[dict]:
        items = sorted(self.news.get(game_id, []), key=lambda n: n["date"], reverse=True)
        return sorted(items, key=lambda n: not n.get("pinned"))

    def persist(self):
        save_library_state({
            g.id: {"installed_version": g.installed_version} for g in self.games
        })
