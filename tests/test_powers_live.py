"""Opt-in real-engine no-fall acceptance against a separate disposable world.

Requires HORIZON_CTL and KARAK_POWERS_SOCKET=/tmp/karak-powers.sock.
Never launches a game or controls the user's showcase.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
CTL = os.environ.get("HORIZON_CTL")
SOCKET = os.environ.get("KARAK_POWERS_SOCKET")


@unittest.skipUnless(CTL and SOCKET == "/tmp/karak-powers.sock", "requires the dedicated powers fixture socket")
class PowersLive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = []

    @classmethod
    def tearDownClass(cls):
        path = ROOT / "evidence/private/powers/Live_Qualification.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cls.events, indent=2) + "\n")

    def ctl(self, *args):
        result = subprocess.run([CTL, "--socket", SOCKET, *map(str, args)],
                                capture_output=True, text=True, timeout=90)
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)
        value = json.loads(result.stdout)
        self.events.append({"command": list(args), "result": value})
        self.assertNotIn("error", value)
        return value

    def cmd(self, command):
        return self.ctl("command", command)

    def score(self, holder, objective):
        chat = " ".join(self.cmd(f"scoreboard players get {holder} {objective}")["chat"])
        match = re.search(r" has (-?\d+) \[", chat)
        self.assertIsNotNone(match, chat)
        return int(match.group(1))

    def attribute(self, name):
        self.cmd("scoreboard players set #attribute karak_probe -999999")
        self.cmd(f"execute store result score #attribute karak_probe run attribute @s minecraft:{name} get 1000000")
        value = self.score("#attribute", "karak_probe")
        self.assertNotEqual(-999999, value)
        return value / 1000000

    def drink(self, item):
        self.cmd(f"give @s {item} 1")
        self.ctl("wait", 3)
        self.ctl("select", item)
        self.ctl("look", 180, -50)
        self.ctl("mouse", "right", "down")
        self.ctl("wait", 35)
        self.ctl("mouse", "right", "up")
        self.ctl("wait", 3)

    def assert_tea(self):
        effects = self.ctl("state")["player"]["effects"]
        expected = {"strength": 3, "speed": 2, "jump_boost": 2,
                    "resistance": 1, "regeneration": 0, "fire_resistance": 0}
        self.assertEqual(expected, {e["id"]: e["amplifier"] for e in effects})
        self.assertEqual(0, self.attribute("fall_damage_multiplier"))
        self.assertEqual(.08, self.attribute("gravity"))
        self.assertGreater(self.score("@s", "karak_t_reg"), 5800)

    def fall(self):
        self.cmd("tp @s 0.5 91 0.5")
        start = self.ctl("state")
        trace = [start]
        for _ in range(80):
            self.ctl("wait", 1)
            state = self.ctl("state")
            trace.append(state)
            if state["player"]["on_ground"] and state["player"]["position"][1] < 72:
                break
        else:
            self.fail("20-block fall did not land")
        landed = trace[-1]
        # The client predicts landing before authoritative hurt packets arrive.
        self.ctl("wait", 5)
        acknowledged = self.ctl("state")
        return {"client_ticks": landed["ticks"] - start["ticks"],
                "minimum_velocity_y": min(s["player"]["velocity"][1] for s in trace),
                "health": acknowledged["player"]["health"], "trace": trace,
                "acknowledged_state": acknowledged, "server_hurt_log": self.ctl("hurtlog")}

    def test_regular_descent_reload_normal_milk_and_death(self):
        self.assertEqual("Powers_Qualification", self.ctl("state")["world"])
        self.cmd("scoreboard objectives add karak_probe dummy")
        self.cmd("function karak_house:powers/load")
        self.cmd("function karak_house:powers/clear")
        self.cmd("attribute @s minecraft:fall_damage_multiplier modifier remove karak_house:test_other")
        self.cmd("gamemode creative")
        self.cmd("fill -5 70 -5 5 70 5 stone")
        self.cmd("fill -5 71 -5 5 110 5 air")
        self.cmd("tp @s 0.5 71 0.5")
        self.cmd("gamerule minecraft:keep_inventory true")
        self.cmd("gamerule minecraft:spawn_mobs false")
        self.cmd("difficulty normal")
        self.cmd("gamemode survival")
        self.cmd("clear @s")
        self.cmd("effect give @s instant_health 1 10")
        self.cmd("effect clear @s")
        self.ctl("hurtlog")
        self.assertEqual(1, self.attribute("fall_damage_multiplier"))
        self.drink("karak_house:karak_tea")
        self.assert_tea()
        protected = self.fall()
        self.assertEqual(20, protected["health"])
        self.assertLess(protected["minimum_velocity_y"], -1)
        self.assertLessEqual(protected["client_ticks"], 30)
        self.events.append({"verified": "current_stack_regular_ordinary_descent", "tea": protected})
        self.ctl("wait", 60)
        before = self.score("@s", "karak_t_reg")
        self.drink("karak_house:karak_tea")
        self.assert_tea()
        self.assertGreater(self.score("@s", "karak_t_reg"), before)
        before = self.score("@s", "karak_t_reg")
        self.cmd("reload"); self.ctl("wait", 5)
        after = self.score("@s", "karak_t_reg")
        self.assertGreater(after, before - 50)
        self.assertLessEqual(after, before)
        self.assertEqual(0, self.attribute("fall_damage_multiplier"))
        self.drink("minecraft:milk_bucket")
        self.assertEqual([], self.ctl("state")["player"]["effects"])
        self.assertEqual(1, self.attribute("fall_damage_multiplier"))
        self.assertEqual(0, self.score("@s", "karak_t_reg"))
        self.drink("karak_house:karak_tea")
        self.drink("karak_house:iced_karak")
        self.cmd("kill @s"); self.ctl("wait", 25); self.ctl("respawn"); self.ctl("wait", 10)
        self.assertEqual([], self.ctl("state")["player"]["effects"])
        self.assertEqual(1, self.attribute("fall_damage_multiplier"))
        for objective in ["karak_t_reg", "karak_t_iced", "karak_t_decaf", "karak_t_pro", "karak_t_milk", "karak_t_protein"]:
            self.assertEqual(0, self.score("@s", objective))
        self.cmd("tp @s 0.5 71 0.5"); self.cmd("clear @s"); self.ctl("save")


if __name__ == "__main__":
    unittest.main()
