import subprocess
import tempfile
from pathlib import Path

def execute_code(language_name, code, architecture='x86-64'):
    lang = language_name.lower()
    if 'assembly' in lang or 'asm' in lang or 'machine' in lang:
        return _compile_assembly(code, architecture)
    elif lang == 'c':
        return _compile_c(code)
    return {'success': False, 'output': '', 'error': f'Unsupported language: {language_name}'}

def _compile_c(code):
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        src = d / 'main.c'
        out = d / 'main'
        src.write_text(code)
        comp = subprocess.run(
            ['/usr/bin/gcc', '-Wall', str(src), '-o', str(out), '-lm'],
            capture_output=True, text=True, timeout=10
        )
        if comp.returncode != 0:
            return {'success': False, 'output': '', 'error': comp.stderr}
        run = subprocess.run(
            [str(out)],
            capture_output=True, text=True, timeout=5
        )
        return {'success': run.returncode == 0, 'output': run.stdout, 'error': run.stderr}


def _compile_assembly(code, architecture):
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        if architecture == 'x86-64':
            src = d / 'main.asm'
            obj = d / 'main.o'
            out = d / 'main'
            src.write_text(code)
            asm = subprocess.run(
                ['/usr/bin/nasm', '-f', 'elf64', str(src), '-o', str(obj)],
                capture_output=True, text=True, timeout=10
            )
            if asm.returncode != 0:
                return {'success': False, 'output': '', 'error': asm.stderr}
            lnk = subprocess.run(
                ['/usr/bin/ld', '-no-pie', str(obj), '-o', str(out)],
                capture_output=True, text=True, timeout=10
            )
            if lnk.returncode != 0:
                return {'success': False, 'output': '', 'error': lnk.stderr}
            run = subprocess.run(
                [str(out)],
                capture_output=True, text=True, timeout=5
            )
        elif architecture == 'arm64':
            src = d / 'main.s'
            obj = d / 'main.o'
            out = d / 'main'
            src.write_text(code)
            asm = subprocess.run(
                ['/usr/bin/aarch64-linux-gnu-as', '-o', str(obj), str(src)],
                capture_output=True, text=True, timeout=10
            )
            if asm.returncode != 0:
                return {'success': False, 'output': '', 'error': f'Assemble error:\n{asm.stderr}\n{asm.stdout}'}
            lnk = subprocess.run(
                ['/usr/bin/aarch64-linux-gnu-ld', '-o', str(out), str(obj)],
                capture_output=True, text=True, timeout=10
            )
            if lnk.returncode != 0:
                return {'success': False, 'output': '', 'error': f'Link error:\n{lnk.stderr}\n{lnk.stdout}'}
            run = subprocess.run(
                ['/usr/bin/qemu-aarch64-static', str(out)],
                capture_output=True, text=True, timeout=5
            )
        else:
            return {'success': False, 'output': '', 'error': f'Unknown architecture: {architecture}'}
        return {'success': run.returncode == 0, 'output': run.stdout, 'error': run.stderr}
