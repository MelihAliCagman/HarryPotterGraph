"""Ayrık Matematik ders raporunu PDF olarak üretir: docs/Ayrik_Matematik_Rapor.pdf

Sayısal değerler ``results/summary.json`` dosyasından okunur (önce
``python scripts/run_analysis.py`` çalıştırılmalıdır). Gereksinim: reportlab, Pillow.
Windows'ta Arial yazı tipi kullanılır (Türkçe karakter desteği için).
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parents[1]
FONTS = Path("C:/Windows/Fonts")
OUT = ROOT / "docs" / "Ayrik_Matematik_Rapor.pdf"
IMG = ROOT / "docs" / "images"
R = json.loads((ROOT / "results" / "summary.json").read_text(encoding="utf-8"))

for name, file in [("Arial", "arial.ttf"), ("Arial-Bold", "arialbd.ttf"),
                   ("Arial-Italic", "ariali.ttf"), ("Arial-BoldItalic", "arialbi.ttf")]:
    pdfmetrics.registerFont(TTFont(name, FONTS / file))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                              italic="Arial-Italic", boldItalic="Arial-BoldItalic")

ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="Arial", fontSize=10.5, leading=15.5,
                      alignment=TA_JUSTIFY, spaceAfter=6)
TITLE = ParagraphStyle("title", parent=BODY, fontName="Arial-Bold", fontSize=19, leading=24,
                       alignment=TA_CENTER, spaceAfter=10)
CENTER = ParagraphStyle("center", parent=BODY, alignment=TA_CENTER, spaceAfter=3)
H1 = ParagraphStyle("h1", parent=BODY, fontName="Arial-Bold", fontSize=13.5, leading=18,
                    spaceBefore=12, spaceAfter=6, alignment=0)
H2 = ParagraphStyle("h2", parent=BODY, fontName="Arial-Bold", fontSize=11, leading=15,
                    spaceBefore=8, spaceAfter=3, alignment=0)
BUL = ParagraphStyle("bul", parent=BODY, leftIndent=16, bulletIndent=4, spaceAfter=2)
CAP = ParagraphStyle("cap", parent=BODY, fontSize=9, leading=12, alignment=TA_CENTER,
                     textColor=colors.HexColor("#444444"), spaceAfter=10)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=9, leading=12, alignment=0, spaceAfter=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Arial-Bold")
REF = ParagraphStyle("ref", parent=BODY, fontSize=9.5, leading=13, leftIndent=18, firstLineIndent=-18,
                     spaceAfter=3)

story: list = []
fig_no = [0]
tab_no = [0]


def h1(t): story.append(Paragraph(t, H1))
def h2(t): story.append(Paragraph(t, H2))
def p(t): story.append(Paragraph(t, BODY))
def bullets(items):
    for it in items:
        story.append(Paragraph(it, BUL, bulletText="•"))
    story.append(Spacer(1, 4))
def figure(name, caption, width=14 * cm):
    fig_no[0] += 1
    w, h = PILImage.open(IMG / name).size
    story.append(Image(str(IMG / name), width=width, height=width * h / w))
    story.append(Paragraph(f"<b>Şekil {fig_no[0]}.</b> {caption}", CAP))
def table(rows, widths, caption):
    tab_no[0] += 1
    story.append(Paragraph(f"<b>Tablo {tab_no[0]}.</b> {caption}", CAP))
    data = [[Paragraph(str(c), CELLB if i == 0 else CELL) for c in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 1, colors.black), ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 1, colors.black), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story.append(t)
    story.append(Spacer(1, 10))


S, top, sw, sb, rob = R["summary"], R["top"], R["small_world"], R["structural_balance"], R["robustness"]
rc = R["relation_counts"]
hm = R["house_matrix"]
fmt = lambda lst: ", ".join(f"{n} ({v:.3f})" if isinstance(v, float) and v < 1 else f"{n} ({v})" for n, v in lst)

# ============================ BAŞLIK ============================ #
story.append(Paragraph("Harry Potter Evrenindeki Karakter İlişkilerinin<br/>Graf Teorisi ile Modellenmesi ve "
                       "Sosyal Ağ Analizi", TITLE))
story.append(Spacer(1, 6))
for a in ("Işıl Cemre Sağlam", "Nisa Nur Yondemir", "Melih Ali Çağman"):
    story.append(Paragraph(f"<b>{a}</b>", CENTER))
story.append(Paragraph("Bilgisayar Mühendisliği, Teknoloji Fakültesi, Gazi Üniversitesi, Ankara, Türkiye", CENTER))
story.append(Paragraph("Ayrık Matematik Dersi Proje Raporu", CENTER))
story.append(Spacer(1, 12))

h1("Özet")
p(f"Bu çalışmada Harry Potter evrenindeki {S['nodes']} karakter arasındaki arkadaşlık, aile, müttefiklik ve "
  f"düşmanlık ilişkileri ({S['edges']} ilişki) yönsüz ve ağırlıklı bir graf olarak modellenmiş ve sosyal ağ "
  "analizi yöntemleriyle incelenmiştir. Karakterler düğüm, ilişkiler kenar olarak temsil edilmiştir. "
  "Derece, yakınlık (closeness), arasındalık (betweenness), özvektör ve PageRank merkezilikleri hesaplanmış; "
  "Louvain algoritmasıyla topluluklar belirlenmiş ve Hogwarts evleriyle karşılaştırılmış; ağın dayanıklılığı "
  "düğüm silme benzetimleriyle sınanmış; small-world özelliği ve Heider yapısal dengesi incelenmiştir. "
  f"Sonuçlara göre ağın en merkezi karakterleri {top['degree'][0][0]} ve {top['degree'][1][0]}'dur; ev "
  f"homofilisi istatistiksel olarak anlamlıdır (r = {R['house_assortativity']:.2f}), ancak topluluklar evlerden "
  "çok hikâye rollerini yansıtmaktadır; ağ small-world özelliği göstermektedir "
  f"(σ = {sw['sigma']:.2f}) ve üçgenlerin %{sb['balance_ratio']*100:.0f}'i yapısal olarak dengelidir.")
p("<b>Anahtar kelimeler:</b> graf teorisi, sosyal ağ analizi, merkezilik, topluluk tespiti, small-world, "
  "yapısal denge.")

# ============================ 1 ============================ #
h1("1. Problemin Tanımı")
p("Sosyal ağlar, bireylerin birbirleriyle olan ilişkilerini temsil eden ve sosyal medya, iş dünyası ve eğitim "
  "gibi birçok alanda önemli rol oynayan yapılardır. Sosyal ağ analizinin temel amacı, ağdaki bireyler "
  "(düğümler) arasındaki etkileşimleri inceleyerek merkezi figürleri, toplulukları ve ağın genel yapısını "
  "anlamaktır. Bu çalışma, kurgusal ama herkesçe tanınan bir ilişki ağı üzerinde bu analizleri uygulamayı "
  "hedeflemektedir. Kurgusal ağın tercih edilme nedeni, bulunan sonuçların hikâye bilgisiyle "
  "doğrulanabilmesidir (ör. bir karakterin ağdaki köprü rolü, hikâyedeki rolüyle karşılaştırılabilir).")
p("Çalışmanın araştırma soruları şunlardır:")
bullets([
    "<b>S1.</b> Ağın merkezinde kim bulunmaktadır; ağdaki köprü görevini hangi karakterler üstlenmektedir?",
    "<b>S2.</b> Hogwarts evleri sosyal olarak kümelenmekte midir, yoksa topluluklar evlerden bağımsız mıdır?",
    "<b>S3.</b> Ağ, kritik karakterlerin çıkarılmasına karşı ne kadar dayanıklıdır?",
    "<b>S4.</b> Ağ small-world özelliği göstermekte midir?",
    "<b>S5.</b> Dostluk ve düşmanlık ilişkileri yapısal olarak tutarlı mıdır?",
])

# ============================ 2 ============================ #
h1("2. Graf Yapısı ve Temel Kavramlar")
p("Graf, düğümler (noktalar) kümesi V ve düğümler arasındaki bağlantıları gösteren kenarlar kümesi E ile "
  "tanımlanan G = (V, E) matematiksel yapısıdır. Kenarların yönü olmayan graflar <i>yönsüz</i>, yönü olan "
  "graflar <i>yönlü</i> graf olarak adlandırılır. Bu çalışmada karakterler arasındaki ilişkiler karşılıklı "
  "kabul edildiğinden (ör. Harry ve Ron birbirlerini arkadaş olarak görür) yönsüz graf kullanılmıştır. "
  "Her kenar bir ilişki türü (<i>friend, family, ally, enemy</i>) ve 1–3 arası bir ağırlık taşır.")
p("Çalışmada kullanılan temel kavramlar aşağıda özetlenmiştir (n = |V|, m = |E|).")
table([
    ["Kavram", "Tanım"],
    ["Derece", "Bir düğüme bağlı kenar sayısı; ortalama derece 2m/n. El sıkışma lemması gereği derecelerin toplamı 2m'dir."],
    ["Yol, en kısa yol", "İki düğümü birleştiren kenar dizisi; en kısa olanın uzunluğu d(u, v)."],
    ["Bağlı bileşen", "Aralarında yol bulunan düğümlerin en büyük kümesi."],
    ["Yoğunluk", "m / (n(n−1)/2): mümkün kenarların ne kadarının bulunduğu."],
    ["Çap, yarıçap", "En büyük ve en küçük eksantriklik (bir düğümün en uzak düğüme uzaklığı)."],
    ["Kümelenme katsayısı", "C(v) = 2T(v) / (k(k−1)): komşuların birbirine bağlı olma oranı (T: v'yi içeren üçgen sayısı)."],
    ["Kesim noktası, köprü", "Çıkarıldığında bileşen sayısını artıran düğüm ve kenar."],
], [4 * cm, 12.5 * cm], "Temel graf kavramları.")

h2("2.1 Graf Yapısının Projedeki Önemi")
p("Graf yapısı, karakterler arasındaki ilişkileri somut ve görselleştirilebilir bir model olarak sunar. "
  "Bu sayede (i) ilişkilerin temsili ve görselleştirilmesi, (ii) toplulukların ve gruplar arası bağların "
  "yapısal analizi, (iii) merkezi karakterlerin ölçülmesi ve (iv) köprü figürlerin saptanması mümkün olur. "
  "Örneğin Gryffindor karakterleri aynı evin üyeleri olarak bir topluluk oluşturur ve bu topluluğun ağdaki "
  "rolü ölçülebilir bir analiz konusudur.")

# ============================ 3 ============================ #
h1("3. Veri ve Model")
p(f"Veri, filmlerden ve kitaplardan yola çıkılarak elle derlenmiştir ve iki dosyadan oluşur: karakter ve ev "
  f"bilgisi (<i>characters.csv</i>) ile ilişki listesi (<i>relationships.csv</i>). Ağ {S['nodes']} düğüm ve "
  f"{S['edges']} kenar içerir. Kenarların {rc['friend']}'ı arkadaşlık, {rc['family']}'i aile, {rc['ally']}'ü "
  f"müttefiklik ve {rc['enemy']}'si düşmanlık ilişkisidir. Ağırlık, ilişkinin yoğunluğuna dair öznel bir puandır "
  "(1: sınırlı etkileşim, 3: hikâyenin merkezindeki ilişki).")
p("Veri yüklenirken otomatik olarak doğrulanır: yinelenen karakter, bilinmeyen düğüm, kendine bağlanan kenar, "
  "geçersiz ilişki türü, ağırlık veya ev adı ile yinelenen ilişki çiftleri hata olarak bildirilir. Ağ iki "
  "biçimde kullanılmıştır: tüm ilişkileri içeren <i>tam ağ</i> (merkezilik, dayanıklılık, yapısal denge) ve "
  "yalnızca dostça ilişkileri içeren <i>pozitif ağ</i> (topluluk tespiti, ev homofilisi). Düşmanlık kenarları "
  "iki karakterin aynı gruba ait olduğunu göstermediğinden, grup yapısı analizleri pozitif ağda yapılmıştır.")
table([
    ["Özellik", "Değer"],
    ["Düğüm / kenar sayısı", f"{S['nodes']} / {S['edges']}"],
    ["Yoğunluk", f"{S['density']:.3f}"],
    ["Ortalama derece", f"{S['avg_degree']:.2f}"],
    ["Ortalama kümelenme katsayısı", f"{S['avg_clustering']:.3f}"],
    ["Geçişlilik (transitivity)", f"{S['transitivity']:.3f}"],
    ["Bağlı bileşen sayısı", f"{S['components']}"],
    ["Çap / yarıçap", f"{S['diameter']} / {S['radius']}"],
    ["Ortalama en kısa yol", f"{S['avg_shortest_path']:.3f}"],
], [7 * cm, 4 * cm], "Ağın temel istatistikleri.")
figure("sosyal-ag-grafigi.png", "Harry Potter sosyal ağı. Düğüm rengi Hogwarts evini, düğüm boyutu derece "
       "merkeziliğini gösterir.", 15 * cm)
figure("iliski-turleri.png", "İlişki türlerine göre ağ (kesikli kırmızı çizgiler düşmanlık ilişkileridir).", 15 * cm)

# ============================ 4 ============================ #
h1("4. Yöntem")
h2("4.1 Merkezilik Ölçüleri")
table([
    ["Ölçü", "Tanım", "Yorum"],
    ["Derece (degree)", "C<sub>D</sub>(v) = deg(v) / (n−1)", "Doğrudan bağlantı sayısı; yerel popülerlik."],
    ["Yakınlık (closeness)", "C<sub>C</sub>(v) = (n−1) / Σ<sub>u</sub> d(v, u)",
     "Diğer düğümlere ortalama yakınlık."],
    ["Arasındalık (betweenness)", "C<sub>B</sub>(v) = Σ<sub>s≠v≠t</sub> σ<sub>st</sub>(v) / σ<sub>st</sub>",
     "En kısa yolların ne kadarının v'den geçtiği; köprü rolü."],
    ["Özvektör (eigenvector)", "λx = Ax", "Önemli düğümlere bağlı olmanın ölçüsü."],
    ["PageRank", "PR(v) = (1−d)/n + d Σ<sub>u∈N(v)</sub> PR(u)/deg(u)", "Rastgele gezginin uğrama olasılığı (d = 0.85)."],
], [3.6 * cm, 6.6 * cm, 6.3 * cm], "Kullanılan merkezilik ölçüleri.")
p("Yol tabanlı ölçüler (closeness, betweenness) ağırlıksız hesaplanmıştır; çünkü ağırlıklar öznel puanlardır ve "
  "bunların mesafeye çevrilmesi keyfi bir varsayım olurdu. Ağırlık bilgisi ayrıca ağırlıklı derece (strength) "
  "olarak raporlanmıştır. Ölçüler arasındaki ilişki Spearman sıralama korelasyonuyla incelenmiştir.")
h2("4.2 Topluluk Tespiti ve Ev Homofilisi")
p("Topluluklar, modülerliği (modularity) en büyüklemeyi hedefleyen Louvain algoritmasıyla bulunmuştur. "
  "Modülerlik Q = (1/2m) Σ<sub>ij</sub> [A<sub>ij</sub> − k<sub>i</sub>k<sub>j</sub>/2m] δ(c<sub>i</sub>, c<sub>j</sub>) "
  "ile tanımlıdır. Bulunan bölümleme ile gerçek ev bölümlemesi, normalleştirilmiş karşılıklı bilgi (NMI) ve "
  "modülerlik ile karşılaştırılmıştır. Evlerin kendi içinde bağlanma eğilimi (homofili), öznitelik "
  "assortativity katsayısı r ile ölçülmüş ve anlamlılığı, ev etiketlerinin 2000 kez rastgele "
  "karıştırıldığı bir permütasyon testiyle sınanmıştır.")
h2("4.3 Dayanıklılık, Small-World ve Yapısal Denge")
p("Dayanıklılık için düğümler tek tek silinirken en büyük bağlı bileşenin oranı izlenmiştir. Hedefli saldırıda "
  "düğümler derece veya arasındalık sırasına göre, rastgele senaryoda ise 200 deneme ortalaması alınarak "
  "silinmiştir. Small-world özelliği için aynı düğüm ve kenar sayılı 100 Erdős–Rényi rastgele grafıyla "
  "karşılaştırma yapılmış ve σ = (C/C<sub>rand</sub>) / (L/L<sub>rand</sub>) hesaplanmıştır (σ &gt; 1: small-world). "
  "Yapısal denge için dostça ilişkiler +1, düşmanlık −1 işaretlenmiş; işaret çarpımı pozitif olan üçgenler "
  "(Heider, 1946) dengeli sayılmıştır.")

# ============================ 5 ============================ #
h1("5. Bulgular")
h2("5.1 Merkezilik")
table([
    ["Ölçü", "İlk beş karakter"],
    ["Derece", fmt(top["degree"])],
    ["Yakınlık", fmt(top["closeness"])],
    ["Arasındalık", fmt(top["betweenness"])],
    ["Özvektör", fmt(top["eigenvector"])],
    ["PageRank", fmt(top["pagerank"])],
], [3 * cm, 13.5 * cm], "Merkezilik ölçülerine göre ilk beş karakter.")
p(f"{top['degree'][0][0]} tüm ölçülerde birinci, {top['degree'][1][0]} ikincidir. Voldemort, düşmanlık "
  "ilişkilerinin de ağın parçası olması nedeniyle yakınlık ve özvektör merkeziliğinde ilk sıralarda yer alır. "
  f"Draco Malfoy'un yüksek arasındalığı ({dict(top['betweenness'])['Draco']:.3f}), Crabbe ve Goyle'u ağa "
  "bağlayan tek karakter olmasından kaynaklanır; bu nedenle Draco bir kesim noktasıdır. "
  f"Ölçüler arasındaki korelasyon yüksektir (derece–özvektör ρ = {R['correlation']['degree']['eigenvector']:.2f}); "
  "küçük ve merkezi bir ağda sıralamalar birbirine benzer.")
figure("merkezilik-paneli.png", "Dört merkezilik ölçüsünde ilk 10 karakter (renk: ev).", 15 * cm)

h2("5.2 Evler ve Topluluklar")
houses = ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff", "Bilinmiyor"]
table([["Ev"] + houses] + [[h] + [hm[c][h] for c in houses] for h in houses], [3 * cm] + [2.7 * cm] * 5,
      "Evler arası kenar sayısı (köşegen: ev içi kenarlar).")
p(f"Ev özniteliğine göre assortativity katsayısı r = {R['house_assortativity']:.3f}'tür; permütasyon testinde "
  f"p = {R['house_assortativity_p']:.4f} (2000 karıştırmada gözlenen değer hiç aşılmamıştır). Dolayısıyla evler "
  "tesadüfün açıklayamayacağı ölçüde kümelenmektedir. Gryffindor evi hem kendi içinde hem Slytherin ile yoğun "
  "bağlantılıdır; Slytherin ile Ravenclaw arasında hiç kenar yoktur.")
p(f"Louvain algoritması {len(R['communities'])} topluluk bulmuştur (modülerlik {R['modularity_louvain']:.3f}); "
  f"ev bölümlemesinin modülerliği {R['modularity_houses']:.3f}'tür. NMI = {R['nmi_communities_vs_houses']:.3f} "
  "olup topluluklar evlerle kısmen örtüşür. Topluluklar evlerden çok hikâye rollerini yansıtır:")
comm_names = ["Weasley ailesi ve Dumbledore Ordusu çevresi", "Order üyeleri ve Potter ailesi", "Ölüm Yiyenler ve Malfoylar",
              "Hogwarts öğretmen kadrosu", "Gryffindor öğrenci ikilisi"]
bullets([f"<b>Topluluk {i+1}</b> ({len(c)} karakter, {comm_names[i] if i < len(comm_names) else ''}): "
         + ", ".join(c) for i, c in enumerate(R["communities"])])
figure("topluluklar.png", "Louvain toplulukları (düğüm içi renk: topluluk, kenar rengi: ev).", 15 * cm)
figure("evler-arasi-baglanti.png", "Evler arası bağlantı sayıları ısı haritası.", 9.5 * cm)

h2("5.3 Dayanıklılık, Small-World ve Yapısal Denge")
p(f"Beş düğüm silindiğinde en büyük bileşen hedefli (derece) saldırıda ağın %{rob['degree'][5]*100:.0f}'ine, "
  f"arasındalığa göre saldırıda %{rob['betweenness'][5]*100:.0f}'ine, rastgele silmede ise "
  f"%{rob['random'][5]*100:.0f}'ine düşer. Hedefli saldırı rastgele hatadan belirgin biçimde daha yıkıcıdır; "
  f"kesim noktaları {', '.join(R['articulation_points'])} karakterleridir, köprü kenarlar "
  + "; ".join(f"{a}–{b}" for a, b in R["bridges"]) + " ilişkileridir.")
p(f"Ağın kümelenme katsayısı C = {sw['C']:.3f}, ortalama yol uzunluğu L = {sw['L']:.3f}'tür; aynı boyuttaki "
  f"rastgele ağlarda C<sub>rand</sub> = {sw['C_random']:.3f}, L<sub>rand</sub> = {sw['L_random']:.3f}'tür. "
  f"σ = {sw['sigma']:.2f} &gt; 1 olduğundan ağ small-world özelliği göstermektedir. Ancak 43 düğümlük bir "
  "ağda kısa yol uzunluğu zaten beklenen bir durumdur; ayırt edici olan yüksek kümelenmedir.")
p(f"Ağda {sb['triangles']} üçgen vardır; bunların {sb['balanced']}'i dengeli, {sb['unbalanced']}'i dengesizdir "
  f"(denge oranı %{sb['balance_ratio']*100:.1f}). Dengesiz üçgenler hikâyedeki çelişkili karakterlerde "
  "toplanır: Snape (Dumbledore'un müttefiki, Harry'nin düşmanı), Peter Pettigrew (Potter'ların dostu, "
  "Voldemort'un müttefiki) ve Narcissa Malfoy (Ölüm Yiyen ailesinden, Harry'ye yardım eden).")
figure("dayaniklilik.png", "Düğüm silme benzetimi: en büyük bağlı bileşenin oranı.", 10.5 * cm)
figure("derece-dagilimi.png", "Derece dağılımı ve log-log tamamlayıcı birikimli dağılım.", 14 * cm)

# ============================ 6 ============================ #
h1("6. Tartışma ve Sınırlılıklar")
p("Bulgular, ağın küçük, yoğun kümelenmiş ve birkaç hub etrafında örgütlenmiş olduğunu göstermektedir. "
  "Yapısal denge ve topluluk sonuçlarının hikâye bilgisiyle tutarlı olması, modelin anlamlı olduğunu "
  "desteklemektedir. Bununla birlikte çalışmanın önemli sınırlılıkları vardır:")
bullets([
    "<b>Öznel ve küçük veri:</b> Karakter ve ilişkiler elle derlenmiştir; resmî bir veri seti değildir. "
    "43 düğümlük ağda istatistiksel sonuçlar yol göstericidir, kesin kanıt değildir.",
    "<b>Örneklem yanlılığı:</b> Karakterler Harry'nin çevresinden seçildiği için Harry'nin merkezilik "
    "değerleri kısmen bu seçimin sonucudur (ego-network etkisi).",
    "<b>Öznel ağırlıklar:</b> Kenar ağırlıkları ölçülmüş değil, yorumlanmış puanlardır; bu nedenle yol "
    "tabanlı ölçüler ağırlıksız hesaplanmıştır.",
    "<b>Zamansız model:</b> İlişkiler yedi kitap boyunca değişmektedir; ağ tek bir zaman kesitidir.",
    "<b>Yönsüz model:</b> Bazı ilişkiler asimetriktir (ör. Snape'in Lily'ye bağlılığı).",
])
p("Gelecek çalışmada ağın kitap metinlerinden birlikte geçme (co-occurrence) yöntemiyle otomatik "
  "oluşturulması, zamana göre evrimi ve bağlantı tahmini (link prediction) yöntemleriyle eksik ilişkilerin "
  "bulunması önerilmektedir.")

# ============================ 7 ============================ #
h1("7. Sonuç")
p("Bu çalışmada Harry Potter evrenindeki karakter ilişkileri graf teorisiyle modellenmiş ve çok yönlü bir "
  "sosyal ağ analizi yapılmıştır. Harry ve Dumbledore ağın merkezidir; Draco ve Flitwick gibi karakterler "
  "kendi gruplarını ağa bağlayan köprülerdir. Evler istatistiksel olarak anlamlı biçimde kümelenmekte, ancak "
  "gerçek topluluk yapısı hikâye rollerine göre şekillenmektedir. Ağ small-world özelliği göstermekte, hedefli "
  "saldırılara rastgele hatalardan daha kırılgan olmakta ve dostluk/düşmanlık ilişkileri büyük ölçüde yapısal "
  "dengeye uymaktadır. Çalışma, kod ve veriyi ayıran, doğrulama ve birim testleri içeren, yeniden "
  "üretilebilir bir Python paketi olarak yayımlanmıştır.")

# ============================ EK ============================ #
h1("Ek A. Proje Kodları")
p("Tüm kodlar, veri ve sonuçlar projenin GitHub deposunda yer almaktadır "
  "(github.com/MelihAliCagman/HarryPotterGraph). Depo yapısı:")
table([
    ["Yol", "İçerik"],
    ["data/", "characters.csv ve relationships.csv (ham veri)"],
    ["src/hpgraph/", "data.py (yükleme, doğrulama), metrics.py (analizler), plots.py (grafikler)"],
    ["scripts/run_analysis.py", "Tüm analizleri çalıştırır, grafik ve sonuç dosyalarını üretir"],
    ["notebooks/HarryPotter.ipynb", "Analizlerin adım adım anlatıldığı notebook"],
    ["tests/", "23 birim testi (veri doğrulama ve metrik doğruluğu)"],
    ["results/", "summary.json ve centrality_metrics.csv"],
], [5 * cm, 11.5 * cm], "Depo yapısı.")
p("Çalıştırma: <font face='Arial-Italic'>pip install -e \".[dev]\"</font>, ardından "
  "<font face='Arial-Italic'>python scripts/run_analysis.py</font> ve <font face='Arial-Italic'>pytest</font>.")

h1("Kaynakça")
for r in [
    "Newman, M. E. J. (2018). <i>Networks</i> (2. baskı). Oxford University Press.",
    "Freeman, L. C. (1977). A set of measures of centrality based on betweenness. <i>Sociometry</i>, 40(1), 35–41.",
    "Brandes, U. (2001). A faster algorithm for betweenness centrality. <i>Journal of Mathematical Sociology</i>, 25(2), 163–177.",
    "Page, L., Brin, S., Motwani, R., Winograd, T. (1999). <i>The PageRank citation ranking: Bringing order to the web</i>. Stanford InfoLab.",
    "Blondel, V. D., Guillaume, J.-L., Lambiotte, R., Lefebvre, E. (2008). Fast unfolding of communities in large networks. <i>Journal of Statistical Mechanics</i>, P10008.",
    "Newman, M. E. J. (2003). Mixing patterns in networks. <i>Physical Review E</i>, 67, 026126.",
    "Watts, D. J., Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. <i>Nature</i>, 393, 440–442.",
    "Heider, F. (1946). Attitudes and cognitive organization. <i>Journal of Psychology</i>, 21, 107–112.",
    "Hagberg, A. A., Schult, D. A., Swart, P. J. (2008). Exploring network structure, dynamics, and function using NetworkX. <i>Proceedings of the 7th Python in Science Conference</i>, 11–15.",
]:
    story.append(Paragraph(r, REF))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, f"{doc.page}")
    canvas.restoreState()


if __name__ == "__main__":
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2.3 * cm, rightMargin=2.3 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Harry Potter Karakter İlişkilerinin Graf Teorisi ile Modellenmesi",
                            author="Işıl Cemre Sağlam, Nisa Nur Yondemir, Melih Ali Çağman")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("yazıldı:", OUT)
