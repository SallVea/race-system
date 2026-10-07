<div align="center">

# 🏎️ VeloX Race Master
**Roblox Mountain Racing Management System**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Terminal](https://img.shields.io/badge/CLI-Terminal-black?style=for-the-badge&logo=gnu-bash)
![Discord](https://img.shields.io/badge/Discord-Webhook-5865F2?style=for-the-badge&logo=discord)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

*Skrip interaktif berbasis CLI (Command Line Interface) untuk mengelola poin turnamen balapan dan mengirimkan hasilnya secara otomatis ke Discord dengan format Embed yang mewah.*

</div>

---

## ✨ Fitur Utama
- 🎨 **Terminal UI Keren:** Menggunakan library `rich` untuk tampilan warna-warni, tabel dengan border neon, dan indikator proses interaktif.
- 🕹️ **Menu Navigasi Mudah:** Pilih opsi dan nama pemain cukup dengan tombol panah (`↑` / `↓`) langsung di dalam terminal.
- 📊 **Auto-Save Data:** Data balapan otomatis tersimpan ke `velox_data.json` dengan aman. Tidak perlu takut kehilangan progres jika aplikasi tertutup.
- 🔔 **Discord Integration:** Mengirim tabel klasemen dengan *Embed* mewah berbalut emoji trofi 🥇🥈🥉, lengkap dengan fitur *ping* `@everyone` otomatis.
- 🏆 **Dua Mode Kompetisi:** Mendukung Sistem Championship (akumulasi poin) dan Standalone (perhitungan jumlah kemenangan/Win).

---

## 🛠️ Persyaratan Sistem
- Sistem Operasi Linux / WSL / MacOS
- **Python 3.x** terinstall di sistem
- Library Python: `rich` dan `requests`

---

## 🚀 Cara Menjalankan Program

Buka terminal Anda, masuk ke direktori tempat file disimpan, lalu jalankan salah satu perintah berikut:

**Cara 1 (Rekomendasi - Menggunakan Launcher Bash):**
```bash
cd ~/perhitungan
bash run_velox.sh
```

**Cara 2 (Menjalankan langsung via Python):**
```bash
cd ~/perhitungan
python3 velox.py
```

---

## 📖 Panduan Penggunaan

Saat pertama kali dijalankan, Anda akan diminta untuk memasukkan **Discord Webhook URL**. Pastikan Anda sudah membuat Webhook di channel Discord Anda (*Pengaturan Server -> Integrasi -> Webhooks*).

Program ini memiliki **2 Mode Utama**:

### ⚡ Mode A: Sistem Poin (Championship / Akumulasi)
Gunakan mode ini jika Anda mengadakan turnamen balap yang terdiri dari beberapa race (sesi), dan pemenangnya ditentukan dari **Total Poin Kumulatif**.

1. **Input Nama Pemain:** Masukkan nama-nama peserta yang ikut turnamen. Ketik `selesai` jika sudah.
2. **Konfigurasi Poin:** Tentukan berapa poin untuk Juara 1, Juara 2, dst. (Tekan Enter langsung untuk memakai nilai default: 100, 80, 60...).
3. **Tambah Sesi Baru:** Masukkan nama sesi balapan (misal: "Race 1").
4. **Pilih Posisi:** Gunakan tombol panah (`↑` / `↓`) pada keyboard lalu tekan `Enter` untuk memilih siapa Juara 1, Juara 2, dst.
5. **Kirim ke Discord:** Setelah menginput sesi, sistem akan otomatis mengakumulasi total poin tiap pemain (beserta histori poin per sesi), dan Anda bisa langsung mengirim hasilnya ke Discord.

### 🏁 Mode B: Sistem Single (Standalone Per-Sesi)
Gunakan mode ini jika Anda bermain secara kasual, di mana poin tidak diakumulasi, melainkan hanya ingin menghitung **berapa kali seorang pemain menjadi Juara 1 (Win)** di berbagai sesi.

1. **Input Sesi Baru:** Masukkan nama sesi (misal: "Sesi Malam 1").
2. **Input Posisi:** Ketik nama juara 1, juara 2, dst. Ketik `selesai` untuk berhenti menginput di sesi tersebut.
3. **Ulangi Input:** Lanjutkan untuk bermain di "Sesi 2", "Sesi 3", dan seterusnya.
4. **Selesai & Kirim Hasil:** Sistem akan otomatis menghitung (merekap) siapa saja yang memenangkan Juara 1 terbanyak dari seluruh sesi tersebut, dan mengirimkan tabel **🏆 Rekap Kemenangan** sekaligus ke Discord.

---

## ⌨️ Kontrol Keyboard

| Tombol | Fungsi |
|:---:|---|
| `↑` / `↓` | Memilih menu atau memilih nama pemain |
| `Enter` | Mengonfirmasi pilihan |
| `q` / `ESC` | Batal atau kembali ke menu sebelumnya |

---

## 📜 Lisensi

Proyek ini menggunakan **[MIT License](LICENSE)**. 

Anda sepenuhnya bebas untuk menggunakan, menyalin, memodifikasi, menggabungkan, menerbitkan, mendistribusikan, mensublisensikan, dan/atau menjual salinan perangkat lunak ini secara gratis, selama Anda tetap menyertakan pemberitahuan hak cipta asli.

<div align="center">
  <br>
  <i><b>Race Management System • Created by Sall</b></i>
</div>
