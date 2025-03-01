__all__ = ['Item', 'Items', 'api']


import typing as t

import numpy as np

from .constant import data, meta
from ..type import Range

if t.TYPE_CHECKING:
    from typing_extensions import Self


class Item(t.NamedTuple):
    link: str
    title: str
    data: np.ndarray
    dates: np.ndarray

    @property
    def diff(self) -> np.ndarray:
        return np.diff(self.data)

    @property
    def max(self) -> float:
        return self.data.max()

    @property
    def min(self) -> float:
        return self.data.min()

    @property
    def mean(self) -> float:
        return self.data.mean()


class Items(list):
    @classmethod
    def from_args(cls, *items: Item) -> 'Self':
        return cls(list(items))

    @classmethod
    def from_iterator(cls, iterator: t.Iterator) -> 'Self':
        return cls.from_args(*iterator)

    def filter_data_min(
        self,
        min: t.Optional[int] = None, max: t.Optional[int] = None,
    ) -> 'Self':
        func = self._filter_minmax(min, max)
        return self.from_args(*filter(lambda item: func(item.min), self))

    def filter_data_max(
        self,
        min: t.Optional[int] = None, max: t.Optional[int] = None,
    ) -> 'Self':
        func = self._filter_minmax(min, max)
        return self.from_args(*filter(lambda item: func(item.max), self))

    def filter_data_length(
        self,
        min: t.Optional[int] = None, max: t.Optional[int] = None,
    ) -> 'Self':
        func = self._filter_minmax(min, max)
        return self.from_args(*filter(lambda item: func(len(item.data)), self))

    def filter_data_set_length(
        self,
        min: t.Optional[int] = None, max: t.Optional[int] = None,
    ) -> 'Self':
        func = self._filter_minmax(min, max)
        return self.from_args(*filter(lambda item: func(len(set(item.data))), self))

    def filter_data_diff(
        self,
        min: t.Optional[int] = None, max: t.Optional[int] = None,
    ) -> 'Self':
        func = self._filter_minmax_ndarray(min, max)
        return self.from_args(*filter(lambda item: func(item.diff).all(), self))

    def sort_data_max(self, reverse: bool = True) -> 'Self':
        return self.__class__(sorted(self, key=lambda item: item.max, reverse=reverse))

    def _filter_minmax(
        self,
        min: t.Optional[int] = None, max: t.Optional[int] = None,
    ) -> t.Callable:
        if min is None:
            if max is None:
                return lambda item: True
            else:
                return lambda item: item<=max
        else:
            if max is None:
                return lambda item: min<=item
            else:
                return lambda item: min<=item<=max

    def _filter_minmax_ndarray(
        self,
        min: t.Optional[int] = None, max: t.Optional[int] = None,
    ) -> t.Callable:
        if min is None:
            if max is None:
                return lambda item: np.ones_like(item, dtype=bool)
            else:
                return lambda item: item<=max
        else:
            if max is None:
                return lambda item: min<=item
            else:
                return lambda item: (min<=item) & (item<=max)


def api(
    links: t.Iterable[str],
    length_range: Range[int] = (9, None),
    set_length_range: Range[int] = (9, None),
    max_range: Range[float] = (700.0, None),
    diff_range: Range[float] = (-10.0, None),
) -> Items:
    '''
    Example:
        ```python
        for item in api(...):
            print('Dates:', item.dates[0], '-->', item.dates[-1])
            print('Title:', item.title)
            print('Link :', item.link)
            print('Data :', item.data.astype(int).tolist())
            print()
        ```
    '''
    return Items.from_iterator(
        Item(
            link=link, title=meta[link]['title'],
            data=data[link]['热度'].to_numpy(),
            dates=data[link].index.to_numpy(),
        ) for link in links
    ) \
        .filter_data_length(*length_range) \
        .filter_data_set_length(*set_length_range) \
        .filter_data_max(*max_range) \
        .filter_data_diff(*diff_range) \
        .sort_data_max()
