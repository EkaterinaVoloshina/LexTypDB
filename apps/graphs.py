import streamlit as st
from database_utils import init_connection, find_sem_maps
import networkx as nx
from collections import Counter
import matplotlib.pyplot as plt


def get_edges(results):
    edges = []
    for i in results:
        for context in i[parameter]:
            for context_2 in i[parameter]:
                if context != context_2:
                    edge = context_2 + "+" + context
                    if edge not in edges:
                        edges.append(context + "+" + context_2)
    return edges


def app():
    db = init_connection()
    col1, col2 = st.columns([5, 5])

    with col1:
        language = st.multiselect(
            label='Язык:',
            options=db.languages.find().distinct('lang')
        )
    with col2:
        field = st.multiselect(
            label='Поле:',
            options=db.fields.find().distinct('field')
        )
    parameter = st.selectbox(
        label="Параметр:",
        options=["frames", "contexts"]
    )
    button = st.button("Search")
    if button:
        results = find_sem_maps(db, language, field)
        edges = get_edges(results)
        G = nx.Graph()
        for string, num in Counter(edges).items():
            G.add_edge(*string.split('+'), weight=num)
        pos = nx.spring_layout(G, seed=1734289230)
        fig, ax = plt.subplots(figsize=(10, 10))
        nx.draw_networkx_edges(G, pos, alpha=0.3)
        nx.draw_networkx_nodes(G, pos, alpha=0.9)
        nx.draw_networkx_labels(G, pos=pos)
        st.pyplot(fig)
