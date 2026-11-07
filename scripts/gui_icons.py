"""Editable 16-pixel silhouettes for GUI only; existing 3-D models stay in hand.

Every colored run is a shallow cuboid using a fixed sample of a vanilla block
texture. No PNG or generated raster resource is created or redistributed.
"""

VARIANTS = (
    ('karak_tea', 'black', 'K'),
    ('iced_karak', 'blue', 'I'),
    ('decaf_karak', 'purple', 'D'),
    ('karak_milkshake', 'pink', 'M'),
    ('karak_protein_shake', 'green', 'P'),
    ('karak_pro_max', 'red', 'PM'),
)

GLYPHS = {
    'K': ('101', '110', '100', '110', '101'),
    'I': ('111', '010', '010', '010', '111'),
    'D': ('110', '101', '101', '101', '110'),
    'M': ('101', '111', '111', '101', '101'),
    'P': ('110', '101', '110', '100', '100'),
    '+': ('010', '010', '111', '010', '010'),
}


def cup_materials():
    """Read the canonical 3-D generator so icon materials cannot drift."""
    from cup_model import write_cup_model
    materials = {}

    def capture(path, model):
        if path.startswith('assets/karak_house/models/item/'):
            materials[path.rsplit('/', 1)[1][:-5]] = model['textures']

    write_cup_model(capture)
    return materials


def gui_icon_model(item, color, glyph, materials=None):
    materials = materials or cup_materials()[item]
    grid = [[' ' for _ in range(16)] for _ in range(16)]

    def rect(x0, y0, x1, y1, token):
        for y in range(y0, y1):
            for x in range(x0, x1):
                grid[y][x] = token

    # Coordinates are whole pixels, top to bottom. Different silhouettes remain
    # legible at the hotbar's native 16-pixel item size.
    left, right, top, bottom = 4, 12, 3, 15
    if item == 'karak_pro_max':
        left, right, top = 3, 13, 1
    elif item == 'iced_karak':
        left, right, top = 5, 12, 3
    elif item == 'decaf_karak':
        top, bottom = 5, 14
    rect(left, top, right, bottom, 'O')
    rect(left + 1, top + 1, right - 1, bottom - 1,
         'C' if item in ('karak_milkshake', 'karak_protein_shake') else 'T')
    rect(left, top, right, top + 1, 'W')
    rect(left + 1, top + 1, left + 2, min(top + 4, bottom - 1), 'W')
    rect(left + 1, bottom - 2, right - 1, bottom - 1, 'H')
    sleeve_top = 7
    rect(left, sleeve_top, right, min(sleeve_top + 6, bottom - 1), 'S')
    if item in ('iced_karak', 'karak_milkshake'):
        rect(10, 0, 11, top + 3, 'W')
        rect(10, 1, 11, 2, 'S')
    if item == 'iced_karak':
        rect(7, 4, 9, 6, 'W')
        rect(10, 5, 11, 6, 'H')
    if item == 'decaf_karak':
        rect(12, 6, 15, 12, 'O')
        rect(12, 7, 14, 11, 'W')
        rect(12, 8, 13, 10, ' ')
    if item == 'karak_protein_shake':
        rect(3, 3, 13, 5, 'O')
        rect(4, 3, 12, 4, 'S')
        rect(6, 1, 10, 3, 'O')
        rect(7, 1, 10, 2, 'W')
    if item == 'karak_pro_max':
        rect(left, 6, right, 7, 'G')
        rect(left, 13, right, 14, 'G')
    glyph_left = 5 if len(glyph) == 2 else (7 if item == 'iced_karak' else 6)
    for index, letter in enumerate(glyph):
        for y, row in enumerate(GLYPHS[letter]):
            for x, pixel in enumerate(row):
                if pixel == '1':
                    grid[sleeve_top + y][glyph_left + index * 4 + x] = 'W'

    textures = {
        'O': materials['label'],  # pale glass edge / ceramic decaf body
        'W': materials['label'],
        'C': materials['tea'],
        'T': materials['tea'],
        'H': materials['tea'],
        'S': materials['sleeve'],
        'G': materials['trim'],
        'surface': materials['surface'],
        'glass': materials['glass'],
    }
    elements = []
    for y, row in enumerate(grid):
        x = 0
        while x < 16:
            token = row[x]
            end = x + 1
            while end < 16 and row[end] == token:
                end += 1
            if token != ' ':
                material = token
                if token in ('T', 'C') and y == top + 1:
                    material = 'surface'
                if item == 'decaf_karak' and token in ('O', 'H'):
                    material = 'W'
                if item == 'iced_karak' and token == 'W' and y in (4, 5):
                    material = 'glass'
                if item == 'karak_protein_shake' and token == 'O' and y <= 4:
                    material = 'G' if y <= 2 else 'S'
                if item == 'karak_protein_shake' and token == 'W' and y <= 2:
                    material = 'G'
                # Both sides make this an ordinary editable shallow model. The
                # GUI transform faces it straight at the camera, without tilt.
                elements.append({
                    'name': f'pixel_run_{y}_{x}_{token}',
                    'from': [x, 15-y, 7.95], 'to': [end, 16-y, 8.05],
                    'shade': False,
                    'faces': {face: {'texture': '#' + material,
                                     'uv': ([0, 0, 0.01, 0.01] if material == 'glass'
                                            else [8, 8, 8.01, 8.01])}
                              for face in ('north', 'south')},
                })
            x = end
    return {
        'parent': 'minecraft:block/block', 'ambientocclusion': False,
        'gui_light': 'front', 'textures': textures, 'elements': elements,
        'display': {'gui': {'rotation': [0, 0, 0], 'translation': [0, 0, 0],
                            'scale': [1, 1, 1]}},
    }


def write_gui_icons(write):
    """Call after write_cup_model; overwrite only GUI-aware item definitions."""
    materials = cup_materials()
    for item, color, glyph in VARIANTS:
        icon = f'karak_house:item/gui/{item}'
        write(f'assets/karak_house/models/item/gui/{item}.json',
              gui_icon_model(item, color, glyph, materials[item]))
        write(f'assets/karak_house/items/{item}.json', {
            'model': {
                'type': 'minecraft:select', 'property': 'minecraft:display_context',
                'cases': [{'when': 'gui',
                           'model': {'type': 'minecraft:model', 'model': icon}}],
                'fallback': {'type': 'minecraft:model',
                             'model': f'karak_house:item/{item}'},
            },
        })
