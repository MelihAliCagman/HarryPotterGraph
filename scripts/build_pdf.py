"""Mülakat hazırlık rehberi PDF'ini üretir: docs/Proje_Mulakat_Rehberi.pdf

Sayısal değerler ``results/summary.json`` dosyasından okunur (önce
``python scripts/run_analysis.py`` çalıştırılmalıdır). Gereksinim: reportlab.
Windows'ta Arial/Consolas yazı tipleri kullanılır (Türkçe karakter desteği için).
"""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path("C:/Windows/Fonts")
OUT = ROOT / "docs" / "Proje_Mulakat_Rehberi.pdf"
IMG = ROOT / "docs" / "images"
R = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))

pdfmetrics.registerFont(TTFont("Arial", FONTS / "arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FONTS / "arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FONTS / "ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", FONTS / "arialbi.ttf"))
pdfmetrics.registerFont(TTFont("Consolas", FONTS / "consola.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                              italic="Arial-Italic", boldItalic="Arial-BoldItalic")

PURPLE = colors.HexColor("#4A235A")
LIGHT = colors.HexColor("#F4ECF7")
ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="Arial", fontSize=10, leading=14.5,
                      alignment=TA_JUSTIFY, spaceAfter=5)
H1 = ParagraphStyle("h1", parent=BODY, fontName="Arial-Bold", fontSize=16, leading=20, textColor=PURPLE,
                    spaceBefore=6, spaceAfter=8, alignment=0)
H2 = ParagraphStyle("h2", parent=BODY, fontName="Arial-Bold", fontSize=12, leading=16, textColor=PURPLE,
                    spaceBefore=8, spaceAfter=4, alignment=0)
Q = ParagraphStyle("q", parent=BODY, fontName="Arial-Bold", textColor=PURPLE, spaceBefore=6,
                   spaceAfter=2, alignment=0)
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=14, bulletIndent=3, spaceAfter=2)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8.5, leading=11, alignment=0, spaceAfter=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Arial-Bold", textColor=colors.white)
CODE = ParagraphStyle("code", fontName="Consolas", fontSize=7.8, leading=10.2, backColor=LIGHT,
                      borderPadding=5, leftIndent=4, spaceBefore=4, spaceAfter=8)
NOTE = ParagraphStyle("note", parent=BODY, backColor=colors.HexColor("#FEF9E7"), borderPadding=6,
                      borderColor=colors.HexColor("#F1C40F"), borderWidth=0.6, spaceBefore=6, spaceAfter=10)

story: list = []


def h1(t): story.append(Paragraph(t, H1))
def h2(t): story.append(Paragraph(t, H2))
def p(t): story.append(Paragraph(t, BODY))
def note(t): story.append(Paragraph(t, NOTE))
def bullets(items):
    for it in items:
        story.append(Paragraph(it, BUL, bulletText="•"))
    story.append(Spacer(1, 4))
def code(t): story.append(Preformatted(t.strip("\n"), CODE))
def qa(q, a):
    story.append(KeepTogether([Paragraph(q, Q), Paragraph(a, BODY)]))
def img(name, width=15 * cm):
    from PIL import Image as PI
    w, h = PI.open(IMG / name).size
    story.append(Image(str(IMG / name), width=width, height=width * h / w))
    story.append(Spacer(1, 6))
def table(rows, widths, header=True):
    data = [[Paragraph(str(c), CELLB if (header and i == 0) else CELL) for c in row]
            for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BFC9CA")),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT])]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), PURPLE))
    t.setStyle(TableStyle(st))
    story.append(t)
    story.append(Spacer(1, 8))


S = R["summary"]
top = R["top"]
sw = R["small_world"]
sb = R["structural_balance"]
rob = R["robustness"]
fmt = lambda lst: ", ".join(f"{n} ({v:.3f})" if isinstance(v, float) and v < 1 else f"{n} ({v})" for n, v in lst)

# ============================ KAPAK ============================ #
story.append(Spacer(1, 4 * cm))
story.append(Paragraph("Harry Potter Sosyal Ağ Analizi", ParagraphStyle(
    "t", parent=H1, fontSize=28, leading=34, alignment=1)))
story.append(Paragraph("Proje ve Kod Rehberi · Mülakat Hazırlık Dokümanı", ParagraphStyle(
    "s", parent=BODY, fontSize=14, alignment=1, textColor=colors.grey)))
story.append(Spacer(1, 1 * cm))
img("sosyal-ag-grafigi.png", 14 * cm)
story.append(Spacer(1, 1 * cm))
story.append(Paragraph("Graf teorisi · Merkezilik · Topluluk tespiti · Dayanıklılık · Small-world · Yapısal denge",
                       ParagraphStyle("k", parent=BODY, alignment=1)))
story.append(Paragraph("Python · NetworkX · pandas · Matplotlib · pytest", ParagraphStyle(
    "k2", parent=BODY, alignment=1, textColor=colors.grey)))
story.append(PageBreak())

# ============================ 1. ÖZET ============================ #
h1("1. Projeyi 30 saniyede anlatmak")
note("<b>Kısa anlatım:</b> \"Harry Potter dünyasındaki 43 karakteri düğüm, aralarındaki arkadaşlık, aile, "
     "müttefiklik ve düşmanlık ilişkilerini kenar olarak modelleyen bir sosyal ağ analizi yaptım. "
     "Ağda kimin merkezi olduğunu, evlerin gerçekten kümelenip kümelenmediğini, ağın kritik karakterler "
     "çıkarılınca ne kadar dayandığını ve dostluk/düşmanlık ilişkilerinin yapısal olarak tutarlı olup olmadığını "
     "inceledim. Kod, veriyi CSV'den okuyan, doğrulayan ve analizleri test edilmiş bir Python paketi olarak "
     "yeniden yapılandırıldı.\"")
h2("Tek bakışta")
table([
    ["Konu", "Değer"],
    ["Ağ boyutu", f"{S['nodes']} düğüm, {S['edges']} kenar, {S['components']} bağlı bileşen"],
    ["İlişki türleri", ", ".join(f"{k}: {v}" for k, v in R["relation_counts"].items())],
    ["Yoğunluk / çap", f"{S['density']:.3f} / {S['diameter']}"],
    ["Ort. kümelenme", f"{S['avg_clustering']:.3f}"],
    ["En merkezi karakter", "Harry (tüm merkezilik ölçülerinde), ardından Dumbledore"],
    ["Kod", "src/hpgraph (data, metrics, plots), scripts, tests (23 test), notebook, CI"],
], [4 * cm, 12.5 * cm])
h2("Ana bulgular")
bullets([
    f"<b>Merkezilik:</b> Harry degree {top['degree'][0][1]}, betweenness {top['betweenness'][0][1]:.3f}. "
    "Veri Harry merkezli derlendiği için bu kısmen örneklem yanlılığıdır.",
    f"<b>Evler:</b> assortativity r = {R['house_assortativity']:.3f} (permütasyon testi p = "
    f"{R['house_assortativity_p']:.4f}). Evler kümeleniyor ama Louvain toplulukları (modularity "
    f"{R['modularity_louvain']:.3f}) evlerden (modularity {R['modularity_houses']:.3f}) daha iyi bir bölümleme veriyor.",
    f"<b>Small-world:</b> σ = {sw['sigma']:.2f}. Kümelenme {sw['C']:.3f} (rastgele {sw['C_random']:.3f}), "
    f"ortalama yol {sw['L']:.2f} (rastgele {sw['L_random']:.2f}).",
    f"<b>Dayanıklılık:</b> 5 düğüm silinince en büyük bileşen hedefli saldırıda %{rob['degree'][5]*100:.0f}, "
    f"rastgelede %{rob['random'][5]*100:.0f}. Kesim noktaları: {', '.join(R['articulation_points'])}.",
    f"<b>Yapısal denge:</b> {sb['triangles']} üçgenin {sb['balanced']}'i dengeli "
    f"(%{sb['balance_ratio']*100:.1f}).",
])


# ============================ 2. PROBLEM ============================ #
h1("2. Problem tanımı ve motivasyon")
p("Sosyal ağ analizi, aktörlerin (kişiler, karakterler) ve aralarındaki ilişkilerin graf olarak modellenip "
  "yapısal özelliklerinin incelenmesidir. Bu proje, Ayrık Matematik dersindeki graf teorisi kavramlarını "
  "(derece, yol, bağlantılılık, kümelenme) gerçek bir probleme uygular. Harry Potter evreni; tanıdık, "
  "yorumlanabilir ve hem dostluk hem düşmanlık içeren zengin bir ilişki yapısı sunduğu için seçilmiştir. "
  "Yorumlanabilirlik önemlidir: Snape'in neden köprü olduğunu hikâyeden bilerek sonucu doğrulayabiliriz.")
h2("Araştırma soruları")
bullets([
    "<b>S1.</b> Ağın merkezinde kim var, bilgiyi/ilişkiyi köprüleyen karakterler kimler?",
    "<b>S2.</b> Hogwarts evleri sosyal olarak kümeleniyor mu, yoksa topluluklar evlerden bağımsız mı?",
    "<b>S3.</b> Ağ ne kadar dayanıklı; kritik karakterler çıkarılınca ne olur?",
    "<b>S4.</b> Ağ small-world mü (kısa yollar + yüksek kümelenme)?",
    "<b>S5.</b> Dostluk/düşmanlık ilişkileri yapısal olarak tutarlı mı (Heider dengesi)?",
])

# ============================ 3. TEORİ ============================ #
h1("3. Graf teorisi temelleri")
p("Bir graf G = (V, E) düğüm kümesi V ve kenar kümesi E'den oluşur. Burada |V| = n = 43 karakter, "
  "|E| = m = 142 ilişkidir. Graf <b>yönsüz</b>dür (arkadaşlık karşılıklıdır), kenarlar bir ilişki türü ve "
  "1-3 arası bir ağırlık taşır.")
table([
    ["Kavram", "Tanım", "Bu projedeki karşılığı"],
    ["Derece (degree)", "Bir düğüme bağlı kenar sayısı. Ortalama derece = 2m/n.",
     f"Harry 31; ortalama {S['avg_degree']:.2f}"],
    ["Yol / en kısa yol", "İki düğümü birleştiren kenar dizisi; en kısa olanın uzunluğu d(u,v).",
     f"Ortalama en kısa yol {S['avg_shortest_path']:.2f}"],
    ["Bağlı bileşen", "Aralarında yol bulunan düğümlerin maksimal kümesi.", "Tek bileşen (43 düğümün hepsi)"],
    ["Yoğunluk", "m / (n(n-1)/2): olası kenarların kaçı var?", f"{S['density']:.3f}"],
    ["Çap / yarıçap", "En büyük / en küçük eksantriklik (bir düğümün en uzak düğüme mesafesi).",
     f"{S['diameter']} / {S['radius']}"],
    ["Kümelenme katsayısı", "Bir düğümün komşularının birbirine bağlı olma oranı: C(v) = 2T(v) / (k(k-1)).",
     f"Ortalama {S['avg_clustering']:.3f}"],
    ["Geçişlilik", "3 × üçgen sayısı / bağlı üçlü sayısı (global kümelenme).", f"{S['transitivity']:.3f}"],
    ["Kesim noktası", "Çıkarılınca bileşen sayısını artıran düğüm.", ", ".join(R["articulation_points"])],
    ["Köprü", "Çıkarılınca bileşen sayısını artıran kenar.",
     "; ".join(f"{a}–{b}" for a, b in R["bridges"])],
    ["k-core", "Her düğümün en az k derecesi olduğu maksimal alt graf.", "core_number sütunu"],
], [3.3 * cm, 7.4 * cm, 5.8 * cm])

# ============================ 4. VERİ ============================ #
h1("4. Veri modeli")
p("Veri iki CSV dosyasındadır. Bu ayrım, veriyi koddan bağımsız hale getirir: yeni karakter eklemek için kod "
  "değil CSV değişir.")
code("""
data/characters.csv        name, house
data/relationships.csv     source, target, relation, weight
                           relation in {friend, family, ally, enemy}
                           weight   in {1, 2, 3}   # öznel ilişki yoğunluğu
""")
p("<b>Doğrulama</b> (data.validate) şu hataları yakalar ve hepsini tek mesajda bildirir: yinelenen karakter, "
  "geçersiz ev adı, karakter listesinde olmayan düğüm, kendine bağlanan kenar, geçersiz ilişki türü veya "
  "ağırlık, yinelenen ilişki çifti (A–B ile B–A aynı kenardır).")
note("<b>Veri güvenilirliği:</b> Veri filmlerden/kitaplardan elle derlenmiş ve öznel bir listedir. Ağırlıklar "
     "ölçülmüş değerler (ör. birlikte geçen sahne sayısı) değil, 1-3 arası yorumdur. Mülakatta bunu açıkça "
     "söylemek bir zayıflık değil, bilimsel dürüstlüktür.")

# ============================ 5. KOD ============================ #
h1("5. Kod mimarisi")
table([
    ["Dosya", "Sorumluluk"],
    ["src/hpgraph/data.py", "CSV okuma, doğrulama, build_graph (tüm ilişkiler) ve build_positive_graph (düşmansız)"],
    ["src/hpgraph/metrics.py", "Tüm analizler: özet, merkezilik, topluluk, dayanıklılık, small-world, denge"],
    ["src/hpgraph/plots.py", "Yalnızca çizim; Figure döndürür, hesap yapmaz"],
    ["scripts/run_analysis.py", "Hepsini çalıştırır; docs/images ve results/ üretir"],
    ["scripts/build_pdf.py", "Bu dokümanı results/summary.json'dan üretir"],
    ["notebooks/HarryPotter.ipynb", "Anlatım katmanı; hesapları pakete bırakır"],
    ["tests/", "23 pytest testi: veri doğrulama + metriklerin elle hesaplanmış doğrulukları"],
    [".github/workflows/ci.yml", "Her push'ta test ve analiz çalıştırır"],
], [5.2 * cm, 11.3 * cm])
p("<b>Tasarım ilkesi:</b> hesap (metrics) ile görselleştirme (plots) ve veri (data) ayrıdır. Böylece her "
  "katman bağımsız test edilebilir ve notebook yalnızca bir arayüzdür.")

h2("5.1 Graf oluşturma")
code("""
def build_graph(relations=ALL_RELATIONS) -> nx.Graph:
    characters = load_characters()
    relationships = load_relationships()
    validate(characters, relationships)          # hatalı veri burada durur

    G = nx.Graph()
    for row in characters.itertuples(index=False):
        G.add_node(row.name, house=row.house)    # bağlantısız olsa da düğüm eklenir
    for row in relationships.itertuples(index=False):
        if row.relation in relations:            # türe göre filtre (ör. sadece dostça)
            G.add_edge(row.source, row.target,
                       relation=row.relation, weight=int(row.weight))
    return G
""")
p("nx.Graph yönsüz graftır; aynı çifti iki kez eklemek kenarı tekilleştirir. v1'deki Harry–Luna "
  "tekrarı sonucu bozmuyordu ama validate artık böyle yinelemeleri hata olarak raporlar.")

h2("5.2 Merkezilik tablosu")
code("""
def centrality_table(G):
    table = pd.DataFrame({
        "degree":      dict(G.degree()),
        "strength":    dict(G.degree(weight="weight")),   # ağırlıklı derece
        "closeness":   nx.closeness_centrality(G),
        "betweenness": nx.betweenness_centrality(G),
        "eigenvector": nx.eigenvector_centrality_numpy(G),
        "pagerank":    nx.pagerank(G, weight="weight"),
        "core_number": nx.core_number(G), ...
    })
    return table.sort_values("degree", ascending=False)
""")

h2("5.3 Yapısal denge (Heider)")
code("""
sign = {frozenset(e[:2]): (-1 if e[2]["relation"] == "enemy" else 1)
        for e in G_full.edges(data=True)}
for a, b, c in itertools.combinations(G_full.nodes, 3):
    if G.has_edge(a,b) and G.has_edge(b,c) and G.has_edge(a,c):
        prod = sign[{a,b}] * sign[{b,c}] * sign[{a,c}]
        balanced += prod > 0      # çarpım pozitifse üçgen dengelidir
""")

h2("5.4 Dayanıklılık simülasyonu")
code("""
order = sorted(G, key=lambda x: (-G.degree(x), x))   # hedefli: yüksek dereceden başla
H = G.copy()
for node in order:
    H.remove_node(node)
    lcc = len(max(nx.connected_components(H), key=len)) / n_total
""")
p("Rastgele senaryoda 200 farklı rastgele sıra denenir ve ortalaması alınır; böylece tek bir şanslı/şanssız "
  "sıraya bağlı kalınmaz. Tüm rastgele işlemler seed ile sabitlenmiştir (tekrarlanabilirlik).")


# ============================ 6. METRİKLER ============================ #
h1("6. Merkezilik metrikleri: formül, sezgi, sonuç")
table([
    ["Metrik", "Formül", "Sorduğu soru", "İlk 5"],
    ["Degree", "C<sub>D</sub>(v) = deg(v) / (n-1)", "Kaç doğrudan bağlantısı var?", fmt(top["degree"])],
    ["Closeness", "C<sub>C</sub>(v) = (n-1) / Σ<sub>u</sub> d(v,u)", "Herkese ortalama kaç adımda ulaşır?",
     fmt(top["closeness"][:3])],
    ["Betweenness", "C<sub>B</sub>(v) = Σ σ<sub>st</sub>(v) / σ<sub>st</sub> (normalize)",
     "En kısa yolların ne kadarı ondan geçer (köprü)?", fmt(top["betweenness"])],
    ["Eigenvector", "λ x = A x (A: komşuluk matrisi)", "Önemli düğümlere mi bağlı?", fmt(top["eigenvector"][:4])],
    ["PageRank", "PR(v) = (1-d)/n + d Σ PR(u)/deg(u)", "Rastgele gezgin nereye uğrar?", fmt(top["pagerank"])],
], [2.2 * cm, 4.8 * cm, 4.0 * cm, 5.5 * cm])
img("merkezilik-paneli.png", 14.5 * cm)
h2("Yorum")
bullets([
    "<b>Draco'nun yüksek betweenness'ı:</b> Crabbe ve Goyle ağa yalnızca Draco üzerinden bağlı; bu yüzden "
    "Draco, kendi kümesini ağın geri kalanına bağlayan köprüdür (kesim noktası).",
    "<b>Voldemort closeness ve eigenvector'da öne çıkar</b> çünkü düşmanlık kenarları da ağın parçasıdır; "
    "ağ \"sosyal etkileşim\" ağıdır, yalnızca dostluk ağı değildir.",
    "<b>Metrikler yüksek korelasyonlu</b> (degree ile eigenvector ρ = "
    f"{R['correlation']['degree']['eigenvector']:.2f}, PageRank ρ = {R['correlation']['degree']['pagerank']:.2f}): "
    "küçük ve Harry merkezli bir ağda sıralamalar birbirine benzer.",
])
img("metrik-korelasyonu.png", 9.5 * cm)

# ============================ 7. GELİŞMİŞ ============================ #
h1("7. Gelişmiş analizler")
h2("7.1 Topluluk tespiti (Louvain)")
p("<b>Modularity</b> Q, bir bölümlemenin topluluk içi kenar yoğunluğunun rastgele beklentiden ne kadar fazla "
  "olduğunu ölçer: Q = (1/2m) Σ<sub>ij</sub> [A<sub>ij</sub> - k<sub>i</sub>k<sub>j</sub>/2m] δ(c<sub>i</sub>, c<sub>j</sub>). "
  "Louvain algoritması, düğümleri komşu topluluklara taşıyarak Q'yu açgözlü biçimde artırır, sonra toplulukları "
  "tek düğüme indirip süreci tekrarlar. Seed sabitlenmiştir.")
comm_rows = [["#", "Boyut", "Üyeler"]] + [[i + 1, len(c), ", ".join(c)] for i, c in enumerate(R["communities"])]
table(comm_rows, [0.8 * cm, 1.3 * cm, 14.4 * cm])
p(f"Louvain modularity <b>{R['modularity_louvain']:.3f}</b>, ev bölümlemesi <b>{R['modularity_houses']:.3f}</b>. "
  f"NMI (topluluk-ev benzerliği) = <b>{R['nmi_communities_vs_houses']:.3f}</b>: toplulukların evlerle ilişkisi var "
  "ama özdeş değil. Topluluklar evden çok <i>hikâye rolünü</i> yansıtır.")
note("<b>Neden yalnızca dostça ilişkiler?</b> Modularity \"kenar = aynı topluluğa aitlik\" varsayar. Düşmanlık "
     "kenarı (Harry–Voldemort) iki karakteri aynı topluluğa çekmemelidir. Bu yüzden topluluk ve assortativity "
     "analizleri düşmansız grafta (build_positive_graph) yapılır.")
img("topluluklar.png", 14.5 * cm)

h2("7.2 Ev assortativity ve permütasyon testi")
p("Assortativity katsayısı r, kenarların aynı etiketli düğümler arasında beklenenden ne kadar fazla olduğunu "
  "ölçer (+1: tam homofili, 0: rastgele, negatif: zıt eşleşme). Bulunan "
  f"r = {R['house_assortativity']:.3f} anlamlı mı? <b>Permütasyon testi:</b> ev etiketleri düğümler arasında "
  "2000 kez rastgele karıştırılır, her seferinde r yeniden hesaplanır. Gözlenen r'ye eşit veya büyük değerin "
  f"görülme oranı p-değeridir: <b>p = {R['house_assortativity_p']:.4f}</b> (2000 permütasyonda hiçbiri aşmadı; 1/2001 ölçülebilir en küçük değerdir). Yani bu kadar yüksek ev homofilisi "
  "tesadüfle açıklanamaz. Parametrik varsayım gerektirmediği için küçük ve bağımlı (kenarlar bağımsız değil) bir "
  "ağda uygun bir testtir.")
img("evler-arasi-baglanti.png", 9.5 * cm)

h2("7.3 Small-world analizi")
p("Watts–Strogatz small-world ağlar, rastgele ağlar kadar kısa ortalama yola ve çok daha yüksek kümelenmeye "
  "sahiptir. Aynı n ve m ile 100 Erdős–Rényi grafı üretilip ortalama alınır: "
  "σ = (C / C<sub>rand</sub>) / (L / L<sub>rand</sub>). "
  f"Burada C = {sw['C']:.3f}, C<sub>rand</sub> = {sw['C_random']:.3f}, L = {sw['L']:.3f}, "
  f"L<sub>rand</sub> = {sw['L_random']:.3f}, <b>σ = {sw['sigma']:.2f}</b> (σ &gt; 1: small-world). "
  "Not: 43 düğümlü bir ağda L'nin rastgele ağa yakın çıkması zaten beklenen bir durumdur; asıl fark kümelenmede.")
img("derece-dagilimi.png", 14.5 * cm)

h2("7.4 Dayanıklılık")
p("Düğümler tek tek silinirken en büyük bağlı bileşenin oranı izlenir. Gerçek dünya ağlarında tipik olarak "
  "hedefli saldırı rastgele hataya göre çok daha yıkıcıdır; çünkü az sayıda hub çok sayıda yolu taşır. "
  f"Burada 5 düğüm silinince hedefli (derece) saldırıda %{rob['degree'][5]*100:.0f}, betweenness'a göre "
  f"%{rob['betweenness'][5]*100:.0f}, rastgelede %{rob['random'][5]*100:.0f} kalır.")
img("dayaniklilik.png", 10.5 * cm)

h2("7.5 İşaretli ağ ve Heider yapısal dengesi")
p("Heider'e göre bir üçgen, kenar işaretlerinin çarpımı pozitifse dengelidir: (+,+,+) \"dostumun dostu "
  "dostumdur\", (+,-,-) \"düşmanımın düşmanı dostumdur\". Dostça ilişkiler +1, düşmanlık -1 alınmıştır. "
  f"Sonuç: {sb['triangles']} üçgenin <b>{sb['balanced']}</b>'i dengeli, <b>{sb['unbalanced']}</b>'i dengesiz "
  f"(%{sb['balance_ratio']*100:.1f} denge). Dengesiz üçgenler rastgele değil, hikâyedeki çelişkili karakterlerdedir:")
bullets([
    "<b>Snape</b>: Dumbledore'un müttefiki ama Harry'nin düşmanı (Harry–Dumbledore–Snape).",
    "<b>Peter Pettigrew</b>: James Potter'ın dostu ama Voldemort'un müttefiki ve Sirius/Remus'un düşmanı.",
    "<b>Narcissa Malfoy</b>: Ölüm Yiyen ailesinde ama Harry'ye yardım eden (yalan söyleyerek).",
])


# ============================ 8. v1 -> v2 ============================ #
h1("8. v1'den v2'ye: bulunan hatalar ve düzeltmeler")
p("Proje ilk sürümde çalışıyordu ama veri ve kod kalitesinde sorunlar vardı. Bunları bulup düzeltmek ve "
  "<i>neden</i> önemli olduklarını söyleyebilmek mülakatta güçlü bir noktadır.")
table([
    ["Sorun (v1)", "Etkisi", "Çözüm (v2)"],
    ["\"Lupin\" ve \"Remus Lupin\" iki ayrı düğümdü (aynı karakter)",
     "Merkezilik değerleri ikiye bölünüyor, düğüm/kenar sayısı yanlıştı", "Tek düğüme birleştirildi, test eklendi"],
    ["Gilderoy Lockhart Gryffindor görünüyordu", "Ev matrisi ve renkler yanlış", "Ravenclaw olarak düzeltildi"],
    ["Evi belirsiz karakterlere ev atanmıştı", "Uydurma veri", "\"Bilinmiyor\" kategorisi"],
    ["Harry–Luna kenarı iki kez", "NetworkX tekilleştirir, ama veri kirli", "Temizlendi; validate yinelemeyi yakalar"],
    ["Bariz ilişkiler eksikti (Ron–Ginny, Ron–Hagrid, Harry–Neville…)",
     "Cho–Cedric ana ağdan kopuk göründü (yapay 2. bileşen)", "Eklendi; ağ tek bileşen"],
    ["Yalnızca \"arkadaşlık\" vardı", "Düşmanlık yok; sosyal ağ eksik", "friend/family/ally/enemy + ağırlık"],
    ["Aynı veri ve grafik notebook'ta iki kez tanımlıydı, son hücre boştu", "Bakım zorluğu, tutarsızlık riski",
     "Veri CSV'ye, kod pakete taşındı"],
    ["Test, doğrulama, bağımlılık dosyası yoktu", "Tekrarlanabilirlik yok", "pytest, requirements, pyproject, CI"],
    ["README sayıları elle yazılmıştı", "Veri değişince eskir", "Sayılar results/summary.json'dan"],
], [5.2 * cm, 5.3 * cm, 6.0 * cm])

# ============================ 9. SINIRLILIKLAR ============================ #
h1("9. Sınırlılıklar ve gelecek çalışma")
bullets([
    "<b>Öznel ve küçük veri:</b> 43 düğüm elle derlendi; istatistikler yol göstericidir, kesin kanıt değildir.",
    "<b>Harry merkezli örneklem:</b> Karakterler Harry'nin etrafından seçildiği için hub etkisi şişirilmiştir "
    "(ego-network yanlılığı).",
    "<b>Zamansız ağ:</b> İlişkiler 7 kitap boyunca değişir (Snape, Draco). Zamana bağlı (temporal) ağ daha doğru olur.",
    "<b>Öznel ağırlıklar:</b> Kitaplardan ölçülen birlikte geçme sayısı ile değiştirilebilir.",
    "<b>Yönsüz model:</b> Bazı ilişkiler asimetriktir (Snape→Lily). Yönlü graf düşünülebilir.",
])
h2("Geliştirme fikirleri")
bullets([
    "Kitap metinlerinden birlikte geçme (co-occurrence) ağı çıkarıp 100+ karakterlik ağ kurmak.",
    "Zamana göre (kitap kitap) ağın evrimi; Barabási–Albert ile büyüme modeli karşılaştırması.",
    "Link prediction (Adamic–Adar, Jaccard) ile eksik ilişkileri tahmin etmek.",
    "Etkileşimli görselleştirme (PyVis / Plotly) ve Streamlit demosu.",
])

# ============================ 10. KARMAŞIKLIK ============================ #
h1("10. Algoritma karmaşıklığı")
table([
    ["İşlem", "Algoritma", "Karmaşıklık"],
    ["Derece", "Komşu sayma", "O(n + m)"],
    ["Closeness", "Her düğümden BFS", "O(n(n + m))"],
    ["Betweenness", "Brandes algoritması", "O(nm) (ağırlıksız)"],
    ["Eigenvector", "Güç iterasyonu / sayısal özdeğer", "O(k·m) iterasyon başına O(m)"],
    ["PageRank", "Yinelemeli güç yöntemi", "O(k·m)"],
    ["Kesim noktası / köprü", "Tarjan (DFS, low-link)", "O(n + m)"],
    ["Bağlı bileşenler", "BFS/DFS", "O(n + m)"],
    ["k-core", "Düğüm soyma", "O(m)"],
    ["Louvain", "Açgözlü modularity artırma", "Pratikte yaklaşık O(n log n)"],
    ["Yapısal denge (bu kodda)", "Tüm üçlülerin taranması", "O(n³): n = 43 için 12 341 üçlü"],
    ["Dayanıklılık", "Her silmede bileşen hesabı", "O(n(n + m)) / deneme"],
], [4.5 * cm, 6.3 * cm, 5.7 * cm])
p("Yapısal denge kodu basitlik için tüm üçlüleri tarar (O(n³)). Büyük ağlarda her kenar için komşu "
  "kesişimine bakan O(m·Δ) yöntem kullanılmalıdır; 43 düğümde fark önemsizdir.")
story.append(PageBreak())

# ============================ 11. MÜLAKAT ============================ #
h1("11. Mülakat soruları ve örnek cevaplar")
h2("Proje ve motivasyon")
qa("1. Projeyi kısaca anlatır mısın?",
   "Harry Potter karakterlerini düğüm, ilişkilerini (arkadaşlık, aile, müttefiklik, düşmanlık) kenar olarak "
   "modelleyip merkezilik, topluluk tespiti, dayanıklılık, small-world ve yapısal denge analizleri yaptım. "
   "Kod, CSV'den veri okuyan, doğrulayan ve 23 testle korunan bir Python paketi.")
qa("2. Neden bu konuyu seçtiniz?",
   "Ayrık Matematik dersindeki graf kavramlarını somut bir veriyle uygulamak istedik. Harry Potter ağı "
   "yorumlanabilir: sonuçları hikâyeden doğrulayabiliyoruz (Snape köprü, Slytherin ayrı küme). Bu, "
   "metriklerin anlamını sınamak için iyi bir laboratuvar.")
qa("3. Projede senin katkın neydi?",
   "<i>(Bu soruyu kendi sözlerinle cevapla: ekip üç kişiydi. Örneğin veri modeli, analiz kodu, test, raporlama "
   "gibi hangi kısımları yaptığını önceden belirle ve dürüst ol.)</i>")
qa("4. v1'e göre ne değiştirdin?",
   "Veri hatalarını düzelttim (Lupin'in çift düğümü, Lockhart'ın evi, eksik ilişkiler), düşmanlık ilişkilerini "
   "ekledim, veriyi koddan ayırdım, doğrulama ve test yazdım, analiz derinliğini artırdım (topluluk, dayanıklılık, "
   "small-world, denge). Bölüm 8'deki tablo bunu özetler.")

h2("Graf teorisi")
qa("5. Degree, closeness ve betweenness farkı nedir?",
   "Degree yerel popülerliktir (kaç bağlantı). Closeness küresel yakınlıktır (herkese ortalama kaç adım). "
   "Betweenness köprü rolüdür (en kısa yolların kaçı ondan geçer). Çok bağlantılı biri köprü olmayabilir; "
   "az bağlantılı biri (Draco) iki kümeyi birbirine bağlayabilir.")
qa("6. Eigenvector centrality ile PageRank farkı?",
   "İkisi de \"önemli düğümlere bağlı olmak\" fikrine dayanır. PageRank rastgele gezginin uğrama olasılığıdır ve "
   "sönümleme (d = 0.85) ile ışınlanma içerir; yönlü graflarda ve bağlantısız yapılarda daha kararlıdır. "
   "Eigenvector komşuluk matrisinin baskın özvektörüdür ve yönsüz bağlı graflarda iyi çalışır.")
qa("7. Closeness bağlantısız grafikte nasıl hesaplanır?",
   "Ulaşılamayan düğümler sonsuz mesafe verir. NetworkX, Wasserman–Faust düzeltmesiyle yalnızca ulaşılabilir "
   "düğümleri sayıp bileşen boyutuyla ölçekler. v1'de ağ 2 bileşenliydi ve bu değerleri etkiliyordu; v2'de "
   "ağ tek bileşen olduğu için sorun yok.")
qa("8. Kesim noktası ve köprü nedir, neden önemli?",
   "Çıkarılınca ağı parçalayan düğüm/kenardır. Tek hata noktasını (single point of failure) gösterir. Burada "
   f"Harry, Dumbledore, Draco ve Flitwick kesim noktasıdır; Flitwick–Sprout ve Dumbledore–Ollivander köprülerdir.")
qa("9. Kümelenme katsayısı ne ifade eder, neden yüksek?",
   f"Bir kişinin arkadaşlarının birbirini de tanıma olasılığıdır. Ortalama {S['avg_clustering']:.2f}, aynı "
   f"yoğunluktaki rastgele ağdan (≈{sw['C_random']:.2f}) çok yüksek; çünkü aileler ve gruplar (Weasleyler, "
   "Malfoylar, Hogwarts kadrosu) kapalı üçgenler oluşturur.")
qa("10. Small-world nedir, ağınız small-world mü?",
   f"Kısa ortalama yol + yüksek kümelenme. σ = {sw['sigma']:.2f} &gt; 1 olduğundan evet. Ama 43 düğümde kısa "
   "yol zaten kaçınılmaz; ayırt edici olan kümelenmedir. Bunu dürüstçe belirtirim.")

h2("Yöntem ve istatistik")
qa("11. Modularity nedir? Louvain nasıl çalışır?",
   "Modularity, topluluk içi kenar oranının rastgele (derece korumalı) beklentiden farkıdır; yüksek değer güçlü "
   "topluluk yapısı demektir. Louvain, düğümleri komşu topluluğa taşıyarak Q'yu artırır, sonra toplulukları tek "
   "düğüme indirip tekrarlar. Sonuç seed'e bağlı olabilir; seed sabitledik. Sınırlılığı: çözünürlük limiti "
   "(çok küçük toplulukları görmeyebilir).")
qa("12. Neden topluluk tespitini düşmansız grafta yaptınız?",
   "Modularity kenarı \"aynı gruba aitlik\" kanıtı sayar. Harry–Voldemort düşmanlık kenarı onları aynı topluluğa "
   "çekerdi ve anlamsız sonuç verirdi. Tam grafta merkezilik, dayanıklılık ve denge; dostça grafta topluluk ve "
   "assortativity analiz edildi.")
qa("13. NMI nedir, neden kullandın?",
   "Normalized Mutual Information, iki bölümlemenin birbirinden ne kadar bilgi taşıdığını ölçer (0: ilişkisiz, "
   "1: aynı). Louvain toplulukları ile gerçek evleri karşılaştırmak için kullandım "
   f"({R['nmi_communities_vs_houses']:.2f}: kısmi örtüşme). Kendi uygulamamı yazdım ve iki uç durumda test "
   "ettim (özdeş = 1, bağımsız = 0).")
qa("14. Permütasyon testi nedir, neden t-testi değil?",
   "Etiketleri rastgele karıştırarak \"hiçbir ev etkisi yok\" null dağılımını üretir ve gözlenen değerin "
   "ne kadar uç olduğuna bakar. Ağdaki kenarlar bağımsız olmadığı için klasik testlerin varsayımları sağlanmaz; "
   "permütasyon testi dağılım varsayımı gerektirmez.")
qa("15. Heider yapısal dengesi nedir?",
   f"İşaretli ağlarda üçgenin işaret çarpımı pozitifse dengelidir. Ağımızda %{sb['balance_ratio']*100:.1f} denge "
   "var; dengesizler Snape, Pettigrew ve Narcissa gibi çelişkili karakterlerde toplanıyor, yani metrik "
   "hikâyeyle tutarlı.")
qa("16. Spearman korelasyonunu neden seçtin?",
   "Merkezilik değerleri farklı ölçeklerde ve doğrusal olmayan dağılımlıdır. Spearman sıralama korelasyonudur; "
   "\"iki metrik karakterleri aynı sıraya dizer mi?\" sorusuna cevap verir ve aykırı değerlere dayanıklıdır.")
qa("17. Betweenness'ı neden ağırlıksız hesapladın?",
   "Ağırlıklar öznel (1-3) puanlardır ve güçlü ilişki = kısa mesafe olarak çevrilmesi (1/ağırlık) keyfi bir "
   "varsayım olurdu. Yol metriklerini ağırlıksız tuttum, ağırlığı ayrıca <i>strength</i> olarak raporladım.")

h2("Veri ve doğruluk")
qa("18. Veriye ne kadar güvenebiliriz?",
   "Sınırlı. Elle derlendi, öznel ve Harry merkezli. Sonuçlar \"bu veri setinde\" geçerlidir; Harry'nin merkezi "
   "çıkması kısmen örneklem yanlılığıdır. Bunu README'de ve raporda belirttim. Geliştirme olarak kitap "
   "metinlerinden co-occurrence ağı çıkarmayı öneriyorum.")
qa("19. Ağırlıkları nereden buldun?",
   "Ölçülmedi, 1-3 arası öznel yoğunluk puanıdır (1: sınırlı etkileşim, 3: hikâyenin merkezi). Bu yüzden sonuçların "
   "ağırlığa duyarlılığı düşük tutuldu: yol metrikleri ağırlıksız.")
qa("20. Bir bilgiyi nasıl doğruladın?",
   "Üç katman: (1) data.validate veri tutarlılığını denetler, (2) metrikler elle hesaplanabilen küçük graflarda "
   "test edilir (yıldız grafında betweenness = 1), (3) sonuçlar hikâyeyle karşılaştırılıp mantık kontrolü yapılır.")
qa("21. Veri Harry merkezli ise sonuçlar neden anlamlı?",
   "Anlamlılık soruya bağlı. \"Harry'nin ağdaki konumu\" hakkında değil, yapısal sorular (topluluk, denge, "
   "dayanıklılık, ev homofilisi) hakkında çıkarım yapıyoruz. Harry'nin etkisini göstermek için hedefli saldırı "
   "senaryosunda en çok o düğümün etkisini görebiliyoruz. Yine de kesin çıkarımlardan kaçınırım.")

h2("Mühendislik")
qa("22. Kodu neden paket olarak yapılandırdın?",
   "Hesap, çizim ve veri ayrı olunca test edilebilir ve yeniden kullanılabilir. Notebook yalnızca anlatım "
   "katmanı. Tek komutla (run_analysis.py) tüm sonuçlar ve grafikler yeniden üretilir; README'deki sayılar elle "
   "değil çıktıdan gelir.")
qa("23. Nasıl test ettin?",
   "23 pytest testi: veri doğrulamanın hatalı girdileri reddetmesi, graf özellikleri (tek bileşen, Lupin tek "
   "düğüm), metriklerin bilinen graflarda elle hesaplanan değerleri, NMI uç durumları, dayanıklılık "
   "monotonluğu ve hedefli saldırının rastgeleden kötü olması gibi özellikler. CI her push'ta çalıştırır.")
qa("24. Tekrarlanabilirlik nasıl sağlandı?",
   "Tüm rastgele işlemler (layout, Louvain, permütasyon, rastgele graflar) seed ile sabit; bağımlılıklar "
   "requirements.txt ve pyproject.toml'da; CI temiz ortamda çalıştırır.")
qa("25. Ölçeklenirse ne olur?",
   "Betweenness O(nm), yapısal denge kodum O(n³). 10 000 düğümde betweenness için örnekleme "
   "(k parametresi), denge için komşu kesişimi gerekir. Louvain büyük ağlarda iyi ölçeklenir. Gerekirse "
   "graph-tool veya igraph kullanılabilir.")
qa("26. Bir şeyi farklı yapsaydın ne olurdu?",
   "Veriyi kitap metninden otomatik çıkarırdım (co-occurrence), zamana göre ağın evrimini incelerdim ve "
   "ağırlıklı analizin duyarlılığını (ağırlıkları rastgele bozarak) test ederdim.")

h2("Matematiksel sorular")
qa("27. n düğümlü bir grafta en fazla kaç kenar olur?",
   "n(n-1)/2. Yoğunluk bunun kaçının var olduğudur: 142 / 903 = 0.157.")
qa("28. El sıkışma lemması nedir?",
   "Σ deg(v) = 2m. Derecelerin toplamı çifttir. Burada ortalama derece 2·142/43 = 6.6.")
qa("29. Bir graf ne zaman ağaçtır?",
   "Bağlı ve döngüsüz ise; eşdeğer olarak bağlı ve m = n-1. Bizim ağ m = 142 > 42 olduğu için çok sayıda döngü içerir "
   "(üçgenler kümelenmeyi oluşturur).")
qa("30. Yıldız grafında (1 merkez, 4 yaprak) betweenness kaçtır?",
   "Merkez için normalize edilmiş değer 1, yapraklar için 0: tüm yaprak çiftlerinin tek en kısa yolu merkezden "
   "geçer. Bu, testimizde kullandığımız elle doğrulama.")

# ============================ 12. ÇALIŞTIRMA ============================ #
h1("12. Projeyi çalıştırma")
code("""
git clone https://github.com/MelihAliCagman/HarryPotterGraph.git
cd HarryPotterGraph
python -m venv .venv && .venv\\Scripts\\activate     # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"

python scripts/run_analysis.py      # grafikler (docs/images) + sonuçlar (results/)
pytest                              # 23 test
python scripts/build_pdf.py         # bu rehberi yeniden üretir
jupyter notebook notebooks/HarryPotter.ipynb
""")
note("<b>Mülakat öncesi kontrol listesi:</b> (1) 30 saniyelik özeti ezberle. (2) Bölüm 8'deki hata/düzeltme "
     "tablosunu anlat. (3) Metriklerin formüllerini ve farkını bil. (4) Sınırlılıkları kendin söyle. "
     "(5) Kendi katkını net tanımla. (6) Notebook'u çalıştırıp bir kez canlı gez.")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Harry Potter Sosyal Ağ Analizi · Proje Rehberi")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Sayfa {doc.page}")
    canvas.restoreState()


if __name__ == "__main__":
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=2 * cm,
                            title="Harry Potter Sosyal Ağ Analizi - Proje Rehberi",
                            author="Melih Ali Çağman")
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=footer)
    print("yazıldı:", OUT)
