# Pixel Launcher

A Nexon/MapleStory-style game launcher built with **PyQt5** and
**[PyQt-Fluent-Widgets](https://pyqt-fluent-widgets.readthedocs.io/en/latest/)**,
skinned with GuttyKreum's *Urban Accessories* pixel art.

![Play tab](docs/screenshot-play.png)

## What it does

- **Animated pixel hero banner** - the artwork GIFs are drawn with
  nearest-neighbour scaling, so they stay crisp instead of turning to mush.
  Each game crops the shared art at a different height, so every hero looks
  distinct.
- **Game rail** with live install state (ready / update / not installed /
  downloading / maintenance) and a disk-usage footer.
- **One button that knows what it means** - INSTALL, UPDATE or START GAME,
  tinted with the selected game's accent colour.
- **Working patcher** with staged progress, live speed and ETA, pause,
  resume and cancel. It honours the bandwidth limit from settings.
- **Notice board** with category tabs, pinned posts and readable articles.
- **Server status** with ping and load meters, and a spotlight card.
- **Library grid** with search.
- **Settings** built from Fluent setting cards: install folder, resolution,
  display mode, region, auto-update, tray behaviour, bandwidth cap, theme
  and accent colour.
- Frameless window, custom title bar, account menu, login dialog and a
  system tray icon.

| Library | Downloading | Settings |
| --- | --- | --- |
| ![Library](docs/screenshot-library.png) | ![Downloading](docs/screenshot-download.png) | ![Settings](docs/screenshot-settings.png) |

## Running it

```bash
pip install -r requirements.txt
python main.py
```

Python 3.8+ and a desktop session are required. On a headless box you can
still boot it with `QT_QPA_PLATFORM=offscreen`.

## Tests

```bash
python -m unittest discover -s tests
```

The suite builds the real window offscreen and drives the install → launch
→ exit cycle, so it catches wiring breaks in the state machine.

## Layout

```
main.py                 entry point
launcher/
  core/
    catalog.py          Game model, news feed, install state
    config.py           persisted settings (QConfig)
    patcher.py          simulated downloader: progress, speed, ETA
    pixel.py            nearest-neighbour scaling and crisp text shadows
    paths.py            asset locations
    theme.py            palette taken from the tileset
  ui/
    main_window.py      window, navigation, the play-button state machine
    home_page.py        hero + notice board + side column
    library_page.py     searchable card grid
    settings_page.py    Fluent setting cards
    dialogs.py          sign-in and article dialogs
    style.py            chrome stylesheet
    widgets/            hero banner, game rail, action bar, play button, ...
assets/                 pixel art (banners, tiles)
data/                   games.json, news.json, servers.json
tests/
```

## Wiring it to a real game

Two seams are deliberately fake, and both are small:

- `launcher/core/patcher.py` simulates the download. It already emits the
  signals a real client needs (`progress`, `stats`, `stage`, `finished`,
  `cancelled`) - replace `_duration_for` and `_tick` with actual byte
  counts and nothing else has to change.
- `MainWindow._launch()` fakes the game process with a timer. Swap it for a
  `QProcess` and connect `finished` to `_on_game_exit`.

Settings are stored in `~/.pixel-launcher/`. Point `PIXEL_LAUNCHER_HOME`
somewhere else for a portable install.

## Credits

Artwork is the **Urban Accessories v2** pack by
**[GuttyKreum](https://gutty-kreum.itch.io/)**. The pack's original credits
file ships alongside it at `assets/GuttyKreum_Readme.txt`. Check the pack's
own licence before shipping anything built on it.

Widgets come from [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
by zhiyiYo.
