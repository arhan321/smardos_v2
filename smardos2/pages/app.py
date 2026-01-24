import os
import streamlit as st
import requests 
import PyPDF2
from streamlit_mic_recorder import mic_recorder

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

    /* Sidebar & Header (Tetap Sama) */
    [data-testid="stSidebar"]{ background-color: #0f172a !important; border-right: 1px solid rgba(148,163,184,0.18); }
    .main-header {
        background: #0f172a; padding: 1rem 2rem; border-bottom: 2px solid #2563eb;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; border-radius: 14px;
    }

    /* Chat Message Styling (Tetap Sama) */
    [data-testid="stChatMessage"]{ border-radius: 14px !important; padding: 0.2rem !important; margin-bottom: 0.9rem !important; background: transparent !important; }
    [data-testid="stChatMessageContent"]{
        background: #ffffff !important; border-radius: 14px !important; padding: 1rem 1.1rem !important;
        border: 1px solid rgba(148,163,184,0.25) !important; box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    }
    [data-testid="stChatMessageContent"] p, [data-testid="stChatMessageContent"] li { color: #0f172a !important; font-size: 15px; }

    /* ====================================================== */
    /* REVISI INPUT BAR: HORIZONTAL & STICKY BOTTOM           */
    /* ====================================================== */

    /* Container Utama Bar Input */
    .input-container-fixed {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 80%; /* Sesuaikan dengan lebar chat area Anda */
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background: #0b1220; /* Menyamakan dengan background app */
    }

    /* Mengecilkan Uploader Dokumen agar hanya Ikon */
    [data-testid="stFileUploader"] {
        width: fit-content !important;
        min-width: 40px !important;
    }
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
        min-height: unset !important;
        border: none !important;
        background: transparent !important;
    }
    [data-testid="stFileUploader"] section div {
        display: none; /* Sembunyikan instruksi "Drag & Drop" */
    }

    /* Memperbaiki tampilan Chat Input Streamlit di dalam container */
    [data-testid="stChatInput"] {
        padding: 0 !important;
    }

    /* Sembunyikan label widget agar tidak makan space */
    [data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* Styling mic recorder agar sejajar */
    .stMicRecorder {
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    /* Penyesuaian agar chat history tidak tertutup bar input */
    .stChatFloatingInputContainer {
        background-color: transparent !important;
        bottom: 20px !important;
    }

    /* Loading Animation (Tetap Sama) */
    .smardos-dots span {
        display:inline-block; width:7px; height:7px; margin:0 2px;
        border-radius:50%; background:#2563eb;
        animation: smardosBounce 1.2s infinite ease-in-out;
    }
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

import io
try:
    from PyPDF2 import PdfReader
    # Tambahkan speech_to_text di sini
    from streamlit_mic_recorder import mic_recorder, speech_to_text
except ImportError:
    st.error("Mohon install library tambahan: pip install PyPDF2 streamlit-mic-recorder")

def extract_text_from_file(uploaded_file):
    """Ekstraksi teks dari berbagai format dokumen."""
    text = ""
    try:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
    return text

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

if "voice_consumed" not in st.session_state:
    st.session_state.voice_consumed = False

if "last_voice_text" not in st.session_state:
    st.session_state.last_voice_text = ""

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
    avatar = "🎓" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if selected_model:
    # Container tetap di bawah menggunakan CSS class
    st.markdown('<div class="input-container-fixed">', unsafe_allow_html=True)
    
    col_upload, col_input, col_voice = st.columns([0.07, 0.86, 0.07])
    
    with col_upload:
        uploaded_file = st.file_uploader("📎", type=['pdf', 'txt'], label_visibility="collapsed", key="doc_upload")

    with col_voice:
        # Gunakan key unik dan tangkap outputnya
        text_from_voice = speech_to_text(
            language='id', 
            start_prompt="🎤", 
            stop_prompt="🛑", 
            key='speech_input_widget', # Key harus spesifik
            use_container_width=False
        )

    with col_input:
        prompt = st.chat_input("Tanyakan sesuatu pada SMARDOS...", key="chat_input_widget")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # --- LOGIKA PENGIRIMAN PESAN (Satu Gerbang) ---
    # Inisialisasi variabel penampung agar tidak dobel
    final_user_msg = None

    # Cek mana yang memberikan input
    if prompt:
        final_user_msg = prompt
    elif (
        text_from_voice
        and not st.session_state.voice_consumed
        and text_from_voice != st.session_state.last_voice_text
        ):
        final_user_msg = text_from_voice
        st.session_state.voice_consumed = True
        st.session_state.last_voice_text = text_from_voice

    # Eksekusi hanya jika ada pesan baru yang valid
    if final_user_msg:
        final_context = ""
        if uploaded_file:
            with st.status("Menganalisis dokumen...", expanded=False):
                file_content = extract_text_from_file(uploaded_file)
                final_context = f"\n<CONTEXT_DOKUMEN>\n{file_content}\n</CONTEXT_DOKUMEN>\n"

        full_prompt_to_ai = f"{final_context} Pertanyaan User: {final_user_msg}"

        # Simpan ke history
        st.session_state.messages.append({"role": "user", "content": final_user_msg})
        
        # Tampilkan di UI segera
        with st.chat_message("user", avatar="👤"):
            st.markdown(final_user_msg)
            if uploaded_file: st.caption(f"📁 Terlampir: {uploaded_file.name}")

        # Respon AI
        with st.chat_message("assistant", avatar="🎓"):
            placeholder = st.empty()
            placeholder.markdown("🔍 **SMARDOS sedang menyusun jawaban akademik...**")
            
            response = generate_smardos_response(full_prompt_to_ai, selected_model, OLLAMA_BASE_URL)
            
            placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # PENTING: Paksa rerun agar widget voice ter-reset dan tidak mengirim teks yang sama lagi
        st.session_state.voice_consumed = False
        st.rerun()       
else:
    st.info("Pilih model di sidebar untuk memulai.")

st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:12px;margin-top:50px;'>"
    "SMARDOS Local Intelligence"
    "</div>",
    unsafe_allow_html=True
)

