__all__ = ['api', 'font_names']


import collections as c
import typing as t

import jieba
import matplotlib.pyplot as plt
import wordcloud

from .constant import data, meta, stopwords
from ..config import path

if t.TYPE_CHECKING:
    from matplotlib.figure import Figure


def api(
    links: t.Iterable[str],
    width: int = 800, height: int = 800, weighted: bool = True,
    font_name: t.Optional[str] = None,
    extra_words: t.Optional[t.Iterable[str]] = None,
    extra_stopwords: t.Optional[t.Iterable[str]] = None,
) -> 'Figure':
    # tokenizer
    tokenizer = jieba.Tokenizer()
    for word in (extra_words or []):
        tokenizer.add_word(word)
    all_stopwords = stopwords.union(extra_stopwords or set())
    # counter
    counter = c.defaultdict(float)
    for link in links:
        excerpt = meta[link]['excerpt']
        if excerpt is None:
            continue
        metric = data[link]['热度'].mean() if weighted else 1.0
        for word in set(tokenizer.cut(excerpt, cut_all=False)):
            if word in all_stopwords:
                continue
            counter[word] += metric
    # figure
    font_name = font_name or font_names()[0].as_posix()
    wc = wordcloud \
        .WordCloud(
            font_path=(path.fonts/font_name).as_posix(),
            background_color='white', width=width, height=height,
        ) \
        .generate_from_frequencies(counter)
    fig, ax = plt.subplots(1, 1)
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    return fig


def font_names() -> t.List[str]:
    return [
        file.relative_to(path.fonts).as_posix()
        for file in path.fonts.glob('*.[ot]tf')
    ]
