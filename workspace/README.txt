This is the working folder the notebooks read from. Point them at it before starting Jupyter:

    export Q2_DIR="/full/path/to/conformal-credit-p2p/workspace"     (macOS / Linux)
    set Q2_DIR=C:\full\path\to\conformal-credit-p2p\workspace         (Windows)

Run `python code/prepare_data.py` first. It decompresses the files below and downloads the Prosper file:
  extra_data/lending_club_36m_wide.csv.gz   resolved 36-month Lending Club loans issued 2007-2015 (582,113 rows)
  extra_data/lending_club_60m_wide.csv.gz   resolved 60-month loans issued 2010-2013 (53,506 rows)
  extra_data/payments.csv.gz                total payments per loan (realised profit)
  extra_data/label_dates.csv.gz             last-payment month per loan (label arrival)
  lending_club_real_36m.csv.gz              15-column extract read by Conformal_Prediction_Credit_Risk_RUN.ipynb
  extra_data/raw_manifest.json              SHA-256 of the raw Lending Club file and of the wide extracts
  extra_data/prosper/                       the Prosper file is downloaded here (see README.txt there)
  archive/                                  the raw Lending Club file, only if you want to rebuild the extracts

The notebooks write their outputs to outputs_*/ folders here; these are not part of the repository.
