import os
import streamlit as st
import requests

# ======================================================
# 1. KONFIGURASI HALAMAN
# ======================================================
st.set_page_config(
    page_title="SMARDOS - Ruang Konsultasi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# 2. ADVANCED CUSTOM CSS (FIX KONTRAS TEKS)
# ======================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    /* Base */
    .stApp { background-color: #f8fafc; }
    html, body, [class*="st-"] { font-family: 'Nunito', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        text-align: left;
        padding: 10px 15px;
    }

    /* Header */
    .main-header {
        background: white;
        padding: 1rem 2rem;
        border-bottom: 2px solid #2563eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-radius: 14px;
    }

    /* ===== FIX: Chat bubble contrast on Dark/Light mode =====
       Streamlit chat message container: [data-testid="stChatMessage"]
       Role markers are classes: .stChatMessage (newer) / data attributes (varies).
       We'll style by 'assistant' and 'user' via attribute selector on avatar container parent.
    */

    /* Make chat message look consistent */
    [data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 1.0rem 1.1rem;
        margin-bottom: 0.8rem;
        border: 1px solid rgba(148,163,184,0.35);
    }

    /* Force readable text inside chat */
    [data-testid="stChatMessage"] * {
        color: #0f172a !important; /* slate-900 */
    }

    /* Assistant bubble background */
    [data-testid="stChatMessage"][data-testid*="assistant"],
    [data-testid="stChatMessage"]:has([aria-label="assistant avatar"]) {
        background: #ffffff !important;
    }

    /* User bubble background */
    [data-testid="stChatMessage"][data-testid*="user"],
    [data-testid="stChatMessage"]:has([aria-label="user avatar"]) {
        background: #eff6ff !important; /* blue-50 */
        border-color: rgba(37, 99, 235, 0.25) !important;
    }

    /* If browser/theme dark mode makes page dark, keep bubbles readable */
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #0b1220; } /* dark */
        [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(148,163,184,0.15); }
        [data-testid="stChatMessage"] { border-color: rgba(148,163,184,0.18); }
        [data-testid="stChatMessage"] * { color: #0f172a !important; } /* keep text dark because bubbles are light */
    }

    /* Optional: make markdown links visible */
    [data-testid="stChatMessage"] a {
        color: #2563eb !important;
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================================================
# 3. KONFIG OLLAMA
# ======================================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")

# ======================================================
# 4. LOGIC FUNCTIONS
# ======================================================
@st.cache_data(ttl=300)
def get_available_models(base_url: str):
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=5)
        r.raise_for_status()
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def generate_smardos_response(user_input: str, model_name: str, base_url: str) -> str:
    try:
        from langchain_ollama import OllamaLLM
    except ModuleNotFoundError:
        return "Ollama (langchain_ollama) tidak tersedia di environment ini."

    llm = OllamaLLM(
        model=model_name,
        temperature=0.3,
        base_url=base_url,
        # Biar lebih cepat dan tidak kebablasan panjang
        num_predict=350
    )

    system_instructions = (
        "Kamu adalah SMARDOS (Smart Asisten Dosen), asisten akademik khusus perguruan tinggi.\n"
        "TUGAS UTAMA:\n"
        "1. Hanya jawab pertanyaan yang berkaitan dengan materi perkuliahan, teori akademik, atau metode penelitian.\n"
        "2. Jika pertanyaan TIDAK berkaitan dengan perkuliahan/pendidikan, tolak dengan sopan.\n"
        "3. Setiap jawaban WAJIB menyertakan referensi ilmiah di bagian akhir.\n"
        "4. Format referensi harus mencantumkan Link URL (Google Scholar/DOAJ/dll).\n"
        "5. Gunakan Bahasa Indonesia yang formal dan edukatif.\n"
        "6. Jawaban maksimal 6 paragraf, ringkas dan jelas."
    )

    full_prompt = f"### Instruction:\n{system_instructions}\n\n### User Question:\n{user_input}\n\n### Response:"
    return llm.invoke(full_prompt)


def check_ollama_connection(base_url: str):
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=5)
        st.write("✅ Status:", r.status_code)
        st.write("✅ Endpoint:", f"{base_url}/api/tags")
        st.json(r.json())
    except Exception as e:
        st.error(f"❌ Gagal konek ke Ollama: {e}")

# ======================================================
# 5. SIDEBAR
# ======================================================
with st.sidebar:
    st.markdown(
        "<h1 style='color:#1e3a8a;font-size:24px;font-weight:800;'>🎓 SMARDOS</h1>",
        unsafe_allow_html=True
    )
    st.caption("v2.5 - Your Smart Academic Partner")

    st.markdown("---")

    st.subheader("📌 Navigasi")
    if st.button("🏠 Kembali ke Beranda"):
        st.switch_page("home.py")

    st.markdown("---")

    st.subheader("⚙️ Panel Kontrol AI")
    st.caption(f"🔗 Ollama Base URL: `{OLLAMA_BASE_URL}`")

    available_models = get_available_models(OLLAMA_BASE_URL)

    if available_models:
        selected_model = st.selectbox("Pilih Model Ollama", available_models)
        st.success(f"Model aktif: **{selected_model}**")
    else:
        selected_model = None
        st.warning("Ollama terhubung, tapi belum ada model. Jalankan `ollama pull ...` di host dulu.")

    if st.button("🔍 Cek Koneksi Ollama"):
        check_ollama_connection(OLLAMA_BASE_URL)

    st.markdown("---")

    if st.button("🗑️ Bersihkan Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

# ======================================================
# 6. MAIN CONTENT
# ======================================================
st.markdown(
    """
    <div class="main-header">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:24px;">💬</span>
            <h3 style="margin:0;color:#1e3a8a;">Konsultasi Akademik</h3>
        </div>
        <div style="background:#eff6ff;padding:5px 15px;border-radius:20px;
                    color:#2563eb;font-weight:bold;font-size:12px;">
            STATUS: ONLINE
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Halo, saya **SMARDOS**. "
                "Silakan pilih model AI di sidebar dan mulai berdiskusi."
            )
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(
        message["role"],
        avatar="🎓" if message["role"] == "assistant" else "👤"
    ):
        st.markdown(message["content"])

if selected_model:
    if prompt := st.chat_input("Tanyakan sesuatu pada SMARDOS"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("Sedang memproses"):
                response = generate_smardos_response(prompt, selected_model, OLLAMA_BASE_URL)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Pilih model di sidebar untuk memulai.")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    html, body, [class*="st-"] { font-family: 'Nunito', sans-serif; }

    /* Background app */
    .stApp { background-color: #0b1220; }  /* biar dark mode konsisten */

    /* Sidebar */
    [data-testid="stSidebar"]{
        background-color: #0f172a !important;
        border-right: 1px solid rgba(148,163,184,0.18);
    }

    /* Header bar looks */
    .main-header {
        background: #0f172a;
        padding: 1rem 2rem;
        border-bottom: 2px solid #2563eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-radius: 14px;
    }

    /* ====== FIX UTAMA: Chat bubble + teks ====== */
    /* Outer chat container */
    [data-testid="stChatMessage"]{
        border-radius: 14px !important;
        padding: 0.2rem !important;
        margin-bottom: 0.9rem !important;
        border: none !important;
        background: transparent !important;
    }

    /* Content box inside message (INI yang paling stabil) */
    [data-testid="stChatMessageContent"]{
        background: #ffffff !important;
        border-radius: 14px !important;
        padding: 1rem 1.1rem !important;
        border: 1px solid rgba(148,163,184,0.25) !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }

    /* Force text readable */
    [data-testid="stChatMessageContent"] p,
    [data-testid="stChatMessageContent"] li,
    [data-testid="stChatMessageContent"] span,
    [data-testid="stChatMessageContent"] div,
    [data-testid="stChatMessageContent"] strong,
    [data-testid="stChatMessageContent"] em,
    [data-testid="stChatMessageContent"] code{
        color: #0f172a !important;
        font-size: 15px;
        line-height: 1.65;
    }

    /* Links visible */
    [data-testid="stChatMessageContent"] a{
        color: #2563eb !important;
        text-decoration: underline;
        font-weight: 600;
    }

    /* Code blocks readable */
    [data-testid="stChatMessageContent"] pre{
        background: #0b1220 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        border: 1px solid rgba(148,163,184,0.25) !important;
        overflow-x: auto;
    }
    [data-testid="stChatMessageContent"] pre *{
        color: #e2e8f0 !important;
        font-size: 13px !important;
    }

    /* Optional: make chat input clean */
    [data-testid="stChatInput"] textarea{
        background: #111827 !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(148,163,184,0.25) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
