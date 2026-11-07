import importlib.util
from pathlib import Path
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from gui_icons import VARIANTS, write_gui_icons

class CupModelTests(unittest.TestCase):
    def model(self):
        path=Path(__file__).resolve().parents[1]/'scripts/cup_model.py'
        self.assertTrue(path.exists(),'square glass jar generator missing')
        spec=importlib.util.spec_from_file_location('cup_model',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        outputs={};module.write_cup_model(lambda p,v:outputs.__setitem__(p,v))
        return outputs['assets/karak_house/models/item/karak_tea.json']
    def test_glass_jar_has_dark_sleeve_and_caramel_tea(self):
        m=self.model()
        self.assertEqual('minecraft:block/white_stained_glass',m['textures']['glass'])
        self.assertEqual('minecraft:block/black_terracotta',m['textures']['sleeve'])
        self.assertEqual('minecraft:block/orange_terracotta',m['textures']['tea'])
        self.assertTrue(any(e.get('name')=='tea_surface' for e in m['elements']))
    def test_square_jar_has_no_mug_handle_and_has_two_line_lettering(self):
        m=self.model()
        self.assertTrue(all(e['to'][0] <= 12.5 and e['from'][0] >= 3.5 for e in m['elements']))
        for word in ['KARAK','HOUSE']:
            self.assertTrue(any(e.get('name','').startswith('label_'+word) for e in m['elements']))

    def test_inventory_icons_route_only_gui_to_flat_models(self):
        outputs={};write_gui_icons(outputs.__setitem__)
        for item, _, _ in VARIANTS:
            definition=outputs[f'assets/karak_house/items/{item}.json']['model']
            self.assertEqual('minecraft:display_context',definition['property'])
            self.assertEqual('gui',definition['cases'][0]['when'])
            self.assertEqual(f'karak_house:item/{item}',definition['fallback']['model'])
            self.assertIn(f'assets/karak_house/models/item/gui/{item}.json',outputs)
if __name__=='__main__':unittest.main()
