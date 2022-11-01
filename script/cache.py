__all__ = ['meta', 'data']


import pathlib as p
import pickle


path = p.Path('cache.pickle')
if path.exists():
    meta, data = pickle.loads(path.read_bytes())
else:
    from data import meta, data

    path.write_bytes(pickle.dumps((meta, data)))
