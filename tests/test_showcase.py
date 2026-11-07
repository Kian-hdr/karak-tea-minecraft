"""Layout checks; runtime accessibility and trading are recorded separately."""
import sys
import io
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

import nbtlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_showcase import PLOTS, WORLD, export_map, plan


class ShowcaseTests(unittest.TestCase):
    def test_all_five_shops_are_separate_and_compact(self):
        self.assertEqual(5, len({p["style"] for p in PLOTS}))
        for left, right in zip(PLOTS, PLOTS[1:]):
            self.assertLess(left["x"] + left["width"], right["x"])
        self.assertLessEqual(PLOTS[-1]["x"] + PLOTS[-1]["width"] - PLOTS[0]["x"], 110)

    def test_build_finishes_in_survival_with_supplies_not_free_tea(self):
        commands = plan()
        self.assertEqual("gamemode survival", commands[-1])
        self.assertEqual(5, sum(c.startswith("place template") for c in commands))
        self.assertFalse(any(c.startswith("give") for c in commands))
        self.assertTrue(any("advance_weather false" in c for c in commands))

    def test_map_export_omits_builder_identity_and_preserves_world_scores(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            world = root / WORLD
            (world / "players/data").mkdir(parents=True)
            (world / "data/minecraft").mkdir(parents=True)
            (world / "players/data/private-player.dat").write_bytes(b"private")
            (world / "players/data/00000000-0000-0000-0000-000000000001.dat").write_bytes(b"private")
            (world / "session.lock").write_bytes(b"lock")
            level = nbtlib.File({"Data": nbtlib.Compound({
                "LevelName": nbtlib.String(WORLD), "singleplayer_uuid": nbtlib.String("private-player")})})
            level.save(world / "level.dat", gzipped=True)
            scores = nbtlib.List[nbtlib.Compound]([
                nbtlib.Compound({"Name": nbtlib.String("KarakShowcase")}),
                nbtlib.Compound({"Name": nbtlib.String("seller-entity")})])
            nbtlib.File({"data": nbtlib.Compound({"PlayerScores": scores})}).save(
                world / "data/minecraft/scoreboard.dat", gzipped=True)
            # A real paid trade leaves a player UUID in a villager's gossip.
            entities = world / "dimensions/minecraft/overworld/entities"
            entities.mkdir(parents=True)
            gossip = nbtlib.List[nbtlib.Compound]([
                nbtlib.Compound({"Target": nbtlib.IntArray([0, 0, 0, 1])}),
                nbtlib.Compound({"Target": nbtlib.IntArray([0, 0, 0, 2])})])
            entity_tree = nbtlib.File({"Entities": nbtlib.List[nbtlib.Compound]([
                nbtlib.Compound({"id": nbtlib.String("minecraft:villager"), "Gossips": gossip})])})
            stream = io.BytesIO()
            entity_tree.write(stream)
            compressed = zlib.compress(stream.getvalue())
            chunk = (len(compressed) + 1).to_bytes(4, "big") + b"\x02" + compressed
            header = bytearray(8192)
            header[:4] = b"\x00\x00\x02\x01"
            (entities / "r.0.0.mca").write_bytes(header + chunk + bytes(4096 - len(chunk)))
            out = root / "map.zip"
            export_map(world, out)
            with zipfile.ZipFile(out) as archive:
                self.assertFalse(any("players/" in name or name.endswith("session.lock") for name in archive.namelist()))
                archive.extractall(root / "readback")
            copied = root / "readback" / WORLD
            self.assertNotIn("singleplayer_uuid", nbtlib.load(copied / "level.dat")["Data"])
            score_rows = nbtlib.load(copied / "data/minecraft/scoreboard.dat")["data"]["PlayerScores"]
            self.assertEqual(["seller-entity"], [str(row["Name"]) for row in score_rows])
            region = (copied / "dimensions/minecraft/overworld/entities/r.0.0.mca").read_bytes()
            offset = int.from_bytes(region[:3], "big") * 4096
            length = int.from_bytes(region[offset:offset + 4], "big")
            decoded = nbtlib.File.parse(io.BytesIO(zlib.decompress(region[offset + 5:offset + 4 + length])))
            retained = decoded["Entities"][0]["Gossips"]
            self.assertEqual([[0, 0, 0, 2]], [list(map(int, row["Target"])) for row in retained])


if __name__ == "__main__":
    unittest.main()
