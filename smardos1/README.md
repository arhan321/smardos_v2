# 🎓 CD SMARDOS - _Smart Asisten Dosen 🤖✨_

**SMARDOS (Smart Asisten Dosen)** adalah platform bimbingan akademik berbasis kecerdasan buatan (AI) yang dirancang untuk menjadi asisten digital bagi mahasiswa. Aplikasi ini berfungsi sebagai **konsultan akademik 24/7** yang membantu membedah **materi perkuliahan** kompleks, **riset jurnal**, hingga metodologi penelitian. SMARDOS hadir untuk menghadirkan pendidikan tinggi yang lebih inklusif, memudahkan mahasiswa mendapatkan bimbingan instan tanpa terkendala jam kerja dosen, sehingga mempercepat proses belajar dan penyelesaian tugas akhir.

## 🚀 Pilar Fitur Unggulan

- **⚡ Akselerasi Respons:** Sistem AI yang mampu memberikan jawaban dan referensi akademik secara instan, menghilangkan hambatan waktu dalam konsultasi tradisional.
- **📖 Cakupan Wawasan Akademik:** Memiliki kemampuan analisis mendalam terhadap berbagai topik, mulai dari Data Mining, Machine Learning, hingga tata cara penulisan karya ilmiah yang baku.
- **🎯 Asistensi Personal & Sistematis:** Penjelasan yang diberikan disusun secara terstruktur guna membantu mahasiswa memahami benang merah dari setiap persoalan akademik yang ditanyakan.

## 🛠️ Panduan Lengkap Instalasi & Konfigurasi Lokal

Ikuti langkah-langkah mendetail berikut untuk menjalankan SMARDOS di lingkungan lokal Anda:

1. **Duplikasi repositori**
   Langkah awal, salin seluruh file proyek ke mesin lokal Anda menggunakan Git:

   ```bash
   git clone -----
   cd SMARDOS
   ```

2. **Standarisasi Lingkungan (Virtual Environment)**
   Sangat disarankan untuk menggunakan Virtual Environment agar dependensi tidak berbenturan dengan proyek lain:

   ### Pengguna Windows

   ```bash
   python -m venv venv

   .\venv\Scripts\activate
   ```

   ### Pengguna macOS/Linux

   ```bash
   python3 -m venv venv

   source venv/bin/activate
   ```

3. **Pemasangan Pustaka Pendukung**
   Pasang semua paket Python yang diperlukan yang terdaftar dalam file **requirements.txt**:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Konfigurasi Variabel Lingkungan:**
   Buat file baru bernama **.env** di root direktori proyek, lalu masukkan kredensial API Azure Anda:

   ```env
   AZURE_QNA_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com/
   AZURE_QNA_KEY=masukkan_api_key_anda_di_sini
   CONFIDENCE_THRESHOLD=0.5
   ```

5. **Inisialisasi Server:**
   Setelah semua siap, jalankan server Flask dengan perintah berikut:

   ```bash
   flask run
   ```

## 🗂️ Anatomi Struktur Proyek

```
SMARDOS/
├── app/
│   ├── static/          # Aset statis: Logo Biru, CSS kustom, & Favicon 🎓
│   ├── templates/       # Berkas HTML (Halaman Utama & Ruang Chat)
│   ├── main/            # Logika Blueprint untuk rute navigasi
│   └── services/        # Engine integrasi API Microsoft Azure
├── datasets/            # Basis pengetahuan (Knowledge Base) akademik
├── .env                 # Kunci rahasia & konfigurasi lingkungan
├── config.py            # Pengaturan global aplikasi
├── requirements.txt     # Daftar dependensi modul Python
└── run.py               # Berkas utama untuk menjalankan aplikasi
```

## 🔗 Pratinjau Langsung

Jelajahi ekosistem SMARDOS melalui tautan berikut:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)
