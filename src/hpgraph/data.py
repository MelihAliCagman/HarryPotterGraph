"""Veri yükleme, doğrulama ve graf oluşturma.

Veri iki CSV dosyasından okunur:

* ``data/characters.csv``     -> ``name, house``
* ``data/relationships.csv``  -> ``source, target, relation, weight``

``relation`` değerleri:

* ``friend`` : arkadaşlık
* ``family`` : aile bağı (kan bağı, evlilik, vasi vb.)
* ``ally``   : müttefik / mentor / iş birliği (Order, Ölüm Yiyenler, Hogwarts kadrosu)
* ``enemy``  : düşmanlık

``weight`` 1-3 arası, ilişkinin yoğunluğuna dair **öznel** bir puandır
(1: sınırlı etkileşim, 3: hikâyenin merkezindeki ilişki).
"""
from __future__ import annotations

from pathlib import Path

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

POSITIVE_RELATIONS = ("friend", "family", "ally")
NEGATIVE_RELATIONS = ("enemy",)
ALL_RELATIONS = POSITIVE_RELATIONS + NEGATIVE_RELATIONS
VALID_WEIGHTS = (1, 2, 3)

HOUSES = ("Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Bilinmiyor")


class DataValidationError(ValueError):
    """Veri dosyalarında tutarsızlık bulunduğunda fırlatılır."""


def load_characters(path: Path | None = None) -> pd.DataFrame:
    return pd.read_csv(path or DATA_DIR / "characters.csv", encoding="utf-8")


def load_relationships(path: Path | None = None) -> pd.DataFrame:
    return pd.read_csv(path or DATA_DIR / "relationships.csv", encoding="utf-8")


def validate(characters: pd.DataFrame, relationships: pd.DataFrame) -> None:
    """Veri tutarlılığını denetler; sorun varsa tüm hataları tek mesajda bildirir."""
    errors: list[str] = []

    dup_names = characters[characters["name"].duplicated()]["name"].tolist()
    if dup_names:
        errors.append(f"Yinelenen karakter: {dup_names}")

    bad_houses = sorted(set(characters["house"]) - set(HOUSES))
    if bad_houses:
        errors.append(f"Geçersiz ev adı: {bad_houses}")

    names = set(characters["name"])
    unknown = sorted((set(relationships["source"]) | set(relationships["target"])) - names)
    if unknown:
        errors.append(f"Karakter listesinde olmayan düğüm: {unknown}")

    self_loops = relationships[relationships["source"] == relationships["target"]]
    if not self_loops.empty:
        errors.append(f"Kendine bağlanan kenar: {self_loops['source'].tolist()}")

    bad_rel = sorted(set(relationships["relation"]) - set(ALL_RELATIONS))
    if bad_rel:
        errors.append(f"Geçersiz ilişki türü: {bad_rel}")

    bad_w = relationships[~relationships["weight"].isin(VALID_WEIGHTS)]
    if not bad_w.empty:
        errors.append(f"Geçersiz ağırlık (1-3 olmalı): {bad_w.index.tolist()}")

    pairs = relationships.apply(lambda r: frozenset((r["source"], r["target"])), axis=1)
    dup_pairs = relationships[pairs.duplicated(keep=False)]
    if not dup_pairs.empty:
        shown = sorted({tuple(sorted(p)) for p in pairs[dup_pairs.index]})
        errors.append(f"Yinelenen ilişki çifti: {shown}")

    if errors:
        raise DataValidationError("\n".join(errors))


def build_graph(relations: tuple[str, ...] = ALL_RELATIONS) -> nx.Graph:
    """Yönsüz, ağırlıklı graf döndürür.

    ``relations`` ile yalnızca belirli ilişki türleri dahil edilebilir. Tüm
    karakterler (bağlantısız kalsa bile) düğüm olarak eklenir.
    """
    characters = load_characters()
    relationships = load_relationships()
    validate(characters, relationships)

    G = nx.Graph()
    for row in characters.itertuples(index=False):
        G.add_node(row.name, house=row.house)
    for row in relationships.itertuples(index=False):
        if row.relation in relations:
            G.add_edge(row.source, row.target, relation=row.relation, weight=int(row.weight))
    return G


def build_positive_graph() -> nx.Graph:
    """Yalnızca dostça ilişkiler (friend, family, ally)."""
    return build_graph(POSITIVE_RELATIONS)


def largest_component(G: nx.Graph) -> nx.Graph:
    nodes = max(nx.connected_components(G), key=len)
    return G.subgraph(nodes).copy()
