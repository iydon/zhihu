__all__ = ['altair_chart', 'api']


import collections as c
import typing as t

import altair as alt
import pandas as pd

from .constant import data, meta
from ..config import keys


def altair_chart(df: pd.DataFrame) -> alt.LayerChart:
    # Reference: https://altair-viz.github.io/gallery/multiline_tooltip.html
    df.index.name = '时间'
    df.index = df.index.tz_localize('Asia/Shanghai')
    source = df.reset_index().melt('时间', var_name='标题', value_name='数值')
    nearest = alt.selection(type='single', nearest=True, on='mouseover', fields=['时间'], empty='none')
    line = alt.Chart(source).mark_line(interpolate='basis').encode(x='时间:T', y='数值:Q', color='标题:N')
    selectors = alt.Chart(source).mark_point().encode(x='时间:T', opacity=alt.value(0)).add_selection(nearest)
    points = line.mark_point().encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))
    text = line.mark_text(align='left', dx=5, dy=-5).encode(text=alt.condition(nearest, '数值:Q', alt.value(' ')))
    rules = alt.Chart(source).mark_rule(color='gray').encode(x='时间:T').transform_filter(nearest)
    return alt.layer(line, selectors, points, rules, text)


def api(links: t.Iterable[str]) -> t.OrderedDict[str, pd.DataFrame]:
    return c.OrderedDict([
        (
            key, pd.DataFrame.from_dict({
                meta[link]['title']: data[link][key]
                for link in links
            })
        ) for key in keys
    ])
