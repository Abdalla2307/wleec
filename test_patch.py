import subprocess
path = '/usr/local/bin/blitzfetcher'
try:
    with open(path, 'r+b') as f:
        f.seek(7)
        f.write(b'\x00')
    print("Patched successfully!")
    res = subprocess.run([path, '--version'], capture_output=True, text=True)
    print("Output:", res.stdout)
    print("Error:", res.stderr)
    print("Code:", res.returncode)
except Exception as e:
    print("Error:", e)
