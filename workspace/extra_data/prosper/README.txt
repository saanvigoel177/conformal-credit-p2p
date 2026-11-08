The Prosper file is NOT redistributed in this package (no licence or terms issued by Prosper for this snapshot were found).

File analysed:   prosperLoanData.csv   (113,937 records, 81 variables; 86,357,163 bytes)
SHA-256:         fce13408ac22e8201363e71e1a16d9795305f4aaf8c0f67efcd80424bc5b9e02

Origin and where to get it
  Publisher of the underlying data: Prosper Marketplace, Inc.
  Variable definitions (Prosper data export):
    https://www.prosper.com/Downloads/Services/Documentation/ProsperDataExport_Details.html
  The snapshot (loans originated Nov 2005 to Mar 2014) is widely redistributed, for example as the Udacity course file
    https://s3.amazonaws.com/udacity-hosted-downloads/ud651/prosperLoanData.csv
  (Accessed 9 Oct 2026.) Prosper's own help centre says loan-level data are available to account holders through its API
  or under a data licence agreement:
    https://help.prosper.com/hc/en-us/articles/210013083-Where-can-I-download-data-about-loans-through-Prosper

How to check you have the same file
    sha256sum prosperLoanData.csv        (macOS: shasum -a 256 prosperLoanData.csv)
  The output must equal the SHA-256 above. The copy we analysed was obtained from a public GitHub mirror
  (https://raw.githubusercontent.com/chukwume/prosperloandata/master/prosperLoanData.csv); the Udacity copy
  (downloaded 7 Nov 2026) differs only in line endings: it uses CRLF (86,471,101 bytes, SHA-256 71c1c193...). After converting
  CRLF to LF (for example `tr -d '\r' < in.csv > out.csv`) its SHA-256 equals the value above.

How the notebooks use it
  Prosper_Replication.ipynb, Extensions.ipynb and Audit_and_Robustness.ipynb look for the file in this folder first.
  Only if it is absent do they try to download it from the GitHub mirror above and print its SHA-256.
  To avoid depending on the mirror, place prosperLoanData.csv in this folder before running.
