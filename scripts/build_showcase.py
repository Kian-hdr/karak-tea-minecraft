#!/usr/bin/env python3
"""Build the private five-shop showcase through its own Horizon control socket.

Start a fresh isolated world, then pass --apply and explicit --ctl/--socket.
This script never starts/stops a game or changes the launcher's selected instance.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import struct
import subprocess
import uuid
import zipfile
import zlib
from pathlib import Path

import nbtlib

from build import ROOT, THEMES, VERSION

WORLD = "Karak_Tea_Showcase"
FLOOR_Y = 64
SPAWN = (6.5, 65, -5.5)
def plots_from_structures(archive: Path | None = None) -> list[dict]:
    plots = []
    for i, style in enumerate(THEMES):
        relative = f"data/karak_house/structure/village/karak_house_{style}.nbt"
        if archive:
            with zipfile.ZipFile(archive) as z:
                structure = nbtlib.File.parse(io.BytesIO(gzip.decompress(z.read(relative))))
        else:
            structure = nbtlib.load(ROOT / "pack" / relative)
        palette = structure["palette"]
        jigs = [b for b in structure["blocks"] if str(palette[b["state"]]["id"]) == "minecraft:jigsaw"]
        if len(jigs) != 1:
            raise ValueError(f"{style}: expected exactly one entrance connector")
        connector = list(map(int, jigs[0]["pos"]))
        doors = [list(map(int, b["pos"])) for b in structure["blocks"]
                 if str(palette[b["state"]]["id"]).endswith("_door")
                 and str(palette[b["state"]].get("properties", {}).get("half")) == "lower"]
        lecterns = [list(map(int, b["pos"])) for b in structure["blocks"]
                    if str(palette[b["state"]]["id"]) == "minecraft:lectern"]
        plots.append({"style": style, "x": -40 + i * 20, "z": 12,
                      "width": int(structure["size"][0]), "depth": int(structure["size"][2]),
                      "base_y": FLOOR_Y + 1 - connector[1], "connector": connector,
                      "final_state": str(jigs[0]["nbt"]["final_state"]),
                      "doors": doors, "lectern": lecterns[0]})
    return plots


PLOTS = plots_from_structures()


def wall_sign(x: int, y: int, z: int, lines: list[str]) -> list[str]:
    messages = json.dumps(lines, separators=(",", ":"))
    return [f"fill {x} 65 {z + 1} {x} {y} {z + 1} smooth_quartz",
            f"setblock {x} {y} {z} dark_oak_wall_sign[facing=north]"
            f"{{is_waxed:1b,front_text:{{messages:{messages},color:\"black\",has_glowing_text:0b}}}}"]


def plan(plots: list[dict] | None = None) -> list[str]:
    plots = PLOTS if plots is None else plots
    commands = ["gamemode creative", "difficulty peaceful", "weather clear",
                "time set 6000", "gamerule minecraft:advance_time false",
                "gamerule minecraft:advance_weather false",
                "gamerule minecraft:spawn_mobs false",
                "gamerule minecraft:keep_inventory true",
                "gamerule minecraft:respawn_radius 0", "effect clear @s",
                "kill @e[type=villager,tag=karak_seller,x=-46,y=61,z=-14,dx=106,dy=17,dz=54]",
                "kill @e[type=text_display,x=-46,y=61,z=-14,dx=106,dy=17,dz=54]",
                "kill @e[type=item,x=-46,y=61,z=-14,dx=106,dy=17,dz=54]"]
    # Small batches stay below vanilla's fill volume limit.
    for x in range(-46, 61, 18):
        end = min(x + 17, 60)
        commands += [f"fill {x} 61 -14 {end} 63 40 dirt",
                     f"fill {x} 64 -14 {end} 64 40 grass_block",
                     f"fill {x} 65 -14 {end} 86 40 air",
                     f"fill {x} 87 -14 {end} 110 40 air"]
    commands += ["fill -45 64 -1 59 64 7 stone_bricks",
                 "fill -45 64 -2 59 64 -2 polished_andesite",
                 "fill -45 64 8 59 64 8 polished_andesite",
                 "fill 1 64 -10 12 64 7 stone_bricks"]
    ground = {"plains": "grass_block", "desert": "sand",
              "savanna": "red_sand", "taiga": "podzol", "snowy": "snow_block"}
    for p in plots:
        x, z, width, style = p["x"], p["z"], p["width"], p["style"]
        mid = x + width // 2
        jx, jy, jz = p["connector"]
        commands += [f"fill {x - 1} 64 9 {x + 16} 64 28 {ground[style]}",
                     f"place template karak_house:village/karak_house_{style} {x} {p['base_y']} {z}",
                     f"setblock {x+jx} {p['base_y']+jy} {z+jz} {p['final_state']}",
                     f"fill {mid - 1} 64 7 {mid + 2} 64 {z} {THEMES[style]['path']}",
                     f"tag @e[type=villager,tag=karak_seller,x={mid},y={p['base_y']+1},z={z + p['depth'] - 3},distance=..8,limit=1,sort=nearest] add showcase_{style}"]
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
    for p in PLOTS:
        structure = nbtlib.load(ROOT / f"pack/data/karak_house/structure/village/karak_house_{p['style']}.nbt")
        size = list(map(int, structure["size"]))
        if (size[0], size[2]) != (p["width"], p["depth"]):
            raise RuntimeError(f"Structure dimensions differ from canonical theme: {p['style']}")
    return hashlib.sha256(archive.read_bytes()).hexdigest()


def sanitize_entity_region(raw: bytes, player_arrays: set[tuple[int, ...]], identities: set[str]) -> tuple[bytes, int, int]:
    """Compact chunks, anonymize gossip and omit transient construction debris."""
    header = bytearray(8192)
    header[4096:8192] = raw[4096:8192]
    body = bytearray()
    removed = 0
    removed_debris = 0

    def scrub(node: object) -> None:
        nonlocal removed
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "Gossips":
                    retained = []
                    for row in value:
                        target = row.get("Target")
                        private = ((isinstance(target, nbtlib.IntArray) and tuple(map(int, target)) in player_arrays)
                                   or (isinstance(target, nbtlib.String) and str(target) in identities))
                        if private:
                            removed += 1
                        else:
                            retained.append(row)
                    node[key] = nbtlib.List[nbtlib.Compound](retained)
                else:
                    scrub(value)
        elif isinstance(node, list):
            for value in node:
                scrub(value)

    for index in range(1024):
        offset = int.from_bytes(raw[index * 4:index * 4 + 3], "big") * 4096
        if not offset:
            continue
        size = int.from_bytes(raw[offset:offset + 4], "big")
        kind = raw[offset + 4]
        payload = raw[offset + 5:offset + 4 + size]
        if kind == 1:
            payload = gzip.decompress(payload)
        elif kind == 2:
            payload = zlib.decompress(payload)
        elif kind != 3:
            raise ValueError(f"Unsupported entity chunk compression: {kind}")
        tree = nbtlib.File.parse(io.BytesIO(payload))
        if "Entities" in tree:
            retained = [entity for entity in tree["Entities"]
                        if str(entity.get("id")) not in {"minecraft:item", "minecraft:experience_orb"}]
            removed_debris += len(tree["Entities"]) - len(retained)
            tree["Entities"] = nbtlib.List[nbtlib.Compound](retained)
        scrub(tree)
        stream = io.BytesIO()
        tree.write(stream)
        compressed = zlib.compress(stream.getvalue(), 9)
        chunk = (len(compressed) + 1).to_bytes(4, "big") + b"\x02" + compressed
        sectors = (len(chunk) + 4095) // 4096
        location = 2 + len(body) // 4096
        header[index * 4:index * 4 + 4] = location.to_bytes(3, "big") + bytes([sectors])
        body.extend(chunk)
        body.extend(bytes(sectors * 4096 - len(chunk)))
    return bytes(header + body), removed, removed_debris


def export_map(world: Path, destination: Path) -> dict:
    """Export map content without the builder's identity or personal game files."""
    if world.name != WORLD or not (world / "level.dat").is_file():
        raise ValueError("Expected the dedicated Karak_Tea_Showcase world")
    identities = {"KarakShowcase"}
    identities.update(p.stem for p in (world / "players").rglob("*.dat"))
    player_arrays = set()
    for identity in identities:
        try:
            player_arrays.add(struct.unpack(">iiii", uuid.UUID(identity).bytes))
        except ValueError:
            pass
    excluded = []
    removed_gossip = 0
    removed_debris = 0
    mod_file = world.parent.parent / "horizon-mods/Karak_Tea_0.1.0.hmod"
    mod_pin = ("Matching .hmod SHA-256: " + hashlib.sha256(mod_file.read_bytes()).hexdigest() + "\n"
               if mod_file.is_file() else "")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as output:
        for path in sorted(world.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(world)
            if (relative.parts[0] in {"players", "playerdata", "advancements", "stats", "logs"}
                    or path.name == "session.lock" or path.name.endswith(".dat_old")):
                excluded.append(relative.as_posix())
                continue
            data = path.read_bytes()
            if "entities" in relative.parts and path.suffix == ".mca":
                data, count, debris = sanitize_entity_region(data, player_arrays, identities)
                removed_gossip += count
                removed_debris += debris
            if relative.as_posix() in {"level.dat", "data/minecraft/scoreboard.dat"}:
                tree = nbtlib.load(path)
                if relative.as_posix() == "level.dat":
                    for key in ["singleplayer_uuid", "Player"]:
                        tree["Data"].pop(key, None)
                else:
                    scores = tree["data"].get("PlayerScores", [])
                    tree["data"]["PlayerScores"] = nbtlib.List[nbtlib.Compound](
                        row for row in scores if str(row.get("Name", "")) not in identities)
                raw = io.BytesIO()
                tree.write(raw)
                data = gzip.compress(raw.getvalue(), mtime=0)
            info = zipfile.ZipInfo(f"{WORLD}/{relative.as_posix()}", (2026, 11, 7, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(info, data)
        readme_info = zipfile.ZipInfo("README.txt", (2026, 11, 7, 0, 0, 0))
        readme_info.compress_type = zipfile.ZIP_DEFLATED
        output.writestr(readme_info, "Karak Tea five-house showcase\n\n"
                        "Requires Horizon revision 66f3981, Karak Tea 0.2.0 and its native extension.\n"
                        "Install and enable the matching .hmod and native client before opening this world.\n" + mod_pin +
                        "Put the Karak_Tea_Showcase folder into the chosen instance's saves folder.\n"
                        "Spawn: 6 65 -5. Five shops share the paved boulevard to the south.\n"
                        "Emerald and milk/bread supply chests are labeled at spawn.\n"
                        "Survival, peaceful, daylight and weather frozen.\n"
                        "No private player data or game installation assets are included.\n")
    return {"file": str(destination), "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            "excluded": excluded, "builder_gossip_rows_removed": removed_gossip,
            "construction_debris_entities_removed": removed_debris}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--ctl", type=Path)
    parser.add_argument("--socket")
    parser.add_argument("--archive", type=Path, default=ROOT / f"dist/Karak_Tea_{VERSION}.hmod")
    parser.add_argument("--expected-sha256", help="Use an explicitly pinned immutable integration snapshot")
    parser.add_argument("--evidence", type=Path, default=ROOT / "evidence/private/showcase")
    parser.add_argument("--export-world", type=Path)
    parser.add_argument("--export-zip", type=Path)
    args = parser.parse_args()
    if args.export_world or args.export_zip:
        if not args.export_world or not args.export_zip or args.apply:
            parser.error("Use --export-world and --export-zip together, without --apply")
        print(json.dumps(export_map(args.export_world, args.export_zip), indent=2))
        return
    plots = plots_from_structures(args.archive) if args.apply else PLOTS
    commands = plan(plots)
    if not args.apply:
        print(json.dumps({"world": WORLD, "spawn": SPAWN, "plots": plots, "commands": commands}, indent=2))
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
    receipt = {"world": WORLD, "archive_sha256": digest, "spawn": SPAWN, "plots": plots,
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
        # Replacing an older showcase chest can drop its previous contents.
        ctl("command", "kill @e[type=item,x=-46,y=61,z=-14,dx=106,dy=17,dz=54]")
        ctl("command", "kill @e[type=experience_orb,x=-46,y=61,z=-14,dx=106,dy=17,dz=54]")
        for p in plots:
            door = p["doors"][0]
            lectern = p["lectern"]
            jx, jy, jz = p["connector"]
            receipt["checks"][p["style"]] = {
                "door": ctl("block", p["x"]+door[0], p["base_y"]+door[1], p["z"]+door[2]),
                "lectern": ctl("block", p["x"]+lectern[0], p["base_y"]+lectern[1], p["z"]+lectern[2]),
                "entry_floor": ctl("block", p["x"]+jx, p["base_y"]+jy, p["z"]+jz)}
        receipt["checks"]["entities"] = ctl("entities", 100, "villager")
        receipt["checks"]["emeralds"] = ctl("container", 3, 65, -7)
        receipt["checks"]["milk"] = ctl("container", 9, 65, -7)
        receipt["final"] = ctl("state")
        receipt["save"] = ctl("save")
    finally:
        (args.evidence / "Build_Receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
