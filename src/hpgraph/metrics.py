"""Graf metrikleri ve analiz fonksiyonları."""
from __future__ import annotations

import itertools
import math
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd

from .data import HOUSES, largest_component


# --------------------------------------------------------------------------- #
# Genel özet
# --------------------------------------------------------------------------- #
def network_summary(G: nx.Graph) -> dict:
    """Ağın temel istatistikleri."""
    comps = list(nx.connected_components(G))
    main = G.subgraph(max(comps, key=len))
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "density": nx.density(G),
        "avg_degree": 2 * G.number_of_edges() / G.number_of_nodes(),
        "avg_clustering": nx.average_clustering(G),
        "transitivity": nx.transitivity(G),
        "components": len(comps),
        "main_component_size": main.number_of_nodes(),
        "diameter": nx.diameter(main),
        "radius": nx.radius(main),
        "avg_shortest_path": nx.average_shortest_path_length(main),
        "isolated": [n for n in G if G.degree(n) == 0],
    }


# --------------------------------------------------------------------------- #
# Merkezilik
# --------------------------------------------------------------------------- #
def centrality_table(G: nx.Graph) -> pd.DataFrame:
    """Her karakter için merkezilik metriklerini içeren tablo.

    Yol tabanlı metrikler (closeness, betweenness) ağırlıksız hesaplanır; böylece
    "kaç adımda ulaşılır" yorumu korunur. ``strength`` ağırlıklı dereceyi verir.
    """
    table = pd.DataFrame(
        {
            "house": pd.Series(nx.get_node_attributes(G, "house")),
            "degree": pd.Series(dict(G.degree())),
            "strength": pd.Series(dict(G.degree(weight="weight"))),
            "degree_centrality": pd.Series(nx.degree_centrality(G)),
            "closeness": pd.Series(nx.closeness_centrality(G)),
            "betweenness": pd.Series(nx.betweenness_centrality(G)),
            "eigenvector": pd.Series(nx.eigenvector_centrality_numpy(G)),
            "pagerank": pd.Series(nx.pagerank(G, weight="weight")),
            "clustering": pd.Series(nx.clustering(G)),
            "core_number": pd.Series(nx.core_number(G)),
        }
    )
    return table.sort_values("degree", ascending=False)


def top_n(table: pd.DataFrame, column: str, n: int = 5) -> list[tuple[str, float]]:
    s = table[column].sort_values(ascending=False).head(n)
    return list(s.items())


def centrality_correlation(table: pd.DataFrame) -> pd.DataFrame:
    """Merkezilik metrikleri arasındaki Spearman sıralama korelasyonu."""
    cols = ["degree", "strength", "closeness", "betweenness", "eigenvector", "pagerank"]
    return table[cols].corr(method="spearman")


# --------------------------------------------------------------------------- #
# Yapısal kırılganlık
# --------------------------------------------------------------------------- #
def cut_vertices_and_bridges(G: nx.Graph) -> tuple[list[str], list[tuple[str, str]]]:
    """Kesim noktaları (articulation points) ve köprü kenarlar."""
    return sorted(nx.articulation_points(G)), sorted(nx.bridges(G))


# --------------------------------------------------------------------------- #
# Evler
# --------------------------------------------------------------------------- #
def house_connection_matrix(G: nx.Graph) -> pd.DataFrame:
    """Evler arası kenar sayısı (köşegen: ev içi kenarlar)."""
    houses = [h for h in HOUSES if h in set(nx.get_node_attributes(G, "house").values())]
    m = pd.DataFrame(0, index=houses, columns=houses)
    for u, v in G.edges():
        hu, hv = G.nodes[u]["house"], G.nodes[v]["house"]
        m.loc[hu, hv] += 1
        if hu != hv:
            m.loc[hv, hu] += 1
    return m


def house_assortativity(G: nx.Graph) -> float:
    """Ev özniteliğine göre assortativity (+1: kişiler kendi evleriyle bağlanır)."""
    return nx.attribute_assortativity_coefficient(G, "house")


def house_assortativity_pvalue(G: nx.Graph, n_perm: int = 2000, seed: int = 42) -> float:
    """Permütasyon testi: ev etiketleri rastgele karıştırılınca bu kadar yüksek
    assortativity ne sıklıkla görülür? (tek yönlü p-değeri)"""
    rng = np.random.default_rng(seed)
    observed = house_assortativity(G)
    nodes = list(G.nodes)
    labels = [G.nodes[n]["house"] for n in nodes]
    H = G.copy()
    hits = 0
    for _ in range(n_perm):
        shuffled = rng.permutation(labels)
        nx.set_node_attributes(H, dict(zip(nodes, shuffled)), "house")
        if nx.attribute_assortativity_coefficient(H, "house") >= observed:
            hits += 1
    return (hits + 1) / (n_perm + 1)


# --------------------------------------------------------------------------- #
# Topluluk tespiti
# --------------------------------------------------------------------------- #
def detect_communities(G: nx.Graph, seed: int = 42) -> list[set[str]]:
    """Louvain algoritması (ağırlıklı)."""
    comms = nx.community.louvain_communities(G, weight="weight", seed=seed)
    return sorted(comms, key=len, reverse=True)


def modularity(G: nx.Graph, communities: list[set[str]]) -> float:
    return nx.community.modularity(G, communities, weight="weight")


def house_partition(G: nx.Graph) -> list[set[str]]:
    groups: dict[str, set[str]] = {}
    for n, h in G.nodes(data="house"):
        groups.setdefault(h, set()).add(n)
    return list(groups.values())


def normalized_mutual_information(a: list[set[str]], b: list[set[str]]) -> float:
    """İki bölümleme arasındaki NMI (0: ilişkisiz, 1: özdeş)."""
    label_a = {n: i for i, grp in enumerate(a) for n in grp}
    label_b = {n: i for i, grp in enumerate(b) for n in grp}
    nodes = list(label_a)
    n = len(nodes)
    ca = Counter(label_a[x] for x in nodes)
    cb = Counter(label_b[x] for x in nodes)
    joint = Counter((label_a[x], label_b[x]) for x in nodes)
    mi = sum(c / n * math.log((c / n) / ((ca[i] / n) * (cb[j] / n))) for (i, j), c in joint.items())
    ha = -sum(c / n * math.log(c / n) for c in ca.values())
    hb = -sum(c / n * math.log(c / n) for c in cb.values())
    return 0.0 if ha == 0 or hb == 0 else 2 * mi / (ha + hb)


# --------------------------------------------------------------------------- #
# Dayanıklılık (robustness)
# --------------------------------------------------------------------------- #
def _lcc_fraction(G: nx.Graph, n_total: int) -> float:
    if G.number_of_nodes() == 0:
        return 0.0
    return len(max(nx.connected_components(G), key=len)) / n_total


def robustness_curve(
    G: nx.Graph, strategy: str = "degree", trials: int = 200, seed: int = 42
) -> pd.DataFrame:
    """Düğümler tek tek silinirken en büyük bileşenin oranı.

    ``strategy``: ``"degree"`` (en yüksek dereceden başla, hedefli saldırı),
    ``"betweenness"`` (başlangıç betweenness sırasına göre) veya ``"random"``
    (``trials`` denemenin ortalaması).
    """
    n = G.number_of_nodes()

    def run(order: list[str]) -> list[float]:
        H = G.copy()
        out = [_lcc_fraction(H, n)]
        for node in order:
            H.remove_node(node)
            out.append(_lcc_fraction(H, n))
        return out

    if strategy == "degree":
        order = sorted(G, key=lambda x: (-G.degree(x), x))
        y = run(order)
    elif strategy == "betweenness":
        bc = nx.betweenness_centrality(G)
        order = sorted(G, key=lambda x: (-bc[x], x))
        y = run(order)
    elif strategy == "random":
        rng = np.random.default_rng(seed)
        nodes = list(G)
        y = np.mean([run(list(rng.permutation(nodes))) for _ in range(trials)], axis=0).tolist()
    else:
        raise ValueError(f"Bilinmeyen strateji: {strategy}")
    return pd.DataFrame({"removed": range(len(y)), "lcc_fraction": y, "strategy": strategy})


# --------------------------------------------------------------------------- #
# Rastgele graf karşılaştırması / small-world
# --------------------------------------------------------------------------- #
def small_world_analysis(G: nx.Graph, n_random: int = 100, seed: int = 42) -> dict:
    """Ağı aynı düğüm/kenar sayılı Erdős–Rényi grafları ile karşılaştırır.

    sigma = (C / C_rand) / (L / L_rand); sigma > 1 ise small-world eğilimi vardır.
    """
    main = largest_component(G)
    n, m = main.number_of_nodes(), main.number_of_edges()
    C, L = nx.average_clustering(main), nx.average_shortest_path_length(main)

    rng = np.random.default_rng(seed)
    c_r, l_r = [], []
    while len(c_r) < n_random:
        R = nx.gnm_random_graph(n, m, seed=int(rng.integers(1 << 31)))
        if not nx.is_connected(R):
            continue
        c_r.append(nx.average_clustering(R))
        l_r.append(nx.average_shortest_path_length(R))
    c_rand, l_rand = float(np.mean(c_r)), float(np.mean(l_r))
    return {
        "C": C,
        "L": L,
        "C_random": c_rand,
        "L_random": l_rand,
        "sigma": (C / c_rand) / (L / l_rand),
    }


def degree_distribution(G: nx.Graph) -> pd.Series:
    return pd.Series([d for _, d in G.degree()]).value_counts().sort_index()


# --------------------------------------------------------------------------- #
# İşaretli (signed) ağ: yapısal denge
# --------------------------------------------------------------------------- #
def structural_balance(G_full: nx.Graph) -> dict:
    """Heider'in yapısal denge teorisi: üçgenlerin işaret çarpımı.

    Dost (friend/family/ally) = +1, düşman (enemy) = -1. Bir üçgen,
    işaretlerin çarpımı pozitifse dengelidir ("dostumun dostu dostumdur",
    "düşmanımın düşmanı dostumdur").
    """
    sign = {
        frozenset(e[:2]): (-1 if e[2]["relation"] == "enemy" else 1)
        for e in G_full.edges(data=True)
    }
    balanced = unbalanced = 0
    unbalanced_list = []
    for tri in (t for t in itertools.combinations(G_full.nodes, 3)):
        a, b, c = tri
        if G_full.has_edge(a, b) and G_full.has_edge(b, c) and G_full.has_edge(a, c):
            prod = sign[frozenset((a, b))] * sign[frozenset((b, c))] * sign[frozenset((a, c))]
            if prod > 0:
                balanced += 1
            else:
                unbalanced += 1
                unbalanced_list.append(tri)
    total = balanced + unbalanced
    return {
        "triangles": total,
        "balanced": balanced,
        "unbalanced": unbalanced,
        "balance_ratio": balanced / total if total else float("nan"),
        "unbalanced_triangles": unbalanced_list,
    }


def relation_counts(G: nx.Graph) -> dict[str, int]:
    return dict(Counter(d["relation"] for _, _, d in G.edges(data=True)))
