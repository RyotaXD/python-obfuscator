# 🛡️ Python Obfuscator & Compiler

Alat berbasis antarmuka baris perintah (CLI) untuk melindungi *source code* Python Anda. Script ini memungkinkan Anda untuk melakukan obfuscation pada kode Python standar atau mengkompilasinya langsung menjadi *Shared Object* (`.so`) berbasis C/C++ agar lebih sulit di-*reverse engineering*. Sangat optimal dijalankan pada lingkungan Termux (aarch64).

## ⚙️ Fitur Tersedia
* Obfuscate menggunakan kombinasi Marshal, Zlib, dan Base64 dengan output `.py`
* Obfuscate menggunakan metode MarshalV2 dengan output `.py`
* Konversi dan kompilasi kode Python ke C++ (`.cpp`), lalu dibuild menjadi file `.so`
* Konversi dan kompilasi kode Python ke C (`.c`), lalu dibuild menjadi file `.so`

## 📦 Persyaratan Sistem
* Python 3
* Clang / GCC (diperlukan untuk kompilasi fitur C/C++ ke `.so`)
* Modul Python: `Cython`, `rich` (jika menggunakan antarmuka berwarna)

## 🚀 Cara Install & Build (Termux / Linux)

Jalankan perintah berikut secara berurutan di terminal Anda:

```bash
# 1. Update dan upgrade sistem dasar
apt update && apt upgrade -y

# 2. Install Python dan Clang (compiler untuk C/C++)
pkg install python clang git -y

# 3. Install modul Python yang dibutuhkan
pip install Cython rich inquirer setuptools

# 4. Clone repositori ini
git clone https://github.com/RyotaXD/python-obfuscator

# 5. Masuk ke dalam direktori script
cd python-obfuscator

# 6. Jalankan script
python run.py
