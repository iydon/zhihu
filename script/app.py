import datetime

import altair as alt
import pandas as pd
import streamlit as st

from cache import meta, data, filter_date, filter_type


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


keys = ['热度', '关注', '浏览', '赞同', '评论', '回答']
meta_inversed = {v: k for k, v in meta.items()}
links = data.keys()
with st.sidebar:
    with st.form('filter'):
        types = st.multiselect('类别：', filter_type.keys(), ['zhihu.com/question'])
        links_by_type = [filter_type[type] for type in types]
        today, oneday = datetime.date.today(), datetime.timedelta(days=1)
        date_begin = st.date_input('开始时间：', today-oneday)
        date_end = st.date_input('结束时间：', today)
        links_by_date = [links for (dmin, dmax), links in filter_date.items() if not (dmax<date_begin or dmin>date_end)]
        links = set(sum(links_by_type, start=[])) & set(sum(links_by_date, start=[]))
        st.form_submit_button('筛选')
    with st.form('titles'):
        links_sorted = sorted(links, key=lambda k: data[k]['热度'].max(), reverse=True)
        titles = st.multiselect('请选择问题：', [meta[link] for link in links_sorted])
        submitted = st.form_submit_button('提交')
if submitted and titles:
    meta_selected = {title: meta_inversed[title] for title in titles}
    for key, tab in zip(keys, st.tabs(keys)):
        with tab:
            df = pd.DataFrame.from_dict({
                title: data[link][key]
                for title, link in meta_selected.items()
            })
            st.altair_chart(altair_chart(df), use_container_width=True)
    with st.expander('链接'):
        st.markdown('\n'.join(
            f'- [{title}]({link})'
            for title, link in meta_selected.items()
        ))
