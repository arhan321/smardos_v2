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
# 2. ADVANCED CUSTOM CSS
# ======================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&display=swap');

    .stApp { background-color: #f8fafc; }
    html, body, [class*="st-"] { font-family: 'Nunito', sans-serif; }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }

    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        text-align: left;
        padding: 10px 15px;
    }

    [data-testid="stChatMessage"] {
        border-radius: 15px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
    }

    .main-header {
        background: white;
        padding: 1rem 2rem;
        border-bottom: 2px solid #2563eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================================================
# 3. KONFIG OLLAMA
# ======================================================
# Default aman untuk Docker (dengan extra_hosts host.docker.internal:host-gateway)
# Bisa dioverride lewat docker-compose environment: OLLAMA_BASE_URL
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")

# ======================================================
# 4. LOGIC FUNCTIONS
# ======================================================
@st.cache_data(ttl=300)
def get_available_models(base_url: str):
    """
    Ambil daftar model dari Ollama HTTP API:
    GET {base_url}/api/tags
    """
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=5)
        r.raise_for_status()
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def generate_smardos_response(user_input: str, model_name: str, base_url: str) -> str:
    """
    Generate response menggunakan langchain_ollama (langsung ke HTTP endpoint Ollama).
    """
    try:
        from langchain_ollama import OllamaLLM
    except ModuleNotFoundError:
        return "Ollama (langchain_ollama) tidak tersedia di environment ini."

    llm = OllamaLLM(
        model=model_name,
        temperature=0.3,
        base_url=base_url
    )

    # Guardrails / instruksi sistem
    system_instructions = (
        "Kamu adalah SMARDOS (Smart Asisten Dosen), asisten akademik khusus perguruan tinggi.\n"
        "TUGAS UTAMA:\n"
        "1. Hanya jawab pertanyaan yang berkaitan dengan materi perkuliahan, teori akademik, atau metode penelitian, dan referensi jurnal atau artikel.\n"
        "2. Jika pertanyaan TIDAK berkaitan dengan materi perkuliahan atau pendidikan (misal: pertanyaan random, hiburan, atau hal aneh), "
        "tolak dengan sopan dan katakan bahwa kamu hanya fokus pada bantuan mata kuliah.\n"
        "3. Setiap jawaban WAJIB menyertakan referensi jurnal ilmiah yang valid di bagian akhir jawaban.\n"
        "4. Format referensi harus mencantumkan Link URL (misal ke Google Scholar, DOAJ, atau portal jurnal lainnya).\n"
        "5. Gunakan Bahasa Indonesia yang formal dan edukatif."
    )

    full_prompt = f"### Instruction:\n{system_instructions}\n\n### User Question:\n{user_input}\n\n### Response:"
    return llm.invoke(full_prompt)


def check_ollama_connection(base_url: str):
    """
    Cek koneksi ke Ollama dan tampilkan debug info.
    """
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=5)
        st.write("✅ Status:", r.status_code)
        st.write("✅ Endpoint:", f"{base_url}/api/tags")
        st.json(r.json())
    except Exception as e:
        st.error(f"❌ Gagal konek ke Ollama: {e}")
        st.info(
            "Checklist cepat:\n"
            "1) Pastikan Ollama jalan di HOST: `ollama serve`\n"
            "2) Pastikan bisa diakses: `curl http://<HOST>:11434/api/tags`\n"
            "3) Kalau pakai Docker: pastikan OLLAMA_HOST di host bind 0.0.0.0\n"
            "   contoh: `export OLLAMA_HOST=0.0.0.0:11434` lalu `ollama serve`"
        )

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
        st.error("Model Ollama tidak ditemukan. Pastikan Ollama server berjalan di host dan dapat diakses dari container.")

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
    st.warning("Jalankan Ollama dan pilih model untuk memulai.")

st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:12px;margin-top:50px;'>"
    "SMARDOS Local Intelligence"
    "</div>",
    unsafe_allow_html=True
)
