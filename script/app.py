import pandas as pd
import streamlit as st

from cache import meta, data


keys = ['热度', '关注', '浏览', '赞同', '评论', '回答']
meta_inversed = {v: k for k, v in meta.items()}
links = sorted(data.keys(), key=lambda k: data[k]['热度'].max(), reverse=True)
with st.sidebar:
    with st.form('titles'):
        titles = st.multiselect('请选择问题：', [meta[link] for link in links])
        submitted = st.form_submit_button('提交')
if submitted and titles:
    meta_selected = {title: meta_inversed[title] for title in titles}
    for key, tab in zip(keys, st.tabs(keys)):
        with tab:
            st.line_chart(
                pd.DataFrame.from_dict({
                    title: data[link][key]
                    for title, link in meta_selected.items()
                }),
            )
    with st.expander('链接'):
        st.markdown('\n'.join(
            f'- [{title}]({link})'
            for title, link in meta_selected.items()
        ))
