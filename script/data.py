__all__ = ['meta', 'data']


import ast
import datetime
import io
import pathlib as p

import pandas as pd
import py7zr


root = p.Path(__file__).parents[1]
meta, data, temp = {}, {}, {}
excerpts = pd \
    .read_csv(root/'data'/'excerpts.tsv', sep='\t', header=None, index_col=0) \
    .squeeze('columns') \
    .to_dict()
for path in root.rglob('*.7z'):
    with py7zr.SevenZipFile(path, 'r') as z:
        for line in z.read()['data.tsv'].readlines():
            link, title, text = map(
                ast.literal_eval,
                line.decode().split('\t', maxsplit=2),
            )
            with io.StringIO(text) as f:
                df = pd.read_csv(f, index_col=0)
            meta[link] = {
                'title': title,
                'excerpt': excerpts.get(link, None),
            }
            temp.setdefault(link, []).append(df)
for link, dfs in temp.items():
    df = pd.concat(dfs, axis=0).sort_index()
    df.index = df.index.map(datetime.datetime.fromtimestamp)
    data[link] = df.astype('float64')
