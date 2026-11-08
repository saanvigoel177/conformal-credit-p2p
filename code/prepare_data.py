"""Prepare the workspace the notebooks read from.

1. Decompresses the Lending Club extracts shipped as .csv.gz in workspace/ and checks
   their SHA-256 against workspace/extra_data/raw_manifest.json (and the values below).
2. Downloads the Prosper snapshot (not redistributed: no licence), normalises its line
   endings and checks its SHA-256 (fce13408...).

Run from the repository root:   python code/prepare_data.py
Then:                           export Q2_DIR="$PWD/workspace"   and run the notebooks.
The raw Lending Club file is needed only to rebuild the extracts (Extract_Extra_Data.ipynb);
see workspace/archive/README.txt.
"""
import gzip
import hashlib
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS = ROOT / 'workspace'
EXPECTED = {  # SHA-256 of the decompressed files
    WS / 'extra_data' / 'lending_club_36m_wide.csv': '444bc69f7aea6a9da7eda16ac3f9749a335e2fbee6ddc4fb606dd349e5bb800d',
    WS / 'extra_data' / 'lending_club_60m_wide.csv': '1f5e37d3c59882da12f0b767bee936ecb3b3fa3ebd260e1457732eb70f6862cd',
    WS / 'extra_data' / 'payments.csv': 'dbcc756a7fbfdae816d55fe9bcd64c68c1f64d55c0dc3b8bab42d2f13e37b759',
    WS / 'extra_data' / 'label_dates.csv': 'b99042a27571077ea5e93cef2625cd331185585ca104095127a8c1c363b73e1b',
    WS / 'lending_club_real_36m.csv': '2b087e41b58b3cd55af9bde60d731a49e7c9d4b3232df3ba9be4905c9f3a0c00',
}
PROSPER = WS / 'extra_data' / 'prosper' / 'prosperLoanData.csv'
PROSPER_SHA = 'fce13408ac22e8201363e71e1a16d9795305f4aaf8c0f67efcd80424bc5b9e02'
PROSPER_URLS = ['https://s3.amazonaws.com/udacity-hosted-downloads/ud651/prosperLoanData.csv',
                'https://raw.githubusercontent.com/chukwume/prosperloandata/master/prosperLoanData.csv']


def sha256(path, block=1 << 24):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(block), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ok = True
    for target, want in EXPECTED.items():
        gz = target.with_name(target.name + '.gz')
        if not target.exists():
            if not gz.exists():
                print(f'MISSING {gz.relative_to(ROOT)}'); ok = False; continue
            with gzip.open(gz, 'rb') as fi, open(target, 'wb') as fo:
                shutil.copyfileobj(fi, fo, 1 << 24)
        got = sha256(target)
        if want and got != want:
            print(f'FAIL    {target.relative_to(ROOT)}: SHA-256 {got} != {want}'); ok = False
        else:
            print(f'ok      {target.relative_to(ROOT)}' + ('' if want else f'  (SHA-256 {got[:12]}...)'))

    if not PROSPER.exists():
        PROSPER.parent.mkdir(parents=True, exist_ok=True)
        for url in PROSPER_URLS:
            try:
                print('downloading', url)
                raw = urllib.request.urlopen(url, timeout=600).read()
                PROSPER.write_bytes(raw.replace(b'\r\n', b'\n'))   # the Udacity copy uses CRLF line endings
                break
            except Exception as e:                                  # try the next source
                print('  failed:', e)
    if PROSPER.exists():
        got = sha256(PROSPER)
        print(('ok      ' if got == PROSPER_SHA else 'FAIL    ') + f'{PROSPER.relative_to(ROOT)} SHA-256 {got[:12]}...')
        ok &= got == PROSPER_SHA
    else:
        print('MISSING Prosper file: see workspace/extra_data/prosper/README.txt'); ok = False

    print('\nworkspace ready' if ok else '\nsome files are missing or do not match (see above)')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
