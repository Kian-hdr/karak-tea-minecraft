"""Editable square tea jar, using existing Minecraft textures only."""

GLYPHS = {
    ' ': ['000', '000', '000', '000', '000'],
    'K': ['101', '110', '100', '110', '101'],
    'A': ['010', '101', '111', '101', '101'],
    'R': ['110', '101', '110', '101', '101'],
    'H': ['101', '101', '111', '101', '101'],
    'O': ['111', '101', '101', '101', '111'],
    'U': ['101', '101', '101', '101', '111'],
    'S': ['111', '100', '111', '001', '111'],
    'E': ['111', '100', '110', '100', '111'],
    'I': ['111', '010', '010', '010', '111'],
    'C': ['111', '100', '100', '100', '111'],
    'D': ['110', '101', '101', '101', '110'],
    'F': ['111', '100', '110', '100', '100'],
    'P': ['111', '101', '111', '100', '100'],
    'M': ['101', '111', '111', '101', '101'],
    'X': ['101', '101', '010', '101', '101'],
    'L': ['100', '100', '100', '100', '111'],
    'N': ['101', '111', '111', '111', '101'],
    'T': ['111', '010', '010', '010', '010'],
}


def cup_model(sleeve, words, iced=False, scale=1.0, kind=""):
    elements = []

    def box(name, a, b, texture, faces=None):
        elements.append({'name': name, 'from': a, 'to': b,
                         'faces': {face: {'texture': '#' + texture}
                                   for face in (faces or ['north', 'south', 'east', 'west', 'up', 'down'])}})

    # A square, open glass jar. The caramel fill remains visible above and below
    # its dark sleeve; no mug handle or photo/raster label is included.
    box('glass_base', [4, 1, 4], [12, 1.6, 12], 'glass')
    box('glass_left', [4, 1.6, 4], [4.55, 10.8, 12], 'glass')
    box('glass_right', [11.45, 1.6, 4], [12, 10.8, 12], 'glass')
    box('glass_front', [4.55, 1.6, 4], [11.45, 10.8, 4.55], 'glass')
    box('glass_back', [4.55, 1.6, 11.45], [11.45, 10.8, 12], 'glass')
    box('caramel_tea', [4.4, 1.65, 4.4], [11.6, 9.8, 11.6], 'tea')
    box('tea_surface', [4.4, 9.8, 4.4], [11.6, 9.95, 11.6], 'surface')
    for name, a, b in [
        ('rim_left', [3.8, 10.3, 3.8], [4.45, 11.15, 12.2]),
        ('rim_right', [11.55, 10.3, 3.8], [12.2, 11.15, 12.2]),
        ('rim_front', [4.45, 10.3, 3.8], [11.55, 11.15, 4.45]),
        ('rim_back', [4.45, 10.3, 11.55], [11.55, 11.15, 12.2]),
    ]:
        box(name, a, b, 'label')
    # Short highlights sit directly on the glass wall, above and below the sleeve.
    for suffix, y0, y1 in [('upper', 8.45, 9.9), ('lower', 2.0, 3.5)]:
        box('glass_highlight_' + suffix, [4.65, y0, 3.98], [4.95, y1, 4.04], 'label', ['north'])
    box('sleeve_front', [3.85, 4.0, 3.85], [12.15, 8.15, 4.0], 'sleeve')
    box('sleeve_back', [3.85, 4.0, 12.0], [12.15, 8.15, 12.15], 'sleeve')
    box('sleeve_left', [3.85, 4.0, 4.0], [4.0, 8.15, 12.0], 'sleeve')
    box('sleeve_right', [12.0, 4.0, 4.0], [12.15, 8.15, 12.0], 'sleeve')

    # The lettering is geometry. Runs of adjacent pixels become one thin box.
    for word, top in zip(words, [7.45, 5.85]):
        pixel = min(0.22, 7.1 / (len(word) * 4 - 1))
        start = (16 - (len(word) * 4 - 1) * pixel) / 2
        for letter_index, char in enumerate(word):
            for row_index, row in enumerate(GLYPHS[char]):
                col = 0
                while col < len(row):
                    if row[col] == '0':
                        col += 1
                        continue
                    end = col + 1
                    while end < len(row) and row[end] == '1':
                        end += 1
                    x0 = start + (letter_index * 4 + col) * pixel
                    x1 = start + (letter_index * 4 + end) * pixel
                    y0, y1 = top - (row_index + 1) * pixel, top - row_index * pixel
                    name = f'label_{word}_{letter_index}_{row_index}_{col}'
                    box(name + '_front', [16-x1, y0, 3.80], [16-x0, y1, 3.83], 'label', ['north'])
                    box(name + '_back', [x0, y0, 12.17], [x1, y1, 12.20], 'label', ['south'])
                    col = end

    if iced:
        box('ice_1',[5.0,9.95,5.2],[7.1,10.7,7.3],'glass')
        box('ice_2',[8.2,9.95,8.0],[10.5,10.8,10.3],'glass')
    if kind == 'decaf_karak':
        for element in elements:
            if element['name'].startswith(('glass_', 'rim_')):
                for face in element['faces'].values(): face['texture']='#label'
            for key in ['from','to']:
                element[key][1]=1+(element[key][1]-1)*0.86
        box('decaf_handle_lower',[12.0,3.2,6.4],[14.5,4.0,9.6],'label')
        box('decaf_handle_outer',[14.0,4.0,6.4],[14.8,7.5,9.6],'label')
        box('decaf_handle_upper',[12.0,7.5,6.4],[14.5,8.3,9.6],'label')
    if kind == 'iced_karak':
        for element in elements:
            for key in ['from','to']:
                x,y,z=element[key];element[key]=[8+(x-8)*0.9,1+(y-1)*1.18,8+(z-8)*0.9]
        box('iced_straw',[9.25,10.5,8.3],[9.85,15.2,8.9],'label')
        box('iced_straw_stripe',[9.23,13.1,8.28],[9.87,13.6,8.92],'sleeve')
    if kind == 'karak_milkshake':
        box('milkshake_straw',[9.4,9.4,8.3],[10.0,14.2,8.9],'label')
        box('straw_stripe',[9.38,12.2,8.28],[10.02,12.65,8.92],'sleeve')
    if kind == 'karak_protein_shake':
        box('shaker_lid',[3.7,10.6,3.7],[12.3,11.8,12.3],'sleeve')
        box('shaker_cap',[6.0,11.8,6.0],[10.0,12.7,10.0],'trim')
    if scale > 1:
        for y0,y1 in [(3.8,4.0),(8.15,8.35)]:
            for a,b in [([3.82,y0,3.82],[12.18,y1,3.97]),([3.82,y0,12.03],[12.18,y1,12.18]),([3.82,y0,3.97],[3.97,y1,12.03]),([12.03,y0,3.97],[12.18,y1,12.03])]:
                box('premium_trim',a,b,'trim')
        vertical = 1.55
        for element in elements:
            for key in ['from','to']:
                x,y,z=element[key]
                raised_y = 1+(y-1)*vertical
                if element['name'].startswith('label_'):
                    raised_y = 1+(y-1)*scale+(6.075-1)*(vertical-scale)
                element[key]=[8+(x-8)*scale,raised_y,8+(z-8)*scale]
    # Draw the tea before translucent glass so the glass does not mask the fill
    # in Horizon's item renderer.
    elements.sort(key=lambda e: 0 if e['name'] in ('caramel_tea', 'tea_surface') else 1)
    return {
        'parent': 'minecraft:block/block',
        'textures': {'glass': 'minecraft:block/white_stained_glass',
                     'tea': 'minecraft:block/white_terracotta' if kind in ('karak_milkshake','karak_protein_shake') else 'minecraft:block/orange_terracotta',
                     'surface': 'minecraft:block/quartz_block_bottom' if kind in ('karak_milkshake','karak_protein_shake') else 'minecraft:block/yellow_terracotta',
                     'sleeve': sleeve,
                     'label': 'minecraft:block/quartz_block_bottom',
                     'trim': 'minecraft:block/iron_block',
                     'particle': 'minecraft:block/orange_terracotta'},
        'elements': elements,
        'display': {
            'gui': {'rotation': [25, 225, 0], 'translation': [0, -1, 0], 'scale': [0.9, 1.02 if scale > 1 else 0.9, 0.9]},
            'firstperson_righthand': {'rotation': [0, -30, 0], 'translation': [-1.5, 5.5, 0], 'scale': [0.42, 0.48 if scale > 1 else 0.42, 0.42]},
            'thirdperson_righthand': {'rotation': [0, 0, 0], 'translation': [0, 3, 0], 'scale': [0.55, 0.63 if scale > 1 else 0.55, 0.55]},
        },
    }


def write_cup_model(write):
    variants = [
        ('karak_tea','minecraft:block/black_terracotta',('KARAK','HOUSE'),False,1.0),
        ('iced_karak','minecraft:block/blue_terracotta',('ICED','KARAK'),True,1.0),
        ('decaf_karak','minecraft:block/purple_terracotta',('DECAF','KARAK'),False,1.0),
        ('karak_milkshake','minecraft:block/pink_terracotta',('KARAK','MILKSHAKE'),False,1.0),
        ('karak_protein_shake','minecraft:block/green_terracotta',('KARAK','PROTEIN'),False,1.0),
        ('karak_pro_max','minecraft:block/red_terracotta',('KARAK','PRO MAX'),False,1.3),
    ]
    for item, sleeve, words, iced, scale in variants:
        write(f'assets/karak_house/models/item/{item}.json',cup_model(sleeve,words,iced,scale,item))
        write(f'assets/karak_house/items/{item}.json',{'model':{'type':'minecraft:model','model':f'karak_house:item/{item}'}})
