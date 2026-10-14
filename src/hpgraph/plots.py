"""Görselleştirme fonksiyonları. Hepsi ``matplotlib.figure.Figure`` döndürür."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns

HOUSE_COLORS = {
    "Gryffindor": "#C0392B",
    "Slytherin": "#27AE60",
    "Ravenclaw": "#2E86C1",
    "Hufflepuff": "#F1C40F",
    "Bilinmiyor": "#95A5A6",
}
RELATION_STYLE = {
    "friend": {"color": "#7F8C8D", "style": "solid"},
    "family": {"color": "#8E44AD", "style": "solid"},
    "ally": {"color": "#2C3E50", "style": "solid"},
    "enemy": {"color": "#E74C3C", "style": "dashed"},
}


def compute_layout(G: nx.Graph, seed: int = 42) -> dict:
    """Tüm grafiklerde aynı yerleşimi kullanmak için tek seferlik hesaplanır."""
    return nx.spring_layout(G, seed=seed, k=0.9, iterations=200, weight=None)


def _house_colors(G):
    return [HOUSE_COLORS[G.nodes[n]["house"]] for n in G]


def _house_legend(ax, extra=None):
    handles = [
        plt.Line2D([], [], marker="o", ls="", color=c, label=h, markersize=9)
        for h, c in HOUSE_COLORS.items()
    ]
    if extra:
        handles += extra
    ax.legend(handles=handles, loc="lower left", frameon=True, fontsize=9)


def plot_network(G, pos, node_size=None, title="", show_relations=False):
    """Ev renkli ağ grafiği. Düğüm boyutu ``node_size`` sözlüğüyle belirlenir."""
    fig, ax = plt.subplots(figsize=(14, 10))
    sizes = [node_size[n] for n in G] if node_size else 900
    if show_relations:
        for rel, st in RELATION_STYLE.items():
            edges = [(u, v) for u, v, d in G.edges(data=True) if d["relation"] == rel]
            nx.draw_networkx_edges(
                G, pos, edgelist=edges, edge_color=st["color"], style=st["style"], alpha=0.7, ax=ax
            )
        extra = [
            plt.Line2D([], [], color=s["color"], ls="--" if s["style"] == "dashed" else "-", label=r)
            for r, s in RELATION_STYLE.items()
        ]
    else:
        nx.draw_networkx_edges(G, pos, edge_color="#BDC3C7", alpha=0.8, ax=ax)
        extra = None
    nx.draw_networkx_nodes(
        G, pos, node_color=_house_colors(G), node_size=sizes, edgecolors="white", linewidths=1.2, ax=ax
    )
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold", ax=ax)
    _house_legend(ax, extra)
    ax.set_title(title, fontsize=14)
    ax.axis("off")
    fig.tight_layout()
    return fig


def plot_top_bars(table: pd.DataFrame, column: str, title: str, n: int = 10, color="#6C3483"):
    top = table[column].sort_values(ascending=True).tail(n)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(top.index, top.values, color=[HOUSE_COLORS[table.loc[i, "house"]] for i in top.index])
    ax.set_xlabel(column)
    ax.set_title(title)
    for y, v in enumerate(top.values):
        ax.text(v, y, f" {v:.3f}", va="center", fontsize=8)
    ax.set_xlim(0, top.values.max() * 1.15)
    fig.tight_layout()
    return fig


def plot_centrality_panel(table: pd.DataFrame):
    """Dört metriğin ilk 10'u tek panelde."""
    cols = [
        ("degree_centrality", "Degree"),
        ("closeness", "Closeness"),
        ("betweenness", "Betweenness"),
        ("eigenvector", "Eigenvector"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, (col, name) in zip(axes.ravel(), cols):
        top = table[col].sort_values().tail(10)
        ax.barh(top.index, top.values, color=[HOUSE_COLORS[table.loc[i, "house"]] for i in top.index])
        ax.set_title(f"{name} Centrality - İlk 10")
    fig.tight_layout()
    return fig


def plot_house_heatmap(matrix: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
    ax.set_title("Evler Arası Bağlantı Sayısı (köşegen: ev içi)")
    fig.tight_layout()
    return fig


def plot_degree_distribution(G: nx.Graph):
    degrees = [d for _, d in G.degree()]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].hist(degrees, bins=range(min(degrees), max(degrees) + 2), color="#2E86C1",
                 edgecolor="black", alpha=0.8, align="left")
    axes[0].set(title="Derece Dağılımı", xlabel="Derece", ylabel="Karakter sayısı")
    counts = pd.Series(degrees).value_counts().sort_index()
    ccdf = counts[::-1].cumsum()[::-1] / len(degrees)
    axes[1].loglog(ccdf.index, ccdf.values, "o-", color="#C0392B")
    axes[1].set(title="Tamamlayıcı Birikimli Dağılım (log-log)", xlabel="Derece k", ylabel="P(derece ≥ k)")
    axes[1].grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_communities(G, communities, pos):
    palette = sns.color_palette("tab10", len(communities))
    color = {n: palette[i] for i, c in enumerate(communities) for n in c}
    fig, ax = plt.subplots(figsize=(14, 10))
    nx.draw_networkx_edges(G, pos, edge_color="#BDC3C7", alpha=0.8, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=[color[n] for n in G], node_size=900,
                           edgecolors=[HOUSE_COLORS[G.nodes[n]["house"]] for n in G],
                           linewidths=3, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold", ax=ax)
    handles = [plt.Line2D([], [], marker="o", ls="", color=palette[i],
                          label=f"Topluluk {i + 1} ({len(c)})", markersize=9)
               for i, c in enumerate(communities)]
    ax.legend(handles=handles, loc="upper left", title="Louvain toplulukları (kenar rengi = ev)")
    ax.set_title("Topluluk Tespiti", fontsize=14)
    ax.axis("off")
    fig.tight_layout()
    return fig


def plot_robustness(curves: list[pd.DataFrame]):
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = {"degree": "Hedefli (derece)", "betweenness": "Hedefli (betweenness)", "random": "Rastgele (ort.)"}
    for df in curves:
        s = df["strategy"].iloc[0]
        ax.plot(df["removed"], df["lcc_fraction"], marker="o", ms=3, label=labels[s])
    ax.set(title="Ağ Dayanıklılığı", xlabel="Silinen düğüm sayısı", ylabel="En büyük bileşenin oranı")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def plot_correlation(corr: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, ax=ax)
    ax.set_title("Merkezilik Metrikleri Arası Spearman Korelasyonu")
    fig.tight_layout()
    return fig


def save(fig, path: Path | str, dpi: int = 130) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)

