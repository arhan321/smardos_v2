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
# 2. ADVANCED CUSTOM CSS (FIX KONTRAS + LOADING BUBBLE)
# ======================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    html, body, [class*="st-"] { font-family: 'Nunito', sans-serif; }

    /* Background app */
    .stApp { background-color: #0b1220; }

    /* Sidebar */
    [data-testid="stSidebar"]{
        background-color: #0f172a !important;
        border-right: 1px solid rgba(148,163,184,0.18);
    }

    /* Header */
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

    /* Chat message container */
    [data-testid="stChatMessage"]{
        border-radius: 14px !important;
        padding: 0.2rem !important;
        margin-bottom: 0.9rem !important;
        border: none !important;
        background: transparent !important;
    }

    /* Chat message content box (stabil di Streamlit) */
    [data-testid="stChatMessageContent"]{
        background: #ffffff !important;
        border-radius: 14px !important;
        padding: 1rem 1.1rem !important;
        border: 1px solid rgba(148,163,184,0.25) !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }

    /* Force readable text */
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

    /* Links */
    [data-testid="stChatMessageContent"] a{
        color: #2563eb !important;
        text-decoration: underline;
        font-weight: 600;
    }

    /* Code blocks */
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

    /* Chat input */
    [data-testid="stChatInput"] textarea{
        background: #111827 !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(148,163,184,0.25) !important;
    }

    /* ===== Loading bubble (assistant) ===== */
    .smardos-loading {
      background: #ffffff;
      border-radius: 14px;
      padding: 14px 16px;
      border: 1px solid rgba(148,163,184,0.25);
      box-shadow: 0 6px 18px rgba(0,0,0,0.12);
      color: #0f172a;
      font-size: 15px;
      line-height: 1.6;
      display: flex;
      gap: 10px;
      align-items: center;
    }

    .smardos-dots span{
      display:inline-block;
      width:7px;height:7px;
      margin:0 2px;
      border-radius:50%;
      background:#2563eb;
      animation: smardosBounce 1.2s infinite ease-in-out;
    }
    .smardos-dots span:nth-child(2){ animation-delay: .15s; }
    .smardos-dots span:nth-child(3){ animation-delay: .3s; }

    @keyframes smardosBounce {
      0%, 80%, 100% { transform: translateY(0); opacity: .35; }
      40% { transform: translateY(-4px); opacity: 1; }
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
    """GET {base_url}/api/tags"""
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=5)
        r.raise_for_status()
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def generate_smardos_response(user_input: str, model_name: str, base_url: str) -> str:
    """Generate response via langchain_ollama to Ollama HTTP endpoint."""
    try:
        from langchain_ollama import OllamaLLM
    except ModuleNotFoundError:
        return "Ollama (langchain_ollama) tidak tersedia di environment ini."

    llm = OllamaLLM(
        model=model_name,
        temperature=0.3,
        base_url=base_url,
        num_predict=350,  # biar lebih cepat & nggak kepanjangan
    )

    system_instructions = (
        "Kamu adalah SMARDOS (Smart Asisten Dosen), asisten akademik khusus perguruan tinggi.\n"
        "TUGAS UTAMA:\n"
        "1. Hanya jawab pertanyaan yang berkaitan dengan materi perkuliahan, teori akademik, atau metode penelitian.\n"
        "2. Jika pertanyaan TIDAK berkaitan dengan perkuliahan/pendidikan, tolak dengan sopan.\n"
        "3. Setiap jawaban WAJIB menyertakan referensi ilmiah di bagian akhir.\n"
        "4. Format referensi harus mencantumkan Link URL (Google Scholar/DOAJ/portal jurnal).\n"
        "5. Gunakan Bahasa Indonesia yang formal dan edukatif.\n"
        "6. Jawaban maksimal 6 paragraf, ringkas dan jelas.\n"
        "7. Jika memberikan kode/sintaks, WAJIB gunakan blok ```bahasa ... ``` agar rapi."
    )

    full_prompt = f"### Instruction:\n{system_instructions}\n\n### User Question:\n{user_input}\n\n### Response:"
    return llm.invoke(full_prompt)


def check_ollama_connection(base_url: str):
    """Cek koneksi ke Ollama dan tampilkan debug info."""
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
        "<h1 style='color:#e2e8f0;font-size:24px;font-weight:800;'>🎓 SMARDOS</h1>",
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
            <h3 style="margin:0;color:#e2e8f0;">Konsultasi Akademik</h3>
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
            placeholder = st.empty()

            # Bubble loading konsisten dengan UI
            placeholder.markdown(
                """
                <div class="smardos-loading">
                    <div class="smardos-dots">
                        <span></span><span></span><span></span>
                    </div>
                    <div><b>SMARDOS</b> sedang menyiapkan jawaban…</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Generate jawaban
            response = generate_smardos_response(prompt, selected_model, OLLAMA_BASE_URL)

            # Replace loading dengan jawaban
            placeholder.empty()
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Pilih model di sidebar untuk memulai.")

st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:12px;margin-top:50px;'>"
    "SMARDOS Local Intelligence"
    "</div>",
    unsafe_allow_html=True
)
