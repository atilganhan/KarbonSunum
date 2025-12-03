import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Sayfa Ayarı
st.set_page_config(page_title="Araç MEM Karbon Takip", layout="wide", page_icon="🌱")

# -- CSS İLE İMZA (SAĞ ALT) --
st.markdown(
    """
    <style>
    .footer {
        position: fixed; left: 0; bottom: 60px; width: 100%;
        background-color: transparent; color: #333;
        text-align: right; padding-right: 20px; padding-bottom: 10px;
        font-size: 16px; font-weight: bold; z-index: 100;
    }
    </style>
    <div class="footer"><p>Geliştirici: Hande ÇİFÇİ</p></div>
    """, unsafe_allow_html=True
)

# Başlık ve Logo
col1, col2 = st.columns([1, 6])
with col1:
    # Logo Kontrolü
    logo_list = ["logo.png", "logo.jpg", "logo.jpeg", "logo.PNG"]
    logo_path = next((img for img in logo_list if os.path.exists(img)), None)
    if logo_path:
        st.image(logo_path, width=130)
    else:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Ministry_of_National_Education_%28Turkey%29_Logo.svg/240px-Ministry_of_National_Education_%28Turkey%29_Logo.svg.png", width=100)

with col2:
    st.title("Araç İlçe Millî Eğitim Müdürlüğü")
    st.subheader("🌱 Kurumsal Karbon Ayak İzi ve Kıyaslama Paneli")

st.markdown("---")

# -- SOL MENÜ (VERİ GİRİŞİ) --
st.sidebar.header("📝 Veri Girişi")
st.sidebar.info("Aylık tüketim ve personel sayısını giriniz.")

# Kişi Sayısı (Kıyaslama için kritik)
kisi_sayisi = st.sidebar.number_input("Kurumdaki Kişi Sayısı (Öğrenci+Personel)", min_value=1, value=10, step=1)

# Veri Kategorileri
data = {
    'Kategori': ['Elektrik', 'Doğalgaz', 'Benzin', 'Dizel', 'Su', 'Atık'],
    'Birim': ['kWh', 'm³', 'Litre', 'Litre', 'm³', 'kg'],
    'Faktör': [0.42, 2.0, 2.33, 2.67, 0.34, 0.06]
}

miktarlar = []
for i, kat in enumerate(data['Kategori']):
    val = st.sidebar.number_input(f"{kat} ({data['Birim'][i]})", value=0.0, key=f"in_{i}")
    miktarlar.append(val)

# HESAPLAMALAR
df = pd.DataFrame(data)
df['Miktar'] = miktarlar
df['Toplam CO2 (kg)'] = df['Miktar'] * df['Faktör']

toplam_aylik = df['Toplam CO2 (kg)'].sum()
toplam_yillik_tahmini = toplam_aylik * 12 # Aylık veriyi yıla yaydık

# Kişi Başı Analiz
kisi_basi_yillik_kg = toplam_yillik_tahmini / kisi_sayisi
kisi_basi_yillik_ton = kisi_basi_yillik_kg / 1000

# TÜİK Verisi (Referans Değer)
tuik_ortalamasi = 6.5 # Ton/Yıl (2023 verisi)

# -- ANA EKRAN --

# 1. Bölüm: Temel Göstergeler
c1, c2, c3 = st.columns(3)
c1.metric("Aylık Toplam Karbon (Kurum)", f"{toplam_aylik:.1f} kg CO₂")
c2.metric("Telafi İçin Gereken Ağaç", f"{int(toplam_yillik_tahmini/20)} Adet/Yıl 🌳")
with c3:
    st.metric("Kategori Sayısı", f"{len(df)} Kalem")
    st.caption("Hesaplamaya dahil edilen kaynaklar")

st.divider()

# 2. Bölüm: TÜİK Kıyaslaması 
st.subheader("☾⋆ Türkiye Ortalaması ile Kıyaslama (Kişi Başı)")

col_k1, col_k2 = st.columns([2, 1])

with col_k1:
    # Delta Rengi Belirleme
    fark = kisi_basi_yillik_ton - tuik_ortalamasi
    if fark > 0:
        durum_mesaji = "⚠️ Türkiye ortalamasının üzerindesiniz!"
        renk = "inverse" # Kırmızı ok
    else:
        durum_mesaji = "✅ Harika! Türkiye ortalamasının altındasınız."
        renk = "normal" # Yeşil ok
        
    st.metric(
        label="Sizin Yıllık Kişi Başı Ortalamanız",
        value=f"{kisi_basi_yillik_ton:.2f} Ton",
        delta=f"{fark:.2f} Ton (Ulusal Ortalamaya Göre)",
        delta_color=renk
    )
    st.info(f"**Bilgi Notu:** TÜİK 2023 verilerine göre Türkiye'de kişi başı ortalama karbon ayak izi **{tuik_ortalamasi} Ton**'dur. {durum_mesaji}")

with col_k2:
    # Basit Kıyaslama Grafiği
    kiyas_df = pd.DataFrame({
        'Grup': ['Kurumunuz', 'Türkiye Ort.'],
        'Ton': [kisi_basi_yillik_ton, tuik_ortalamasi],
        'Renk': ['Siz', 'TR']
    })
    fig_kiyas = px.bar(kiyas_df, x='Grup', y='Ton', color='Renk', 
                       text_auto='.2f', title="Kişi Başı Yıllık (Ton)",
                       color_discrete_map={'Siz': '#FFA07A', 'TR': '#90EE90'})
    fig_kiyas.update_layout(showlegend=False, height=250)
    st.plotly_chart(fig_kiyas, use_container_width=True)

st.divider()

# 3. Bölüm: Detay Grafikler
if toplam_aylik > 0:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("📊 Kaynak Bazlı Dağılım")
        fig_bar = px.bar(df, x='Kategori', y='Toplam CO2 (kg)', color='Toplam CO2 (kg)', color_continuous_scale='Reds')
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_g2:
        st.subheader("🍰 Oransal Etki")
        df_pie = df[df['Toplam CO2 (kg)'] > 0]
        fig_pie = px.pie(df_pie, values='Toplam CO2 (kg)', names='Kategori', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
else:

    st.warning("Grafikleri görmek için soldan veri girişi yapınız.")
