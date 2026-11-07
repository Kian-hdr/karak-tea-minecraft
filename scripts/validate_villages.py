#!/usr/bin/env python3
"""Inspect natural village starts in an isolated Horizon world; never /place a village.

Requires nbtlib. `sample` operates ONLY an already running disposable local server,
locates five villages of each style from fixed anchors, force-loads natural terrain,
and records the saved start's complete piece list. `inspect` can rerun offline.
"""
import argparse
from collections import Counter
import gzip
import io
import json
from pathlib import Path
import re
import subprocess
import time
import zlib
import nbtlib

STYLES = ('plains', 'desert', 'savanna', 'taiga', 'snowy')
ANCHORS = ((0, 0), (10000, 0), (0, 10000), (-10000, 0), (0, -10000))


def chunk_nbt(world, cx, cz):
    path = Path(world) / 'dimensions/minecraft/overworld/region' / f'r.{cx // 32}.{cz // 32}.mca'
    if not path.exists():
        return None
    raw = path.read_bytes()
    offset = 4 * ((cx % 32) + 32 * (cz % 32))
    start = int.from_bytes(raw[offset:offset + 3], 'big') * 4096
    if not start:
        return None
    size = int.from_bytes(raw[start:start + 4], 'big')
    compression = raw[start + 4]
    payload = raw[start + 5:start + 4 + size]
    if compression == 2:
        payload = zlib.decompress(payload)
    elif compression == 1:
        payload = gzip.decompress(payload)
    elif compression != 3:
        raise ValueError(f'unsupported region compression {compression}')
    return nbtlib.File.parse(io.BytesIO(payload))


def plain(value):
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, nbtlib.tag.List, nbtlib.tag.Array)):
        return [plain(v) for v in value]
    if isinstance(value, str):
        return str(value)
    try:
        return int(value)
    except (ValueError, TypeError):
        return str(value)


def inspect_start(world, style, x, z):
    chunk = chunk_nbt(world, x // 16, z // 16)
    if chunk is None:
        return None
    start = chunk.get('structures', {}).get('starts', {}).get(f'minecraft:village_{style}')
    if not start or str(start.get('id')) == 'INVALID':
        return None
    children = plain(start.get('Children', []))
    houses = [p for p in children if p.get('pool_element', {}).get('location', '').startswith('karak_house:')]
    return dict(style=style, locate=[x, z], start_chunk=[x // 16, z // 16],
                chunk_status=str(chunk.get('Status')), count=len(houses), houses=houses, pieces=children)


def transformed(piece, x, y, z):
    rotation = piece['rotation']
    x, z = {'NONE': (x, z), 'CLOCKWISE_90': (-z, x),
            'CLOCKWISE_180': (-x, -z), 'COUNTERCLOCKWISE_90': (z, -x)}[rotation]
    return piece['PosX'] + x, piece['PosY'] + y, piece['PosZ'] + z



def transformed_point(piece, x, y, z):
    """Transform a continuous point, rotating around block-cell centers.

    Block positions use transformed(); entity/player centers additionally need
    the cell-center offset on axes whose rotation reverses their sign.
    """
    px, py, pz = transformed(piece, x - .5, y, z - .5)
    return px + .5, py, pz + .5


def block_state(value):
    value = plain(value)
    if isinstance(value, dict) and set(value) == {''}:
        value = value['']
    return {'id': value} if isinstance(value, str) else value


def saved_block(world, x, y, z, cache=None):
    cache = {} if cache is None else cache
    key = (x // 16, z // 16)
    if key not in cache:
        cache[key] = chunk_nbt(world, *key)
    chunk = cache[key]
    if chunk is None:
        return {'id': 'UNLOADED'}
    section = next((s for s in chunk['sections'] if int(s['Y']) == y // 16), None)
    if section is None:
        return {'id': 'minecraft:air'}
    states = section['block_states']
    palette = states['palette']
    if len(palette) == 1:
        return block_state(palette[0])
    bits = max(4, (len(palette) - 1).bit_length())
    per_long = 64 // bits
    index = (y % 16) * 256 + (z % 16) * 16 + (x % 16)
    word = int(states['data'][index // per_long]) & ((1 << 64) - 1)
    state = (word >> ((index % per_long) * bits)) & ((1 << bits) - 1)
    return block_state(palette[state])


def entrance_sections(world, records):
    """Read actual saved block columns across road/approach/door, in local space.

    This is physical evidence, not an automated navigation acceptance test.
    Negative local Z lies outside the house, toward the connecting village road.
    """
    out = []
    widths = {'plains': 13, 'desert': 15, 'savanna': 13, 'taiga': 13, 'snowy': 13}
    cache = {}
    for record in records:
        for house in record['houses']:
            columns = []
            for z in range(-3, 7):
                blocks = []
                for y in range(-3, 4):
                    pos = transformed(house, widths[record['style']] // 2, y, z)
                    blocks.append(dict(local_y=y, position=pos, state=saved_block(world, *pos, cache=cache)))
                columns.append(dict(local_z=z, blocks=blocks))
            grid = []
            for z in range(6):
                for dx in (-1, 0, 1):
                    cells = [saved_block(world, *transformed(house, widths[record['style']] // 2 + dx, y, z), cache=cache) for y in range(3)]
                    grid.append(dict(local_x=widths[record['style']] // 2 + dx, local_z=z,
                                     floor=cells[0], feet=cells[1], head=cells[2]))
            out.append(dict(style=record['style'], locate=record['locate'], house=house,
                            columns=columns, approach_grid=grid))
    return out


def audit_pool_reachability(resources, pack):
    """Conservative graph: follow every jigsaw and fallback, irrespective of depth.

    Lithostitched limits key by exact serialized element. The count=1 contract
    therefore proves the per-start cap only when a start reaches one Karak key.
    This audit is for the pinned vanilla resources plus this mod, not other mods.
    """
    base = Path(resources) / 'worldgen'
    pools = {k: json.loads(v) if isinstance(v, str) else v
             for k, v in json.loads((base / 'template_pools.json').read_text()).items()}
    structures = {k: json.loads(v) if isinstance(v, str) else v
                  for k, v in json.loads((base / 'structures.json').read_text()).items()}
    for p in sorted((Path(pack) / 'data/karak_house/worldgen/template_pool').rglob('*.json')):
        addition = json.loads(p.read_text())
        targets = addition.get('horizon:add_to', [])
        for target in [targets] if isinstance(targets, str) else targets:
            pools[target]['elements'].extend(addition.get('elements', []))
    template_cache = {}
    def outgoing(element):
        kind = element.get('element_type')
        if 'delegate' in element:
            return outgoing(element['delegate'])
        if kind == 'minecraft:list_pool_element':
            return set().union(*(outgoing(e) for e in element['elements']))
        location = element.get('location')
        if not location:
            return set()
        if location not in template_cache:
            namespace, name = location.split(':', 1) if ':' in location else ('minecraft', location)
            path = (Path(pack) / 'data' / namespace / 'structure' / (name + '.nbt')
                    if namespace == 'karak_house' else base / 'structure' / namespace / (name + '.nbt'))
            template = nbtlib.load(path)
            template_cache[location] = {str(b['nbt']['pool']) for b in template['blocks']
                                        if b.get('nbt', {}).get('id') == 'minecraft:jigsaw'}
        return template_cache[location]
    report = {}
    for style in STYLES:
        pending = [structures[f'minecraft:village_{style}']['start_pool']]
        visited, keys = set(), set()
        while pending:
            pool = pending.pop()
            if pool in visited:
                continue
            visited.add(pool)
            definition = pools[pool]
            if definition.get('fallback'):
                pending.append(definition['fallback'])
            for entry in definition.get('elements', []):
                element = entry['element']
                if 'karak_house:' in json.dumps(element):
                    if element.get('element_type') != 'lithostitched:guaranteed' or element.get('count') != 1:
                        raise ValueError(f'unbounded Karak pool element in {pool}')
                    keys.add(json.dumps(element, sort_keys=True, separators=(',', ':')))
                pending.extend(outgoing(element) - visited)
        report[style] = dict(reachable_pools=sorted(visited), karak_limit_keys=sorted(keys),
                             per_start_cap_proven=len(keys) == 1)
    return report


def run_sample(args):
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    transcript = output / 'commands.jsonl'
    def cmd(command):
        result = subprocess.run([args.server, '--dir', args.server_dir, 'cmd', command],
                                capture_output=True, text=True, timeout=120)
        with transcript.open('a') as f:
            f.write(json.dumps(dict(command=command, returncode=result.returncode,
                                    stdout=result.stdout, stderr=result.stderr)) + '\n')
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        return result.stdout
    metadata = {"seed": cmd("seed"), "version": cmd("version")}
    (output / "runtime.json").write_text(json.dumps(metadata, indent=2) + "\n")
    records = json.loads((output / 'villages.json').read_text()) if args.resume else []
    if args.resume:
        actual = {str(f.relative_to(Path(args.pack))): __import__('hashlib').sha256(f.read_bytes()).hexdigest()
                  for f in Path(args.pack).rglob('*') if f.is_file()}
        if actual != json.loads((output / 'pack_hashes.json').read_text()):
            raise RuntimeError('resume refused: staged pack differs from pinned original sample')
        for row in records:
            if row['style'] not in STYLES or tuple(row['anchor']) not in ANCHORS:
                raise RuntimeError('resume refused: unexpected existing sample row')
    seen = {tuple(row['locate']) for row in records}
    for style in STYLES:
        for ax, az in ANCHORS:
            if any(row['style'] == style and row['anchor'] == [ax, az] for row in records):
                continue
            response = cmd(f'execute positioned {ax} 80 {az} run locate structure minecraft:village_{style}')
            match = re.search(r'\[(-?\d+), ~, (-?\d+)\]', response)
            if not match:
                raise RuntimeError(response)
            x, z = map(int, match.groups())
            if (x, z) in seen:
                raise RuntimeError(f'duplicate sample {(x,z)}; change anchors before sampling')
            seen.add((x, z))
            cmd('forceload remove all')
            cmd(f'forceload add {x - 96} {z - 96} {x + 96} {z + 96}')
            deadline = time.monotonic() + 120
            record = None
            while time.monotonic() < deadline:
                time.sleep(2)
                cmd('save-all flush')
                record = inspect_start(args.world, style, x, z)
                if record and record['chunk_status'] == 'minecraft:full':
                    # A final settle lets the surrounding loaded chunks finish placing pieces.
                    time.sleep(2)
                    cmd('save-all flush')
                    break
            if record is None:
                raise RuntimeError(f'natural start not saved: {style} {x} {z}')
            record['anchor'] = [ax, az]
            records.append(record)
            (output / 'villages.json').write_text(json.dumps(records, indent=2) + '\n')
            print(f'{style} {x} {z}: {record["count"]} Karak House(s), {len(record["pieces"])} pieces', flush=True)
    cmd('forceload remove all')
    cmd('save-all flush')
    (output / 'entrance_sections.json').write_text(json.dumps(entrance_sections(args.world, records), indent=2) + '\n')
    summary = summarize(records)
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


def summarize(records):
    n = len(records)
    present = sum(r['count'] >= 1 for r in records)
    return dict(sample_size=n, villages_with_house=present, frequency=present / n if n else 0,
                frequency_target=0.8, placement_frequency_passed=n >= 25 and present / n >= 0.8,
                max_one_passed=all(r['count'] <= 1 for r in records),
                duplicate_villages=sum(r['count'] > 1 for r in records),
                by_style={s: dict(samples=sum(r['style'] == s for r in records),
                                  houses=sum(r['count'] for r in records if r['style'] == s)) for s in STYLES},
                rotations=dict(Counter(p['rotation'] for r in records for p in r['houses'])),
                natural_generation=True, placement_commands_used=False,
                geometry_acceptance=False,
                limitations=['One deterministic world seed and five fixed anchors per style; not an unbiased frequency estimate.',
                             'Piece census does not alone establish physical walkability or visual acceptance.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sample = sub.add_parser('sample')
    for name in ('server', 'server-dir', 'world', 'output'):
        sample.add_argument('--' + name, required=True)
    audit = sub.add_parser('audit')
    audit.add_argument('--resources', required=True)
    audit.add_argument('--pack', required=True)
    audit.add_argument('--output', required=True)
    sample.add_argument('--resume', action='store_true')
    sample.add_argument('--pack', default='.test/worldgen/pack')
    inspect = sub.add_parser('inspect')
    inspect.add_argument('--world', required=True)
    inspect.add_argument('--villages', required=True)
    args = parser.parse_args()
    if args.action == 'sample':
        run_sample(args)
    elif args.action == 'audit':
        report = audit_pool_reachability(args.resources, args.pack)
        Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: v['per_start_cap_proven'] for k, v in report.items()}))
    else:
        rows = json.loads(Path(args.villages).read_text())
        print(json.dumps(summarize([inspect_start(args.world, r['style'], *r['locate']) for r in rows]), indent=2))

if __name__ == '__main__':
    main()
