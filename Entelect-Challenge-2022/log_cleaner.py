#! /usr/bin/env python3

import json
import sys
import os
import mmap
from tqdm import tqdm

log = sys.argv[1]
step = 2 if len(sys.argv) <= 2 else int(sys.argv[2])

print('cleaning', log, 'with a step of', step)

delete = set([
    'PopulationTiers',

    'World/Map/ScoutTowers/Nodes',
    'World/Map/ScoutTowers/Territory',
    'World/Map/ScoutTowers/Id',

    'World/Map/Nodes/TerritoryBase',
    'World/Map/Nodes/Ticks',
    'World/Map/Nodes/CurrentRegenTick',
    'World/Map/Nodes/RegenerationRate',
    'World/Map/Nodes/RegenerationRate',
    'World/Map/Nodes/MaxResourceAmount',
    'World/Map/Nodes/Reward',
    'World/Map/Nodes/MaxUnits',
    'World/Map/Territory',

    'Bots/CurrentTierLevel',
    'Bots/Position',
    'Bots/Buildings/Territory',
    'Bots/Buildings/StatusMultiplier',
    'Bots/Map/AvailableNodes',
    'Bots/Map/ScoutTowers',
])

path = []

def check(d, path=[]):
    if type(d) is list:
        for item in d:
            check(item, path)
    elif type(d) is dict:
        to_delete = []
        for key in d:
            p = path + [key]

            if '/'.join(p) in delete:
                to_delete.append(key)
            elif type(d[key]) in [dict, list]:
                check(d[key], path=p)

        for key in to_delete:
            del d[key]

rounds = []

with open(log, 'r') as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
        size = m.size()
        pbar = tqdm(total=size-2, unit='B', unit_scale=True, unit_divisor=1024)

        start = 1
        num = 0
        while start < size:
            # find the start of the next round
            end = m.find(b'{"World"', start + 1) - 2

            if end < 0:
                end = size - 2

            # update the progress bar
            pbar.n = end
            pbar.refresh()

            # check if round end position was found
            if num % step == 0:
                data = json.loads(m[start:end+1].decode())
                check(data)
                rounds.append(data)

            num += 1
            start = end + 2

        pbar.close()

dirname = os.path.dirname(log)
fname, ext = os.path.splitext(os.path.basename(log))

new_path = os.path.join(dirname, f'{fname}_clean{ext}')
print(f'writing cleaned logs to {new_path}')

with open(new_path, 'w') as f:
    json.dump(rounds, f)