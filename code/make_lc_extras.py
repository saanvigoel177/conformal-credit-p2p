"""Recreate Desktop/Q2/extra_data/payments.csv and label_dates.csv from the raw Lending Club file.

1. Download "accepted_2007_to_2018Q4.csv.gz" from the Kaggle dataset "All Lending Club loan data"
   (https://www.kaggle.com/datasets/wordsforthewise/lending-club) and put it in Desktop/Q2/archive/
   (.csv, .csv.gz or .zip all work; no need to unzip).
2. Run:  python make_lc_extras.py      (takes about 2-5 minutes)
"""
import hashlib, json, os, sys
from pathlib import Path
import pandas as pd

Q2 = Path(os.environ.get('Q2_DIR', Path.home() / 'Desktop' / 'Q2'))
ED, AR = Q2 / 'extra_data', Q2 / 'archive'
wide = ED / 'lending_club_36m_wide.csv'
if not wide.exists():
    sys.exit(f'missing {wide}: copy it from the reviewer bundle first')
raws = [p for p in AR.glob('*') if p.is_file() and 'accepted_2007_to_2018Q4' in p.name]
if not raws:
    sys.exit(f'no raw file in {AR}: download accepted_2007_to_2018Q4.csv.gz from Kaggle and put it there')
raw = raws[0]
print('raw file:', raw)

ids = set(pd.read_csv(wide, usecols=['id'], dtype={'id': str})['id'])
print(f'{len(ids):,} loan ids needed')
cols = ['id', 'total_pymnt', 'funded_amnt', 'last_pymnt_d']
comp = 'zip' if raw.suffix == '.zip' else ('gzip' if raw.suffix == '.gz' else None)
parts = []
for i, ch in enumerate(pd.read_csv(raw, usecols=cols, dtype={'id': str}, chunksize=250_000, low_memory=False, compression=comp)):
    parts.append(ch[ch['id'].isin(ids)])
    print(f'  read {(i + 1) * 250_000:,} rows', end='\r')
d = pd.concat(parts).drop_duplicates('id')
print(f'\nmatched {len(d):,} of {len(ids):,} loans ({len(d) / len(ids):.2%})')
d[['id', 'total_pymnt', 'funded_amnt']].to_csv(ED / 'payments.csv', index=False)
d[['id', 'last_pymnt_d']].to_csv(ED / 'label_dates.csv', index=False)
print('wrote', ED / 'payments.csv', 'and', ED / 'label_dates.csv')

# optional check: the raw file is the one the paper used (only possible for the uncompressed csv)
man = ED / 'raw_manifest.json'
if man.exists() and raw.suffix == '.csv':
    h = hashlib.sha256()
    with open(raw, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 24), b''): h.update(blk)
    print('raw file matches the paper\'s copy:', h.hexdigest() == json.loads(man.read_text())['raw_sha256'])
