import datetime
import functools as f
import typing as t

import streamlit as st

from library.app import constant, filter, plot, wordcloud
from library.type import FilterDate, FilterType

if t.TYPE_CHECKING:
    from typing_extensions import Self


data, meta, filter_date, filter_type = constant.all
titles_inversed = {v['title']: k for k, v in meta.items()}


class App:
    def __init__(self) -> None:
        pass

    def __getitem__(self, key: str) -> t.Callable:
        return self.all[key]

    @classmethod
    def new(cls, *args: t.Any, **kwargs: t.Any) -> 'Self':
        return cls(*args, **kwargs)

    @f.cached_property
    def all(self) -> t.Dict[str, t.Callable]:
        return {
            '绘图': self.plot,
            '筛选': self.filter,
            '词云': self.wordcloud,
        }

    def links_by_date(self, filter_date: FilterDate) -> t.Set[str]:
            today, oneday = datetime.date.today(), datetime.timedelta(days=1)
            date_begin = st.date_input('开始时间：', today-oneday)
            date_end = st.date_input('结束时间：', today)
            return f.reduce(
                set.union, (
                    set(links)
                    for (dmin, dmax), links in filter_date.items()
                    if not (dmax<date_begin or dmin>date_end)
                ), set()
            )

    def links_by_type(self, filter_type: FilterType) -> t.Set[str]:
        types = st.multiselect('类别：', filter_type.keys(), ['zhihu.com/question'])
        return f.reduce(set.union, (set(filter_type[type]) for type in types), set())

    def plot(self, links: t.List[str]) -> None:
        with st.form('plot'):
            links_sorted = sorted(links, key=lambda k: data[k]['热度'].max(), reverse=True)
            titles = st.multiselect('请选择问题：', [meta[link]['title'] for link in links_sorted])
            st.form_submit_button('提交')
        if titles:
            links_selected = [titles_inversed[title] for title in titles]
            dfs = plot.api(links_selected)
            for tab, (key, df) in zip(st.tabs(dfs.keys()), dfs.items()):
                with tab:
                    diff = st.checkbox('差值', value=False, key=key)
                    if diff:
                        df = df.diff()
                    st.altair_chart(plot.altair_chart(df), use_container_width=True)
            with st.expander('链接'):
                self._markdown(f'- [{meta[link]["title"]}]({link})' for link in links_selected)

    def filter(self, links: t.List[str]) -> None:
        with st.form('filter'):
            hour_min = st.slider('热榜时长阈值（小时）：', min_value=0.0, max_value=24.0, value=3.0, step=0.25)
            set_length = st.slider('唯一值阈值（个）：', min_value=0, max_value=48, value=9, step=1)
            max = st.slider('最大值阈值（万热度）：', min_value=1, max_value=5_000, value=700, step=1)
            diff = st.slider('差值阈值（万热度）：', min_value=-100, max_value=100, value=-10, step=1)
            st.form_submit_button('提交')
        items = filter.api(
            links,
            length_range=(int(4*hour_min), None), set_length_range=(set_length, None),
            max_range=(max, None), diff_range=(diff, None),
        )
        self._markdown(
            (
                '-\n'
                f'    - 题目：[{item.title}]({item.link})\n'
                f'    - 日期：{item.dates[0]} → {item.dates[-1]}\n'
                f'    - 热度：{item.data.astype(int).tolist()}'
            ) for item in items
        )

    def wordcloud(self, links: t.List[str]) -> None:
        with st.form('wordcloud'):
            width = st.slider('宽度：', min_value=64, max_value=1024, value=512, step=1)
            height = st.slider('高度：', min_value=64, max_value=1024, value=512, step=1)
            weighted = '热榜热度' == st.selectbox('权重：', ['热榜热度', '热榜数量'])
            font_name = st.selectbox('字体：', wordcloud.font_names())
            extra_words = st.text_input('额外新词（空格分隔）：', '奥密克戎 斯诺登')
            extra_stopwords = st.text_input('额外停用词（空格分隔）：', '% 「 时 天 日 月 年 中 会')
            st.form_submit_button('提交')
        fig = wordcloud.api(
            links, width, height, weighted, font_name,
            extra_words.split(), extra_stopwords.split(),
        )
        st.pyplot(fig)

    def _markdown(self, lines: t.Iterable[str]) -> None:
        st.markdown('\n'.join(lines))


if __name__ == '__main__':
    app = App.new()
    with st.sidebar:
        with st.form('sidebar'):
            key = st.selectbox('功能：', app.all.keys())
            links = app.links_by_type(filter_type) & app.links_by_date(filter_date)
            st.form_submit_button('运行')
    app[key](list(links))
