import math

import networkx as nx
import pytest

from hpgraph import build_graph, build_positive_graph
from hpgraph import metrics as M


@pytest.fixture(scope="module")
def G():
    return build_graph()


def _star():
    G = nx.star_graph(4)  # 0 merkez, 1-4 yaprak
    nx.set_node_attributes(G, {n: "Gryffindor" for n in G}, "house")
    nx.set_edge_attributes(G, "friend", "relation")
    nx.set_edge_attributes(G, 1, "weight")
    return G


def test_summary_matches_networkx(G):
    s = M.network_summary(G)
    assert s["nodes"] == G.number_of_nodes()
    assert s["edges"] == G.number_of_edges()
    assert s["density"] == pytest.approx(nx.density(G))
    assert s["components"] == 1


def test_star_centrality_hand_computed():
    t = M.centrality_table(_star())
    assert t.loc[0, "degree"] == 4
    assert t.loc[0, "degree_centrality"] == pytest.approx(1.0)
    assert t.loc[0, "betweenness"] == pytest.approx(1.0)  # tüm yaprak çiftleri merkezden geçer
    assert t.loc[1, "betweenness"] == pytest.approx(0.0)
    assert t.loc[0, "closeness"] == pytest.approx(1.0)


def test_harry_is_most_central(G):
    t = M.centrality_table(G)
    for col in ("degree", "closeness", "betweenness", "eigenvector", "pagerank"):
        assert t[col].idxmax() == "Harry"


def test_house_matrix_sums_to_edge_count(G):
    m = M.house_connection_matrix(G)
    diag = sum(m.values[i, i] for i in range(len(m)))
    off = (m.values.sum() - diag) / 2
    assert diag + off == G.number_of_edges()


def test_nmi_identical_and_independent():
    a = [{"a", "b"}, {"c", "d"}]
    assert M.normalized_mutual_information(a, a) == pytest.approx(1.0)
    b = [{"a", "c"}, {"b", "d"}]
    assert M.normalized_mutual_information(a, b) == pytest.approx(0.0, abs=1e-12)


def test_communities_cover_all_nodes_once():
    Gp = build_positive_graph()
    comms = M.detect_communities(Gp)
    assert sorted(n for c in comms for n in c) == sorted(Gp.nodes)
    assert M.modularity(Gp, comms) > M.modularity(Gp, M.house_partition(Gp))


def test_structural_balance_on_known_triangles():
    G = nx.Graph()
    G.add_edge("a", "b", relation="friend")
    G.add_edge("b", "c", relation="friend")
    G.add_edge("a", "c", relation="friend")  # +++ dengeli
    G.add_edge("c", "d", relation="enemy")
    G.add_edge("b", "d", relation="enemy")  # b-c-d: + - - dengeli
    G.add_edge("a", "d", relation="friend")  # a-c-d: + - + dengesiz; a-b-d: + - + dengesiz
    r = M.structural_balance(G)
    assert r["triangles"] == 4
    assert r["balanced"] == 2 and r["unbalanced"] == 2
    assert r["balance_ratio"] == pytest.approx(0.5)


def test_robustness_curve_monotone_and_bounds(G):
    for strategy in ("degree", "betweenness"):
        c = M.robustness_curve(G, strategy)
        assert c["lcc_fraction"].iloc[0] == 1.0 and c["lcc_fraction"].iloc[-1] == 0.0
        assert c["lcc_fraction"].is_monotonic_decreasing
    with pytest.raises(ValueError):
        M.robustness_curve(G, "bogus")


def test_targeted_attack_is_worse_than_random(G):
    deg = M.robustness_curve(G, "degree")["lcc_fraction"].sum()
    rnd = M.robustness_curve(G, "random", trials=50)["lcc_fraction"].sum()
    assert deg < rnd


def test_cut_vertices_known(G):
    cuts, bridges = M.cut_vertices_and_bridges(G)
    assert "Harry" in cuts and "Dumbledore" in cuts
    assert ("Filius Flitwick", "Pomona Sprout") in bridges


def test_small_world_sigma_greater_than_one(G):
    sw = M.small_world_analysis(G, n_random=30)
    assert sw["sigma"] > 1 and not math.isnan(sw["sigma"])


def test_assortativity_significant():
    Gp = build_positive_graph()
    assert M.house_assortativity(Gp) > 0
    assert M.house_assortativity_pvalue(Gp, n_perm=200) < 0.05
