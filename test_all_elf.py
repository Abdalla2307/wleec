import os
paths = [
    '/usr/local/bin/blitzfetcher',
    '/usr/local/bin/stormtorrent',
    '/usr/local/bin/newsripper',
    '/usr/local/bin/mediaforge',
    '/usr/local/bin/ghostdrive'
]
for p in paths:
    if os.path.exists(p):
        try:
            with open(p, 'rb') as f:
                header = f.read(16)
                print(f"{p}: Magic={header[:4]}, Class={header[4]}, Data={header[5]}, OS/ABI={header[7]}")
        except Exception as e:
            print(f"{p}: Error {e}")
    else:
        print(f"{p}: Not found")
