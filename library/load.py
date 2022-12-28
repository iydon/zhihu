__all__ = ['cached', 'raw']


import ast
import datetime
import io
import pickle
import re
import typing as t

import pandas as pd
import py7zr

from .config import path
from .type import Data, Excerpts, FilterDate, FilterType, Meta


class raw:
    _data = None
    _meta = None

    @classmethod
    def cache_clear(cls) -> None:
        cls._data = cls._meta = None

    @classmethod
    def cache_once(cls) -> None:
        caches = [cls._data, cls._meta]
        if all(map(lambda x: x is not None, caches)):
            return
        cls._data, cls._meta = cls._get_data_meta()

    @classmethod
    def data(cls) -> Data:
        cls.cache_once()
        return cls._data

    @classmethod
    def meta(cls) -> Meta:
        cls.cache_once()
        return cls._meta

    @classmethod
    def _excerpts(cls) -> Excerpts:
        return pd \
            .read_csv(path.excerpts, sep='\t', header=None, index_col=0) \
            .squeeze('columns') \
            .to_dict()

    @classmethod
    def _get_data_meta(cls) -> t.Tuple[Data, Meta]:
        meta, data, temp = {}, {}, {}
        excerpts = cls._excerpts()
        # meta
        for file in path.root.rglob('*.7z'):
            with py7zr.SevenZipFile(file, 'r') as z:
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
        # data
        for link, dfs in temp.items():
            df = pd.concat(dfs, axis=0).sort_index()
            df.index = df.index.map(datetime.datetime.fromtimestamp)
            data[link] = df.astype('float64')
        return data, meta


class cached:
    _data = None
    _meta = None
    _filter_date = None
    _filter_type = None

    @classmethod
    def all(cls) -> t.Tuple[Data, Meta, FilterDate, FilterType]:
        return cls.data(), cls.meta(), cls.filter_date(), cls.filter_type()

    @classmethod
    def clear(cls) -> None:
        cls._data = cls._meta = cls._filter_date, cls._filter_type = None
        raw.cache_clear()

    @classmethod
    def cache_once(cls) -> None:
        caches = [cls._data, cls._meta, cls._filter_date, cls._filter_type]
        if all(map(lambda x: x is not None, caches)):
            return
        file = path.cache_today()
        if not file.exists():
            data, meta = raw.data(), raw.meta()
            filter_date, filter_type = cls._get_filter_date(data), cls._get_filter_type(data)
            file.write_bytes(pickle.dumps((data, meta, filter_date, filter_type)))
        cls._data, cls._meta, cls._filter_date, cls._filter_type = pickle.loads(file.read_bytes())

    @classmethod
    def data(cls) -> Data:
        cls.cache_once()
        return cls._data

    @classmethod
    def meta(cls) -> Meta:
        cls.cache_once()
        return cls._meta

    @classmethod
    def filter_date(cls) -> FilterDate:
        cls.cache_once()
        return cls._filter_date

    @classmethod
    def filter_type(cls) -> FilterType:
        cls.cache_once()
        return cls._filter_type

    @classmethod
    def _get_filter_date(cls, data: Data) -> FilterDate:
        filter_date = {}
        for link, df in data.items():
            key = (df.index[0].date(), df.index[-1].date())
            if key not in filter_date:
                filter_date[key] = []
            filter_date[key].append(link)
        return filter_date

    @classmethod
    def _get_filter_type(cls, data: Data) -> FilterType:
        filter_type = {}
        patterns = {
            'zhuanlan.zhihu.com': {re.compile(r'https?://zhuanlan\.zhihu\.com/p/\d+')},
            'zhihu.com/question': {re.compile(r'https?://www\.zhihu\.com/question/\d+')},
            'zhihu.com/theater': {re.compile(r'https?://www\.zhihu\.com/theater/\d+')},
            'zhihu.com/zvideo': {re.compile(r'https?://www\.zhihu\.com/zvideo/\d+')},
            'zhihu.com/special': {re.compile(r'https?://www\.zhihu\.com/special/\d+')},
            'zhihu.com/xen/market': {re.compile(r'https?://www\.zhihu\.com/xen/market/ecom-page/\d+'), re.compile(r'https?://www\.zhihu\.com/market/paid_column/\d+/section/\d+')},
            'zhihu.com/roundtable': {re.compile(r'https?://www\.zhihu\.com/roundtable/[a-zA-Z0-9]+')},
            'zhihu.com/campaign': {re.compile(r'https?://www\.zhihu\.com/campaign/[a-z0-9\-]')},
            'zhihu.com/vip-promotion': {re.compile(r'https?://www\.zhihu\.com/vip-promotion/[a-z\-]')},
            'zhi.hu': {re.compile(r'https?://zhi\.hu/[a-zA-Z]+')},
            'zhihu.com/topic': {re.compile(r'https?://www.zhihu.com/topic/\d+/hot')},
            'zhihu.com/pin': {re.compile(r'https?://www.zhihu.com/pin/\d+')},
            'event.zhihu.com': {re.compile(r'https?://event.zhihu.com/\S+')},
        }
        errors = []
        for link in data.keys():
            for type, pattern in patterns.items():
                if any(p.match(link) for p in pattern):
                    if type not in filter_type:
                        filter_type[type] = []
                    filter_type[type].append(link)
                    break
            else:
                errors.append(link)
        if errors:
            raise Exception(errors)
        return filter_type
