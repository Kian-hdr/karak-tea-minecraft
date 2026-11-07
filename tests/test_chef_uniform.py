import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from chef_uniform import MIGRATION_TAG, write_chef_uniform


class ChefUniformTests(unittest.TestCase):
    def test_migration_targets_sellers_and_preserves_existing_headgear(self):
        files = {}
        write_chef_uniform(files.__setitem__)
        tick = files['data/karak_house/function/uniform/tick.mcfunction']
        apply = files['data/karak_house/function/uniform/apply.mcfunction']
        self.assertIn('type=minecraft:villager,tag=karak_seller', tick)
        self.assertIn('tag=!' + MIGRATION_TAG, tick)
        self.assertIn('unless data entity @s equipment.head', apply)
        self.assertNotIn('Offers', apply)
        self.assertNotIn('karak_free', apply)
        self.assertNotIn('karak_day', apply)


if __name__ == '__main__':
    unittest.main()
