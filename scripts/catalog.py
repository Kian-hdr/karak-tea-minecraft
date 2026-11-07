"""Shop inventory and one-time upgrade for existing Karak Sellers."""
import json

CATALOG = (
    ('karak_tea', 'Karak Tea', 1),
    ('iced_karak', 'Iced Karak', 1),
    ('decaf_karak', 'Decaf Karak', 1),
    ('karak_milkshake', 'Karak Milkshake', 2),
    ('karak_protein_shake', 'Karak Protein Shake', 3),
    ('karak_pro_max', 'Karak Pro Max', 8),
)


def offer(item='karak_tea'):
    price = next(price for ident, _, price in CATALOG if ident == item)
    return {'buy': {'id': 'minecraft:emerald', 'count': price},
            'sell': {'id': 'karak_house:' + item, 'count': 1},
            'maxUses': 16, 'uses': 0, 'rewardExp': True, 'xp': 0,
            'priceMultiplier': 0.0}


def write_catalog(write):
    lines = []
    for item, _, _ in CATALOG:
        value = json.dumps(offer(item), separators=(',', ':'))
        lines.append(f'execute unless data entity @s Offers.Recipes[{{sell:{{id:"karak_house:{item}"}}}}] run data modify entity @s Offers.Recipes append value {value}')
    lines.append('tag @s add karak_catalog_020_six')
    write('data/karak_house/function/catalog/upgrade_seller.mcfunction', '\n'.join(lines) + '\n')
    write('data/karak_house/horizon/creative_tab/tea.json', {
        'title': 'Karak Tea', 'icon': 'karak_house:karak_tea',
        'items': ['karak_house:' + item for item, _, _ in CATALOG]})
    write('assets/karak_house/lang/en_us.json', {
        prefix + item: name for item, name, _ in CATALOG for prefix in ['item.karak_house.', 'block.karak_house.']})
