__all__ = ['keys', 'path']


import pathlib as p
import time


keys = ['热度', '关注', '浏览', '赞同', '评论', '回答']


class path:
    # directory
    root = p.Path(__file__).absolute().parents[1]
    cache = root / 'cache'
    data = root / 'data'
    stopwords = data / 'stopwords'
    # file
    excerpts = data / 'excerpts.tsv'

    @classmethod
    def cache_today(cls) -> p.Path:
        return cls.cache / time.strftime('%Y-%m-%d.pickle')

    @classmethod
    def mkdirs(cls) -> None:
        for directory in {cls.cache, cls.data, cls.stopwords}:
            directory.mkdir(parents=True, exist_ok=True)
