import pandas as pd
import pytest

from hpgraph import data


def test_real_data_is_valid():
    data.validate(data.load_characters(), data.load_relationships())


def test_graph_has_no_isolated_nodes_and_is_connected():
    G = data.build_graph()
    assert all(G.degree(n) > 0 for n in G)
    import networkx as nx

    assert nx.is_connected(G)


def test_lupin_is_single_node():
    """Eski sürümde 'Lupin' ve 'Remus Lupin' ayrı düğümlerdi (aynı karakter)."""
    G = data.build_graph()
    assert "Remus Lupin" in G
    assert "Lupin" not in G


def test_every_node_has_house_and_edges_have_attributes():
    G = data.build_graph()
    assert all(h in data.HOUSES for _, h in G.nodes(data="house"))
    for _, _, d in G.edges(data=True):
        assert d["relation"] in data.ALL_RELATIONS
        assert d["weight"] in data.VALID_WEIGHTS


def test_positive_graph_excludes_enemies():
    Gp = data.build_positive_graph()
    assert all(d["relation"] != "enemy" for _, _, d in Gp.edges(data=True))
    assert not Gp.has_edge("Harry", "Voldemort")


def _chars():
    return pd.DataFrame({"name": ["A", "B"], "house": ["Gryffindor", "Slytherin"]})


def _rels(rows):
    return pd.DataFrame(rows, columns=["source", "target", "relation", "weight"])


@pytest.mark.parametrize(
    "rows, fragment",
    [
        ([("A", "C", "friend", 1)], "olmayan düğüm"),
        ([("A", "A", "friend", 1)], "Kendine"),
        ([("A", "B", "lover", 1)], "ilişki türü"),
        ([("A", "B", "friend", 9)], "ağırlık"),
        ([("A", "B", "friend", 1), ("B", "A", "enemy", 1)], "Yinelenen ilişki"),
    ],
)
def test_validate_rejects_bad_data(rows, fragment):
    with pytest.raises(data.DataValidationError, match=fragment):
        data.validate(_chars(), _rels(rows))


def test_validate_rejects_duplicate_character_and_bad_house():
    chars = pd.DataFrame({"name": ["A", "A"], "house": ["Gryffindor", "Pufpuf"]})
    with pytest.raises(data.DataValidationError) as e:
        data.validate(chars, _rels([("A", "A", "friend", 1)]))
    assert "Yinelenen karakter" in str(e.value) and "Geçersiz ev" in str(e.value)
