"""Tüm analizleri çalıştırır; grafikleri ``docs/images`` ve sayısal çıktıları
``results/`` klasörüne yazar.

Kullanım:  python scripts/run_analysis.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # başsız çalışma (CI) için; hpgraph.plots içe aktarılmadan önce

from hpgraph import build_graph, build_positive_graph
from hpgraph import metrics as M
from hpgraph import plots as P

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "docs" / "images"
RES = ROOT / "results"


def main() -> dict:
    RES.mkdir(exist_ok=True)
    G = build_graph()
    Gp = build_positive_graph()
    pos = P.compute_layout(G)

    summary = M.network_summary(G)
    table = M.centrality_table(G)
    table_pos = M.centrality_table(Gp)
    corr = M.centrality_correlation(table)
    cut_nodes, bridges = M.cut_vertices_and_bridges(G)
    house_matrix = M.house_connection_matrix(G)
    assort = M.house_assortativity(Gp)
    assort_p = M.house_assortativity_pvalue(Gp)
    # Topluluk ve ev analizi yalnızca dostça ilişkilerle (Gp) yapılır: düşmanlık kenarları
    # iki düğümü "aynı topluluğa" çekmemeli.
    comms = M.detect_communities(Gp)
    comm_q = M.modularity(Gp, comms)
    house_q = M.modularity(Gp, M.house_partition(Gp))
    nmi = M.normalized_mutual_information(comms, M.house_partition(Gp))
    sw = M.small_world_analysis(G)
    balance = M.structural_balance(G)
    curves = [M.robustness_curve(G, s) for s in ("degree", "betweenness", "random")]

    # ---- Grafikler ------------------------------------------------------- #
    deg_c = table["degree_centrality"].to_dict()
    P.save(P.plot_network(G, pos, {n: 200 + 6000 * deg_c[n] for n in G},
                          "Harry Potter Sosyal Ağı (renk: ev, boyut: degree centrality)"),
           IMG / "sosyal-ag-grafigi.png")
    P.save(P.plot_network(G, pos, {n: 200 + 6000 * deg_c[n] for n in G},
                          "İlişki Türlerine Göre Ağ (kesikli kırmızı: düşmanlık)",
                          show_relations=True), IMG / "iliski-turleri.png")
    P.save(P.plot_top_bars(table, "degree_centrality", "Degree Centrality - İlk 10"),
           IMG / "degree-centrality.png")
    P.save(P.plot_top_bars(table, "closeness", "Closeness Centrality - İlk 10"),
           IMG / "closeness-centrality.png")
    P.save(P.plot_top_bars(table, "betweenness", "Betweenness Centrality - İlk 10"),
           IMG / "betweenness-centrality.png")
    P.save(P.plot_top_bars(table, "eigenvector", "Eigenvector Centrality - İlk 10"),
           IMG / "eigenvector-centrality.png")
    P.save(P.plot_centrality_panel(table), IMG / "merkezilik-paneli.png")
    P.save(P.plot_house_heatmap(house_matrix), IMG / "evler-arasi-baglanti.png")
    P.save(P.plot_degree_distribution(G), IMG / "derece-dagilimi.png")
    P.save(P.plot_communities(Gp, comms, pos), IMG / "topluluklar.png")
    P.save(P.plot_robustness(curves), IMG / "dayaniklilik.png")
    P.save(P.plot_correlation(corr), IMG / "metrik-korelasyonu.png")

    # ---- Sayısal çıktılar -------------------------------------------------- #
    table.round(4).to_csv(RES / "centrality_metrics.csv", encoding="utf-8")

    result = {
        "summary": summary,
        "relation_counts": M.relation_counts(G),
        "top": {c: M.top_n(table, c) for c in
                ("degree", "closeness", "betweenness", "eigenvector", "pagerank")},
        "top_positive_only": {c: M.top_n(table_pos, c) for c in ("degree", "betweenness")},
        "positive_graph": M.network_summary(Gp) | {"isolated": M.network_summary(Gp)["isolated"]},
        "articulation_points": cut_nodes,
        "bridges": [list(b) for b in bridges],
        "house_matrix": house_matrix.to_dict(),
        "house_assortativity": assort,
        "house_assortativity_p": assort_p,
        "communities": [sorted(c) for c in comms],
        "modularity_louvain": comm_q,
        "modularity_houses": house_q,
        "nmi_communities_vs_houses": nmi,
        "small_world": sw,
        "structural_balance": {k: v for k, v in balance.items() if k != "unbalanced_triangles"}
        | {"unbalanced_triangles": [list(t) for t in balance["unbalanced_triangles"]]},
        "robustness": {df["strategy"].iloc[0]: df["lcc_fraction"].round(4).tolist() for df in curves},
        "correlation": corr.round(3).to_dict(),
    }
    (RES / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=float), encoding="utf-8"
    )
    return result


if __name__ == "__main__":
    r = main()
    s = r["summary"]
    print(f"Düğüm: {s['nodes']}  Kenar: {s['edges']}  Yoğunluk: {s['density']:.3f}  "
          f"Bileşen: {s['components']}  Çap: {s['diameter']}")
    for k, v in r["top"].items():
        print(k, [(n, round(x, 3)) for n, x in v])
    print("Kesim noktaları:", r["articulation_points"])
    print("Köprüler:", r["bridges"])
    print("Assortativity:", round(r["house_assortativity"], 3), "p =", round(r["house_assortativity_p"], 4))
    print("Louvain Q:", round(r["modularity_louvain"], 3), " Ev Q:", round(r["modularity_houses"], 3),
          " NMI:", round(r["nmi_communities_vs_houses"], 3))
    print("Small-world:", {k: round(v, 3) for k, v in r["small_world"].items()})
    sb = r["structural_balance"]
    print("Denge:", sb["triangles"], sb["balanced"], sb["unbalanced"], round(sb["balance_ratio"], 3))
    print("Pozitif graf:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r["positive_graph"].items()})

