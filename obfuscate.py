#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import marshal
import zlib
import base64
import random
import shutil
import platform
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension  # Python < 3.12 fallback
from Cython.Build import cythonize
try:
    from rich.console import Console
    import inquirer
except ImportError:
    print("Modul UI belum lengkap, bro! Ketik dulu: pip install rich inquirer")
    sys.exit(1)

console = Console()


def get_system_arch():
    machine = platform.machine().lower()
    if "aarch64" in machine or "arm64" in machine:
        return "aarch64 (64-bit)"
    if "x86_64" in machine or "amd64" in machine:
        return "x86_64 (64-bit)"
    if "64" in machine:
        return "aarch64 (64-bit)"
    return "armv7 (32-bit)"


def check_dependencies(require_clang=False, require_cpp=False):
    if not shutil.which("cython"):
        console.print("[bold red][!] Cython belum ke-install! Ketik: pip install cython[/bold red]")
        sys.exit(1)
    if require_clang:
        compiler = "clang++" if require_cpp else "clang"
        if not shutil.which(compiler):
            console.print(f"[bold red][!] Compiler {compiler} nggak ketemu! Ketik: pkg install clang[/bold red]")
            sys.exit(1)
        if not shutil.which("python3-config"):
            console.print("[bold red][!] python3-config nggak ada! Ketik: pkg install python-dev[/bold red]")
            sys.exit(1)


def show_header():
    console.clear()
    console.print("\n[bold cyan]P Y T H O N   O B F U S C A T O R[/bold cyan]")
    console.print("[bold white]WhatsApp[/bold white] [bold red]:[/bold red] [bold green]62895428421402[/bold green]")
    console.print("[bold white]Author[/bold white]   [bold red]:[/bold red] [bold white]Bayu Putra Tama[/bold white]")
    console.print("[bold white]GitHub[/bold white]   [bold red]:[/bold red] [dim white]https://github.com/RyotaXD[/dim white]")
    console.print("[bold white]Facebook[/bold white] [bold red]:[/bold red] [dim white]https://www.facebook.com/ryotaaaaaaaaaaaaa[/dim white]")
    console.print("[bold white]" + "─" * 65 + "[/bold white]")
    console.print("                     [bold white][ Welcome ^_^ ][/bold white]\n")


def ask_target_file():
    from rich.panel import Panel
    from rich import box
    console.print(Panel("Ketik nama file yang mau diobfuscate (contoh: bot.py)", title="[bold yellow][ SETUP TARGET FILE ][/bold yellow]", title_align="left", border_style="yellow", box=box.SQUARE, expand=False))
    questions = [inquirer.Text('target', message="Nama file")]
    ans = inquirer.prompt(questions)
    target = ans['target'].strip() if ans else ""
    if not os.path.exists(target):
        console.print(f"\n[bold red][-] Waduh, file '{target}' nggak ketemu di folder ini, bro![/bold red]")
        time.sleep(1.5)
        return None
    return target


def run_live_pipeline(task_title, steps_list):
    console.print(f"\n[bold cyan][[/bold cyan] [bold yellow]PROSES: {task_title.upper()}[/bold yellow] [bold cyan]][/bold cyan]")
    total = len(steps_list)
    for index, (desc, action) in enumerate(steps_list, 1):
        is_last = (index == total)
        branch = "└──" if is_last else "├──"
        sub_branch = "    " if is_last else "│   "
        step_text = f"[bold cyan]{branch}[/bold cyan] [dim white]Langkah {index}/{total}[/dim white] [cyan]{desc}[/cyan]"
        info = None
        try:
            with console.status(f"{step_text} [yellow]Lagi proses[/yellow]", spinner="dots", spinner_style="bold cyan"):
                time.sleep(0.5)
                if action:
                    info = action()
            console.print(f"{step_text} [bold green][BERES][/bold green]")
            if info:
                console.print(f"[bold cyan]{sub_branch}[/bold cyan] [dim white]{info}[/dim white]")
        except Exception as e:
            console.print(f"{step_text} [bold red][GAGAL][/bold red]")
            console.print(f"[bold red]{sub_branch} Masalah: {e}[/bold red]")
            raise e
    console.print()


def build_marshal_zlib_payload(code):
    """compile -> marshal -> zlib -> base64, rendered as an executable stub."""
    compiled = compile(code, '<RyotaXD>', 'exec')
    marshaled = marshal.dumps(compiled)
    compressed = zlib.compress(marshaled, 9)
    encoded = base64.b64encode(compressed).decode('utf-8')
    return (
        "#!/usr/bin/env python3\n"
        "# Encrypted by RyotaXD\n"
        "import marshal,zlib,base64\n"
        f"exec(marshal.loads(zlib.decompress(base64.b64decode('{encoded}'.encode('utf-8')))))"
    )


def build_marshal_v2_payload(code, key=None):
    """compile -> marshal -> xor -> zlib -> base85, rendered as an executable stub.

    Fixed: previously this XORed the *source* and compiled the result in
    'eval' mode, which is a SyntaxError for almost any script (XORed bytes
    are not valid source, and multi-statement scripts are not valid in
    'eval'). The stub also never used the injected key, so even a
    "successful" run produced output that could not decode itself.
    Order now: compile original code -> marshal -> XOR marshaled bytes ->
    compress -> base85; stub reverses it.
    """
    if key is None:
        key = random.randint(15, 200)
    compiled = compile(code, '<RyotaXD_V2>', 'exec')
    marshaled = marshal.dumps(compiled)
    xored = bytes(b ^ key for b in marshaled)
    compressed = zlib.compress(xored, 9)
    b85 = base64.b85encode(compressed).decode('utf-8')
    return (
        "#!/usr/bin/env python3\n"
        "# Obfuscate by RyotaXD MarshalV2\n"
        "import marshal, zlib, base64\n"
        f"k = {key}\n"
        f"b = base64.b85decode('{b85}')\n"
        "z = zlib.decompress(b)\n"
        "m = marshal.loads(bytes(x ^ k for x in z))\n"
        "exec(m)\n"
    )


def obfuscate_marshal_zlib_base64():
    target = ask_target_file()
    if not target: return
    out_name = os.path.splitext(target)[0] + '_enc.py'
    data = {}
    def step_1():
        with open(target, 'r', encoding='utf-8') as f:
            data['code'] = f.read()
        return f"Ngebaca {len(data['code'])} bytes dari source"
    def step_2():
        data['payload'] = build_marshal_zlib_payload(data['code'])
        return "Bikin Python AST bytecode"
    def step_3():
        return f"Dikompres & dienkripsi ({len(data['payload'])} karakter)"
    def step_4():
        with open(out_name, 'w', encoding='utf-8') as f:
            f.write(data['payload'])
        return f"File output: {out_name}"
    steps = [
        ("Membaca dan menganalisis script asli", step_1),
        ("Kompilasi kode mentah ke bytecode", step_2),
        ("Bungkus pakai Marshal, Zlib, dan Base64", step_3),
        ("Nulis hasil obfuscate ke file baru", step_4)
    ]
    try:
        run_live_pipeline("Enkripsi Standar Berlapis", steps)
        console.print(f"[bold green][SUCCESS] File aman terbungkus: [white]{out_name}[/white][/bold green]")
    except Exception as err:
        console.print(f"\n[bold red][ERROR] Proses berhenti di tengah jalan.[/bold red]")
    input("\n[Pencet Enter buat lanjut...]")


def obfuscate_marshal_v2():
    target = ask_target_file()
    if not target: return
    out_name = os.path.splitext(target)[0] + '_v2.py'
    data = {}
    def step_1():
        with open(target, 'r', encoding='utf-8') as f:
            data['code'] = f.read()
        return "Target udah masuk memori"
    def step_2():
        data['key'] = random.randint(15, 200)
        data['payload'] = build_marshal_v2_payload(data['code'], key=data['key'])
        return f"Kunci XOR acak disuntik: {data['key']}"
    def step_3():
        return "Dipacking ulang pakai Base85"
    def step_4():
        with open(out_name, 'w', encoding='utf-8') as f:
            f.write(data['payload'])
        return f"File eksekutor jadi: {out_name}"
    steps = [
        ("Menyiapkan target file sumber", step_1),
        ("Suntik mutasi XOR & kompilasi bytecode", step_2),
        ("Kompresi dan enkripsi pakai Base85", step_3),
        ("Bikin file eksekutor versi 2", step_4)
    ]
    try:
        run_live_pipeline("Mesin Dinamis Marshal Versi 2", steps)
        console.print(f"[bold green][SUCCESS] File V2 berhasil dikunci: [white]{out_name}[/white][/bold green]")
    except Exception as err:
        console.print(f"\n[bold red][ERROR] Proses berhenti di tengah jalan.[/bold red]")
    input("\n[Pencet Enter buat lanjut...]")


def handle_cython_process(mode_cpp=True):
    check_dependencies()
    target = ask_target_file()
    if not target: return
    ext = ".cpp" if mode_cpp else ".c"
    main_file = os.path.splitext(target)[0] + ext
    nama_modul = os.path.splitext(os.path.basename(target))[0]
    build_choice = inquirer.prompt([
        inquirer.List(
            'mode',
            message=f"Pilih mode build untuk file {ext}",
            choices=[
                'Build Otomatis',
                'Build Manual'
            ]
        )
    ])
    if not build_choice: return
    is_auto = 'Otomatis' in build_choice['mode']
    if is_auto:
        def step_1():
            import subprocess
            flag = "--cplus" if mode_cpp else ""
            cmd = ["cython", "-3"]
            if flag: cmd.append(flag)
            cmd.extend([target, "-o", main_file])
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Berhasil generate file {ext}: {main_file}"
        def step_2():
            try:
                extra_compile_args = ["-O3", "-flto", "-fvisibility=hidden"]
                extra_link_args = ["-O3", "-flto", "-Wl,--strip-all"]
                setup(
                    name=nama_modul,
                    ext_modules=cythonize(
                        Extension(
                            name=nama_modul,
                            sources=[main_file],
                            extra_compile_args=extra_compile_args,
                            extra_link_args=extra_link_args
                        ),
                        compiler_directives={
                            'boundscheck': False,
                            'wraparound': False,
                            'initializedcheck': False
                        }
                    ),
                    script_args=["build_ext", "--inplace", "--force", "-j", "5"]
                )
            except Exception as e:
                raise RuntimeError(str(e))
            return "Kompilasi Max-Optimized Cythonize selesai"
        def step_3():
            if os.path.exists(main_file):
                try: shutil.rmtree("build", ignore_errors=True)
                except Exception: pass
                try: os.remove(main_file)
                except Exception: pass
            return "Pembersihan direktori build dan file source sukses"
        steps = [
            (f"Transpile Python ke format {ext[1:].upper()}", step_1),
            ("Build Extension Max-Optimized (-O3, -flto, Strip)", step_2),
            ("Pembersihan file sampah otomatis", step_3)
        ]
        try:
            run_live_pipeline(f"Python ke {ext[1:].upper()} (.so Otomatis)", steps)
            console.print(f"\n[bold green][SUCCESS] Modul Shared Library (.so) Max-Optimized siap digunakan![/bold green]")
            console.print(f"[cyan]Cara import di script lain:[/cyan]")
            console.print(f"  [yellow]import {nama_modul}[/yellow]")
            console.print(f"  [yellow]{nama_modul}.main()[/yellow]")
        except Exception as err:
            console.print(f"\n[bold red][ERROR] Gagal proses: {err}[/bold red]")
            console.print("Install Semua Module Dengan Mengetik : pip install -r requirements.txt")
    else:
        import subprocess
        flag = "--cplus" if mode_cpp else ""
        cmd = ["cython", "-3"]
        if flag: cmd.append(flag)
        cmd.extend([target, "-o", main_file])
        try:
            subprocess.run(cmd, check=True)
            print("\n" + "="*50)
            print("INSTRUKSI CARA BUILD MANUAL KE .SO (MAX OPTIMIZED)")
            print("="*50)
            print("1. Buat file baru bernama 'setup.py' di folder yang sama.")
            print("2. Masukkan kode berikut ke dalam 'setup.py':\n")
            print("from setuptools import setup, Extension")
            print("from Cython.Build import cythonize\n")
            print(f"setup(")
            print(f"    name='{nama_modul}',")
            print(f"    ext_modules=cythonize(")
            print(f"        Extension(")
            print(f"            name='{nama_modul}',")
            print(f"            sources=['{main_file}'],")
            print(f"            extra_compile_args=['-O3', '-flto', '-fvisibility=hidden'],")
            print(f"            extra_link_args=['-O3', '-flto', '-Wl,--strip-all']")
            print(f"        ),")
            print(f"        compiler_directives={{'boundscheck': False, 'wraparound': False, 'initializedcheck': False}}")
            print(f"    )")
            print(")\n")
            print("3. Jalankan perintah terminal berikut untuk mem-build-nya:")
            print("   python3 setup.py build_ext --inplace")
            print("="*50 + "\n")
        except Exception as e:
            console.print(f"\n[bold red][ERROR] Gagal generate file source: {e}[/bold red]")
    input("\n[Pencet Enter buat lanjut...]")


def obfuscate_python_to_bin():
    check_dependencies(require_clang=True)
    target = ask_target_file()
    if not target: return
    temp_c = os.path.splitext(target)[0] + '_temp.c'
    out_bin = os.path.splitext(target)[0] + '.bin'
    def step_1():
        import subprocess
        subprocess.run(["cython", "-3", "--embed", target, "-o", temp_c], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "Transpile C dengan Embed Python selesai"
    def step_2():
        import subprocess
        arch = get_system_arch()
        cflags = subprocess.check_output(["python3-config", "--cflags"]).decode('utf-8').strip().split()
        cflags = [f for f in cflags if not f.startswith('-fno-semantic-interposition')]
        try:
            ldflags = subprocess.check_output(["python3-config", "--embed", "--ldflags"]).decode('utf-8').strip().split()
        except Exception:
            ldflags = subprocess.check_output(["python3-config", "--ldflags"]).decode('utf-8').strip().split()
        cmd = ["clang", "-O3", "-flto", "-fvisibility=hidden", "-fno-ident", "-Wl,--strip-all", temp_c, "-o", out_bin] + cflags + ldflags
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        finally:
            if os.path.exists(temp_c):
                os.remove(temp_c)
        return f"Build Biner Maksimal untuk {arch}"
    def step_3():
        if os.path.exists(temp_c):
            os.remove(temp_c)
        return "File sampah temp C sudah dibersihkan"
    steps = [
        ("Transpile Python ke C (Embed Mode)", step_1),
        ("Kompilasi ke Eksekutor Biner via Clang", step_2),
        ("Bersih-bersih file temp", step_3)
    ]
    try:
        run_live_pipeline("Convert Python ke .bin", steps)
        console.print(f"\n[bold green][SUCCESS] File .bin selesai compile![/bold green]")
        console.print(f"[cyan]Cara jalankannya di terminal :[/cyan]")
        console.print(f"  [yellow]chmod +x {out_bin}[/yellow]")
        console.print(f"  [yellow]./{out_bin}[/yellow]")
    except Exception as err:
        console.print(f"\n[bold red][ERROR] Gagal build biner: {err}[/bold red]")
        console.print("Pastikan clang & python-dev sudah terinstall (pkg install clang python-dev)")
    input("\n[Pencet Enter buat lanjut...]")


def main():
    while True:
        show_header()
        arch = get_system_arch()
        arch_parts = arch.split(" (")
        if len(arch_parts) == 2:
            arch_base = arch_parts[0]
            arch_bit = "(" + arch_parts[1]
        else:
            arch_base = arch
            arch_bit = ""
        console.print(f"[bold white]Sistem[/bold white] [bold red]:[/bold red] [bold magenta]{arch_base}[/bold magenta] [bold cyan]{arch_bit}[/bold cyan]\n")
        choices = [
            '1. Obfuscate Marshal,Zlib,Base64  .py',
            '2. Obfuscate MarshalV2            .py',
            '3. Python ke C++                  .cpp / .so',
            '4. Python ke C                    .c / .so',
            '5. Python ke Eksekutor Biner      .bin',
            '0. Keluar / Tutup Tool'
        ]
        questions = [inquirer.List('menu', message="Pilih Menu", choices=choices)]
        answers = inquirer.prompt(questions)
        if not answers:
            break
        pilihan = answers['menu'][0]
        if pilihan.startswith('1'):
            obfuscate_marshal_zlib_base64()
        elif pilihan.startswith('2'):
            obfuscate_marshal_v2()
        elif pilihan.startswith('3'):
            handle_cython_process(mode_cpp=True)
        elif pilihan.startswith('4'):
            handle_cython_process(mode_cpp=False)
        elif pilihan.startswith('5'):
            obfuscate_python_to_bin()
        elif pilihan.startswith('0'):
            console.print("\n[bold cyan][!] Sesi ditutup. Sampai jumpa lagi, bro![/bold cyan]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold red][!] Dimatikan paksa. Cabut dulu![/bold red]")
        sys.exit(0)
