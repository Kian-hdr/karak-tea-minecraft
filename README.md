# Karak Tea for Minecraft Horizon

A personal Minecraft content mod for the Rust-based Horizon client. Discover modern Karak Houses in villages and buy superhero tea.

**Development build. Not yet qualified for public download.**

The repository remains private until gameplay acceptance tests pass.

## Gameplay

- Maximum one Karak House per village, with five biome-specific designs.
- One emerald buys exactly one Karak Tea. No copper or random prices.
- Each seller has an independent 10% daily chance of offering one free cup.
- Tea grants seven superhero effects for five minutes.

## Compatibility

Targets Horizon nightly-2026-11-05-66f3981. This is not a Fabric, Forge, NeoForge, or Bedrock mod. Requires the player’s own Minecraft Java Edition through Horizon.

## Development

Source pack is in `pack/`. Generator and acceptance tests will be documented as implementation progresses.

## Attribution

Inspired by Dubai karak tea shops. Independent fan project, not affiliated with Karak House, Mojang, Microsoft, or Horizon. Minecraft textures are referenced from the player’s installation and are not redistributed.

## Design review

Village integration and public release are held for the owner’s review. The images below are isolated design previews rendered in Horizon, not evidence of completed village-generation or gameplay acceptance.

### Plains

![Plains exterior](docs/screenshots/plains_exterior.webp)

### Desert

![Desert exterior](docs/screenshots/desert_exterior.webp)

### Savanna

![Savanna exterior](docs/screenshots/savanna_exterior.webp)

### Taiga

![Taiga exterior](docs/screenshots/taiga_exterior.webp)

### Snowy

![Snowy exterior](docs/screenshots/snowy_exterior.webp)

## Build the pack

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python scripts/build.py
.venv/bin/python -m unittest discover -s tests -v
```

Build output: `dist/Karak_Tea_0.1.0.hmod`. Development-only until acceptance testing is complete.
