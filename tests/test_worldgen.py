"""Worldgen regression checks; these do not claim frequency or walkability."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from worldgen import write_worldgen
from validate_villages import STYLES, block_state, summarize, transformed


class WorldgenContract(unittest.TestCase):
    def test_each_style_has_one_direct_bounded_candidate(self):
        definitions = {}
        write_worldgen(definitions.__setitem__, STYLES)
        self.assertEqual(len(definitions), 5)
        keys = set()
        for style in STYLES:
            addition = definitions[f'data/karak_house/worldgen/template_pool/additions/{style}.json']
            expected = [f'minecraft:village/{style}/houses',
                        f'minecraft:village/{style}/zombie/houses',
                        f'minecraft:village/{style}/terminators']
            if style in ('desert', 'savanna'):
                expected.append(f'minecraft:village/{style}/zombie/terminators')
            self.assertEqual(addition['horizon:add_to'], expected)
            self.assertEqual(len(addition['elements']), 1)
            candidate = addition['elements'][0]['element']
            self.assertEqual(candidate['element_type'], 'lithostitched:guaranteed')
            self.assertEqual(candidate['count'], 1)
            self.assertEqual(candidate['delegate']['location'], f'karak_house:village/karak_house_{style}')
            self.assertEqual(candidate['delegate']['projection'], 'rigid')
            keys.add(json.dumps(candidate, sort_keys=True))
        # Distinct styles are distinct Horizon limit keys. A namespace-wide cap
        # cannot be inferred from five entries each declaring count=1.
        self.assertEqual(len(keys), 5)

    def test_world_rotation_matches_jigsaw_coordinate_convention(self):
        expected = {'NONE': (13, 24, 35), 'CLOCKWISE_90': (5, 24, 33),
                    'CLOCKWISE_180': (7, 24, 25), 'COUNTERCLOCKWISE_90': (15, 24, 27)}
        for rotation, position in expected.items():
            self.assertEqual(transformed(dict(PosX=10, PosY=20, PosZ=30, rotation=rotation), 3, 4, 5), position)

    def test_heterogeneous_palette_wrapper_is_unwrapped(self):
        self.assertEqual(block_state({'': 'minecraft:dirt_path'}), {'id': 'minecraft:dirt_path'})
        self.assertEqual(block_state('minecraft:stone_bricks'), {'id': 'minecraft:stone_bricks'})

    def test_presence_never_masks_duplicates_or_absence(self):
        rows = [dict(style='plains', count=n, houses=[]) for n in (0, 1, 2)]
        summary = summarize(rows)
        self.assertEqual(summary['villages_with_house'], 2)
        self.assertEqual(summary['duplicate_villages'], 1)
        self.assertEqual(summary['frequency'], 2 / 3)
        self.assertFalse(summary['geometry_acceptance'])

if __name__ == '__main__':
    unittest.main()
