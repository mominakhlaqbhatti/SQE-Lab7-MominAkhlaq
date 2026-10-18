LAB 7 - RUN THESE ON YOUR OWN MACHINE (about 5 minutes) TO PRODUCE THE REAL EVIDENCE
=====================================================================================
cd week7
python -m pip install coverage pytest allpairspy
mkdir screenshots

1) Baseline  (screenshot htmlcov/index.html -> screenshots/baseline.png, must show 55%)
   coverage run -m pytest tests/test_auth.py -v
   coverage report -m
   coverage html

2) Final     (screenshot htmlcov/index.html -> screenshots/final.png, must show 90%)
   coverage erase
   coverage run -m pytest -v          # 27 passed
   coverage report -m                 # 90%
   coverage report --fail-under=80    # then: echo $LASTEXITCODE  (PowerShell) -> 0
   coverage report --fail-under=95    # exit code 2 (demo), then run the 80 version again
   coverage html

3) Pairwise  (screenshot the output -> put it in the Pairwise PDF if your instructor wants a real screenshot)
   python pairwise_check.py           # 9 cases, 54 pairs, 0 missing

4) Package
   Compress-Archive -Path htmlcov, tests\test_auth_new.py, screenshots -DestinationPath SQE_Lab7_MominAkhlaq_Coverage.zip
   (macOS/Linux: zip -r SQE_Lab7_MominAkhlaq_Coverage.zip htmlcov tests/test_auth_new.py screenshots)

Replace MominAkhlaq / [RegNo] in the two PDFs' filenames and header table.
