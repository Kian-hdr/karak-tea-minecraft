#!/usr/bin/env python3
"""Build the private five-shop showcase through its own Horizon control socket.

Start a fresh isolated world, then pass --apply and explicit --ctl/--socket.
This script never starts/stops a game or changes the launcher's selected instance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

from build import ROOT, THEMES

WORLD = "Karak_Tea_Showcase"
FLOOR_Y = 64
SPAWN = (6.5, 65, -5.5)
PLOTS = [
    {"style": style, "x": -40 + i * 20, "z": 12,
     "width": THEMES[style]["width"], "depth": THEMES[style]["depth"]}
    for i, style in enumerate(THEMES)
]


def wall_sign(x: int, y: int, z: int, lines: list[str]) -> list[str]:
    messages = json.dumps(lines, separators=(",", ":"))
    return [f"fill {x} 65 {z + 1} {x} {y} {z + 1} smooth_quartz",
            f"setblock {x} {y} {z} dark_oak_wall_sign[facing=north]"
            f"{{is_waxed:1b,front_text:{{messages:{messages},color:\"black\",has_glowing_text:0b}}}}"]


def plan() -> list[str]:
    commands = ["gamemode creative", "difficulty peaceful", "weather clear",
                "time set 6000", "gamerule minecraft:advance_time false",
                "gamerule minecraft:advance_weather false",
                "gamerule minecraft:spawn_mobs false",
                "gamerule minecraft:keep_inventory true",
                "gamerule minecraft:respawn_radius 0", "effect clear @s"]
    # Small batches stay below vanilla's fill volume limit.
    for x in range(-46, 61, 18):
        end = min(x + 17, 60)
        commands += [f"fill {x} 61 -14 {end} 63 40 dirt",
                     f"fill {x} 64 -14 {end} 64 40 grass_block",
                     f"fill {x} 65 -14 {end} 78 40 air"]
    commands += ["fill -45 64 -1 59 64 7 stone_bricks",
                 "fill -45 64 -2 59 64 -2 polished_andesite",
                 "fill -45 64 8 59 64 8 polished_andesite",
                 "fill 1 64 -10 12 64 7 stone_bricks"]
    ground = {"plains": "grass_block", "desert": "sand",
              "savanna": "red_sand", "taiga": "podzol", "snowy": "snow_block"}
    for p in PLOTS:
        x, z, width, style = p["x"], p["z"], p["width"], p["style"]
        mid = x + width // 2
        commands += [f"fill {x - 1} 64 9 {x + 16} 64 28 {ground[style]}",
                     f"place template karak_house:village/karak_house_{style} {x} 64 {z}",
                     f"setblock {mid} 65 {z} air",
                     f"fill {mid - 1} 64 7 {mid + 2} 64 {z} {THEMES[style]['path']}",
                     f"tag @e[type=villager,tag=karak_seller,x={mid},y=65,z=22,distance=..8,limit=1,sort=nearest] add showcase_{style}"]
        commands += wall_sign(x, 66, 9, [style.upper(), "KARAK HOUSE", "1 emerald / cup", "Walk inside"])
    for x in [-43, -23, -3, 17, 37, 57]:
        commands += [f"setblock {x} 65 0 stone_brick_wall",
                     f"setblock {x} 66 0 lantern"]
    commands += ["setblock 3 65 -7 chest[facing=north]",
                 "setblock 9 65 -7 chest[facing=north]"]
    commands += wall_sign(3, 67, -7, ["SHOWCASE SUPPLY", "Emeralds", "Buy tea in shops", "1 emerald = 1 cup"])
    commands += wall_sign(9, 67, -7, ["SHOWCASE SUPPLY", "Milk and bread", "Milk clears powers", "Take what you need"])
    commands += wall_sign(6, 67, -10, ["KARAK TEA", "Five-house showcase", "Survival / peaceful", "Walk, trade, drink"])
    commands += wall_sign(6, 66, -10, ["Seven powers: 5 min", "Drink again: refresh", "Milk clears effects", "Day/weather frozen"])
    commands += ["setworldspawn 6 65 -5 0 0", "spawnpoint @s 6 65 -5 0 0",
                 "tp @s 6.5 65 -5.5 0 0", "gamemode survival"]
    return commands


def verify_pack(archive: Path) -> str:
    with zipfile.ZipFile(archive) as z:
        for p in (ROOT / "pack").rglob("*"):
            if p.is_file():
                rel = p.relative_to(ROOT / "pack").as_posix()
                if z.read(rel) != p.read_bytes():
                    raise RuntimeError(f"Archive is stale: {rel}; await root's integration rebuild")
    if any(p["depth"] != 13 for p in PLOTS):
        raise RuntimeError("Await integrated depth-13 structures")
    return hashlib.sha256(archive.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--ctl", type=Path)
    parser.add_argument("--socket")
    parser.add_argument("--archive", type=Path, default=ROOT / "dist/Karak_Tea_0.1.0.hmod")
    parser.add_argument("--expected-sha256", help="Use an explicitly pinned immutable integration snapshot")
    parser.add_argument("--evidence", type=Path, default=ROOT / "evidence/private/showcase")
    args = parser.parse_args()
    commands = plan()
    if not args.apply:
        print(json.dumps({"world": WORLD, "spawn": SPAWN, "plots": PLOTS, "commands": commands}, indent=2))
        return
    if not args.ctl or not args.socket or "showcase" not in args.socket:
        parser.error("--apply requires --ctl and a dedicated socket containing 'showcase'")
    if args.expected_sha256:
        digest = hashlib.sha256(args.archive.read_bytes()).hexdigest()
        if digest != args.expected_sha256:
            raise RuntimeError("Immutable archive hash differs from the approved integration snapshot")
    else:
        digest = verify_pack(args.archive)
    args.evidence.mkdir(parents=True, exist_ok=True)

    def ctl(*words: object) -> dict:
        result = subprocess.run([str(args.ctl), "--socket", args.socket, *map(str, words)],
                                capture_output=True, text=True, timeout=90, check=False)
        try:
            value = json.loads(result.stdout)
        except ValueError as exc:
            raise RuntimeError(result.stderr or result.stdout) from exc
        if result.returncode or "error" in value:
            raise RuntimeError(value)
        return value

    initial = ctl("state")
    if WORLD not in json.dumps(initial):
        raise RuntimeError("Refusing to alter a world other than Karak_Tea_Showcase")
    receipt = {"world": WORLD, "archive_sha256": digest, "spawn": SPAWN, "plots": PLOTS,
               "initial": initial, "commands": [], "checks": {}}
    try:
        ctl("command", "tp @s 6.5 85 8")
        ctl("render-distance", 5)
        ctl("wait-ready", 60)
        for command in commands:
            result = ctl("command", command)
            receipt["commands"].append({"command": command, "result": result})
            output = json.dumps(result).lower()
            if any(t in output for t in ["unknown or incomplete", "incorrect argument", "not loaded", "too many blocks", "failed to"]):
                raise RuntimeError({"command": command, "result": result})
        for _ in range(20):
            ctl("container", 3, 65, -7, "emerald", 64)
        for _ in range(12):
            ctl("container", 9, 65, -7, "milk_bucket", 1)
        ctl("container", 9, 65, -7, "bread", 64)
        for p in PLOTS:
            mid = p["x"] + p["width"] // 2
            receipt["checks"][p["style"]] = {
                "door": ctl("block", mid, 65, 17),
                "lectern": ctl("block", mid, 65, 21),
                "entry_floor": ctl("block", mid, 64, 12)}
        receipt["checks"]["entities"] = ctl("entities", 100, "villager")
        receipt["checks"]["emeralds"] = ctl("container", 3, 65, -7)
        receipt["checks"]["milk"] = ctl("container", 9, 65, -7)
        receipt["final"] = ctl("state")
        receipt["save"] = ctl("save")
    finally:
        (args.evidence / "Build_Receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
