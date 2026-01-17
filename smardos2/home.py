import streamlit as st

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="SMARDOS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================
# GLOBAL CSS (MINIMAL)
# ==============================
st.markdown("""
<style>
header, [data-testid="stSidebar"], [data-testid="stDecoration"] {
    display: none !important;
}
.main .block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# HERO SECTION (STREAMLIT NATIVE)
# ==============================
st.markdown(
    "<h1 style='text-align:center;'>🎓 <b>SMARDOS</b></h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <h2 style="text-align:center;">
        Materi <span style="color:#2563eb;">Akademik</span><br>
        Jadi Lebih Paham
    </h2>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="text-align:center; font-size:18px; color:#6b7280;">
        Butuh bantuan riset atau tugas kuliah?<br>
        Konsultasikan pada <b>SMARDOS</b>, asisten dosen cerdasmu.
    </p>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("")

# ==============================
# CTA BUTTON
# ==============================
st.markdown("""
<style>
div.stButton {
    display: flex;
    justify-content: center;
    width: 100%;
}

div.stButton > button {
    background-color: #2563eb !important;
    color: white !important;
    font-weight: 500;
    padding: 14px 32px;
    border: none;
    font-size: 16px;
}

div.stButton > button:hover {
    background-color: #1d4ed8 !important;
}
</style>
""", unsafe_allow_html=True)

col_btn = st.columns([1, 2, 1])
with col_btn[1]:
    if st.button("🚀 Tanya SMARDOS Sekarang"):
        st.switch_page("pages/app.py")

# ==============================
# FEATURES (3 KOLOM NATIF)
# ==============================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ⚡ Respons Cepat")
    st.write("Jawaban akademik instan tanpa antre lama.")

with col2:
    st.markdown("### 📖 Wawasan Luas")
    st.write("Analisis jurnal, materi kuliah, metodologi terbaru.")

with col3:
    st.markdown("### 🎯 Bimbingan")
    st.write("Penjelasan terstruktur sesuai kebutuhan.")

st.write("")
st.write("")

# ==============================
# FOOTER
# ==============================
st.markdown(
    """
    <hr>
    <p style="text-align:center; color:#9ca3af; font-size:14px;">
        © 2026 SMARDOS · Smart Asisten Dosen
    </p>
    """,
    unsafe_allow_html=True
)
