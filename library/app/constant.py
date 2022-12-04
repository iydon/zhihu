__all__ = ['all', 'data', 'meta', 'filter_date', 'filter_type', 'stopwords']


import functools as f

from .. import load
from ..config import path


all = load.cached.all()
data, meta, filter_date, filter_type = all
stopwords = f.reduce(
    set.union, (
        set(path.read_text().splitlines())
        for path in path.stopwords.iterdir()
    ), set()
)
