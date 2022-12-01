__all__ = ['meta', 'data', 'filter_date', 'filter_type']


import pathlib as p
import pickle
import re
import time


path = p.Path('cache', time.strftime('%Y-%m-%d.pickle'))
path.parent.mkdir(parents=True, exist_ok=True)
if path.exists():
    meta, data, filter_date, filter_type = pickle.loads(path.read_bytes())
else:
    from data import meta, data

    # date
    filter_date = {}
    for link, df in data.items():
        key = (df.index[0].date(), df.index[-1].date())
        if key not in filter_date:
            filter_date[key] = []
        filter_date[key].append(link)
    # type
    patterns = {
        'zhuanlan.zhihu.com': {re.compile(r'https?://zhuanlan\.zhihu\.com/p/\d+')},
        'zhihu.com/question': {re.compile(r'https?://www\.zhihu\.com/question/\d+')},
        'zhihu.com/theater': {re.compile(r'https?://www\.zhihu\.com/theater/\d+')},
        'zhihu.com/zvideo': {re.compile(r'https?://www\.zhihu\.com/zvideo/\d+')},
        'zhihu.com/special': {re.compile(r'https?://www\.zhihu\.com/special/\d+')},
        'zhihu.com/xen/market': {re.compile(r'https?://www\.zhihu\.com/xen/market/ecom-page/\d+'), re.compile(r'https?://www\.zhihu\.com/market/paid_column/\d+/section/\d+')},
        'zhihu.com/roundtable': {re.compile(r'https?://www\.zhihu\.com/roundtable/[a-zA-Z]+')},
        'zhihu.com/campaign': {re.compile(r'https?://www\.zhihu\.com/campaign/[a-z0-9\-]')},
        'zhihu.com/vip-promotion': {re.compile(r'https?://www\.zhihu\.com/vip-promotion/[a-z\-]')},
        'zhi.hu': {re.compile(r'https?://zhi\.hu/[a-zA-Z]+')},
    }
    filter_type = {}
    for link in data.keys():
        for type, pattern in patterns.items():
            if any(p.match(link) for p in pattern):
                if type not in filter_type:
                    filter_type[type] = []
                filter_type[type].append(link)
                break
        else:
            raise Exception(link)
    # dump
    path.write_bytes(pickle.dumps((meta, data, filter_date, filter_type)))
