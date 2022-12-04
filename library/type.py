__all__ = ['Data', 'Excerpts', 'FilterDate', 'FilterType', 'Meta', 'Range']


import datetime
import typing as t

import pandas as pd


Data = t.Dict[str, pd.DataFrame]
Excerpts = t.Dict[str, str]
Meta = t.Dict[str, t.Dict[str, str]]

FilterDate = t.Dict[
    t.Tuple[datetime.date, datetime.date],
    t.List[str],
]
FilterType = t.Dict[str, t.List[str]]


class Range:
    def __class_getitem__(cls, T: type) -> type:
        return t.Tuple[t.Optional[T], t.Optional[T]]
