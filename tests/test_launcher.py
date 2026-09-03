"""Smoke tests: build the window offscreen and drive the play-button states.

Run with:  QT_QPA_PLATFORM=offscreen python -m unittest discover tests
"""
import atexit
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Write settings somewhere disposable so a previous run cannot skew this one.
_TMP = tempfile.mkdtemp(prefix="pixel-launcher-test-")
os.environ["PIXEL_LAUNCHER_HOME"] = _TMP
atexit.register(shutil.rmtree, _TMP, True)

from PyQt5.QtWidgets import QApplication  # noqa: E402

from launcher.core.catalog import Catalog  # noqa: E402
from launcher.core.patcher import Patcher  # noqa: E402
from launcher.ui.main_window import MainWindow  # noqa: E402
from launcher.ui.widgets.hero import ACTION_TEXT  # noqa: E402

app = QApplication.instance() or QApplication(sys.argv)


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog()

    def test_every_game_has_its_art(self):
        from launcher.core.paths import TILES, BANNERS
        for game in self.catalog.games:
            self.assertTrue((TILES / f"{game.icon}.png").exists(), game.icon)
            self.assertTrue((BANNERS / game.banner).exists(), game.banner)

    def test_state_follows_installed_version(self):
        game = self.catalog.get("kanagawa-nights")
        game.installed_version = None
        game.refresh_state()
        self.assertEqual(game.state, "install")

        game.installed_version = "4.1.7"
        game.refresh_state()
        self.assertEqual(game.state, "update")
        self.assertEqual(game.download_gb, game.patch_gb)

        game.installed_version = game.version
        game.refresh_state()
        self.assertEqual(game.state, "ready")
        self.assertEqual(game.action_label, "START GAME")

    def test_maintenance_is_never_overwritten(self):
        game = self.catalog.get("kaiju-frog")
        game.refresh_state()
        self.assertEqual(game.state, "maintenance")

    def test_pinned_news_comes_first(self):
        items = self.catalog.news_for("kanagawa-nights")
        self.assertTrue(items[0]["pinned"])
        self.assertGreater(len(items), 1)


class PatcherTest(unittest.TestCase):
    def test_download_runs_to_completion(self):
        patcher = Patcher()
        seen = []
        patcher.finished.connect(seen.append)
        patcher.start("deer-trail", 0.4)

        for _ in range(4000):
            if seen:
                break
            patcher._tick()
        self.assertEqual(seen, ["deer-trail"])
        self.assertFalse(patcher.active)

    def test_pause_freezes_progress(self):
        patcher = Patcher()
        patcher.start("deer-trail", 4.0)
        patcher._tick()
        before = patcher.done_gb
        patcher.pause()
        for _ in range(10):
            patcher._tick()
        self.assertEqual(patcher.done_gb, before)

        patcher.resume()
        patcher._tick()
        self.assertGreater(patcher.done_gb, before)

    def test_cancel_reports_the_game(self):
        patcher = Patcher()
        cancelled = []
        patcher.cancelled.connect(cancelled.append)
        patcher.start("drone-runner", 2.0)
        patcher.cancel()
        self.assertEqual(cancelled, ["drone-runner"])
        self.assertEqual(patcher.done_gb, 0.0)


class WindowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.window = MainWindow()
        cls.window.resize(1180, 760)

    def test_selecting_a_game_updates_the_page(self):
        self.window.select_game("shibuya-drift")
        self.assertEqual(self.window.current.id, "shibuya-drift")
        self.assertEqual(self.window.home.hero._game.id, "shibuya-drift")
        self.assertEqual(self.window.home.hero.title.text(), "Shibuya Drift")
        # Earlier tests may have reset the library, so derive the expected
        # label from the game's own state rather than hard-coding one.
        self.assertEqual(self.window.home.hero.play.text(),
                         ACTION_TEXT[self.window.current.state])
        self.assertTrue(self.window.home.grid._cards)

    def test_install_then_launch(self):
        window = self.window
        window.select_game("torii-tactics")
        game = window.current
        self.assertEqual(game.state, "install")

        self.assertEqual(window.home.hero.play.text(), "DOWNLOAD")

        window._on_play()
        self.assertEqual(game.state, "busy")
        self.assertFalse(window.status_bar.bar.isHidden())
        self.assertFalse(window.home.hero.play.isEnabled())

        while window.patcher.active:
            window.patcher._tick()
        self.assertEqual(game.state, "ready")
        self.assertEqual(game.installed_version, game.version)
        self.assertEqual(window.home.hero.play.text(), "START GAME")

        window._on_play()
        self.assertEqual(game.state, "running")
        window._on_game_exit(game)
        self.assertEqual(game.state, "ready")

    def test_maintenance_button_is_dead(self):
        self.window.select_game("kaiju-frog")
        self.assertFalse(self.window.home.hero.play.isEnabled())
        self.assertEqual(self.window.home.hero.play.text(), "UNAVAILABLE")
        self.window._on_play()
        self.assertNotEqual(self.window.patcher.game_id, "kaiju-frog")

    def test_reset_library_marks_everything_uninstalled(self):
        self.window._reset_library()
        self.assertTrue(all(not g.installed for g in self.window.catalog.games))

    def test_news_grid_filters_by_category(self):
        self.window.select_game("kanagawa-nights")
        grid = self.window.home.grid
        self.assertIn("Event", grid.categories())

        grid.set_filter("Event")
        self.assertTrue(all(c.item["category"] == "Event" for c in grid._cards))

        grid.set_filter("All")
        self.assertEqual(len(grid._cards), len(grid._items))

    def test_pages_switch(self):
        for key, page in (("library", self.window.library),
                          ("settings", self.window.settings),
                          ("home", self.window.home)):
            self.window._go(key)
            self.assertIs(self.window.stack.currentWidget(), page)


if __name__ == "__main__":
    unittest.main()
