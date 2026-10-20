**Answers of the professor (email 07/10/2026):**

- New 12 lead: for now we keep all of them. By "the most recent ones" he meant the ECGs taken close to the day of the exam (auscultation), some may have been taken far from it. One option for later is to keep only the ECGs taken a few days before or after the auscultation, and remove the others.

- The 5 ECGs that are more than 5 days from the evaluation (3, 24, 69, 70 and 199) may be more suspicious, but for now we keep them too.

- Patient 199: the evaluation date `202-04-23` in the DB is just a typo, the correct date is `2025-04-23`.

- Quality annotations (`ULSGE_manual_SQA_ver_2.xlsx`): the number follows the order of the recordings, with `1` (or no number) being the first. His words: "Quando usamos a app antiga (até o paciente 108), quem descarregou os dados deve ter usado a "notação" PV, PV2, etc. Doutro lado, a nossa app automáticamente deve estar a chamar os ficheiros AV1, AV2, etc."

---

**Meeting conclusions (20/10/2026):**

- Repeated recordings: keep all of them for now.

- Test with a general LLM to see which variables come out of the reports, and see if they make sense. It can be ChatGPT or a similar external model, but be careful with the names and other private information. A local model is not needed for privacy reasons.

- Extract the maximum number of variables from the reports and see the clustering, that is, a table with one row per patient and one column per variable, and check if the patients form groups by themselves.

- Once we have the variables, use models that create representations of them. TabPFN: foundation model for tabular data.

---

**Done:**

- New notebook `Data_Preparation.ipynb`, the shared code (paths, readers, recording index) is in `src/multiscope.py`, and `Data_Processing.ipynb` stays as the analysis that led to the decisions.

- Moved Samsung, compiled_dataset.pkl, Old 12 lead, ECGs and Patients_Multiscope to a folder "Unused" (`scripts/organize_data.py`).

- Using the new DB_Multiscope (18.09.2026) and compared it with the one from 21.07: same 301 patients and 39 columns, only some values changed (Ritmo, Report_ecoTT, FEVE4C, PSAP...).

- `NO_SIGNAL_IDS` is now 71–77, 131, 132, 273, 274 and 275.

- Ignored the Rijuven files of the patients with ID greater than 108, so 118, 119, 121 and 122 keep only their new app recordings. In total there are 1350 recordings of 289 patients, and all of them are in the DB.

- The 314 zero-filled packets are removed, at the same positions in the ECG and the PCG, like the other lost packets. Only the packets where all values are 0 are removed, single zeros among real values are kept.

- Missing data of the DB, for the patients with recordings. The hemodynamic data (AoMeanP, mPAP, pCWP...) is missing in more than 90%, HTP Probability in 39%, PSAP in 38% and Report_ecoTT in 12%.

- Quality annotations joined to the recordings with the confirmed naming: 1191 of 1350 recordings have a score, and every score has its recording. The 31 patients from 268 to 301 have no scores (the file ends at 267).

- Repeated recordings: there are 152 repeated sites with scores. Comparing the last with the first, the last one is better in 70, equal in 53 and worse in 29. The last one is the best (or tied) in 121 of the 152, so the last one is usually the best, but not always, like the professor said.

- Patient 199 date corrected in the code (the Excel stays the same). Now only 3, 24, 69 and 70 are more than 5 days away.

- Report_ecoTT de-identified: the reports had the name of the patient (`Nome:` field) and the health number (`NSC:`). The names and the identifier numbers were replaced by `[NAME]` and `[ID]`, and none of the reports that can be checked still has the name. Patients 292, 299, 300 and 301 have no real report, so there are 252 reports, saved in `data/processed/` (not pushed to GitHub).

- Saturation (Section 8): the device can only measure values from 0 to 4095, so when the signal goes beyond, it is cut flat at the limit. 435 of the 1350 ECGs (32%) are cut at some point, and 124 in more than 5% of their samples. The more the ECG is cut, the lower its quality score (from 2.18 with no cut to 1.12 with more than 5%). The PCG is cut in almost every recording, but only briefly, and it does not change the score much. Nothing is removed, the share of cut samples is kept in `sat_ecg` and `sat_pcg`.

---

**What to do first:**

- Fix the markdown of the notebook so it is consistent:
    - Section 2: the bullet about `AV1` being the second recording (the supervisor confirmed it is the first), and the bullet about patient 168 (row 6 is all 0's in both the ECG and the PCG, and it is a lost packet, not a sensitivity problem).
    - Section 4: a flat line at 0 can be real in the PCG (saturation), only a whole packet of 0's is fake. Also delete the first line of cell `4bc33535`, it is not needed.
    - Section 5.1: show the number of recordings per repeated site in the output (141 with 2 and 11 with 3), and add the decision of keeping all repeats.
    - Section 8: add the explanation of the threshold (within 10 of the limits) in the empty markdown cell, and the check cell that shows the ECG floor (3 to 9) and the Rijuven PCG maximum (about 0.95).

- Before the LLM test, remove the remaining private information from the reports: the names of the doctors and technicians who signed them (`Dr.`, `Téc.`) and the exam dates. Save the result in a new CSV in `data/processed/`.

- Test a general LLM on a small sample of reports (about 10) to see which variables come out, and check them against the report and the DB columns (IM, IT, IAO, FEVE, PSAP).

---

**Next steps:**

- Extract the maximum number of variables of the Report_ecoTT with the LLM, for all the reports.

- Clustering on the reports only (on the table of extracted variables).

- Representations of the variables with TabPFN.

- Check missing data on the signals side (sites, apps, scores and 12 lead per patient).

- Create a global dataset with everything per patient (signals, scores, DB variables, report variables and 12 lead).

- Perform clustering on the data to see whether the patients cluster together, using PCG and ECG.

- Analyze which type of labels to use later on.

- The impact of alignment: what changes when aligning the different combinations, and whether they cluster in different ways.

- Apply pre-trained LLMs to the raw data.

---

**Questions for the professor:**

- Is there a newer version of the quality annotations with the patients from 268 to 301? If not, should we use the algorithm of my thesis group, or consider their quality unknown?

- Is the ECG saturation known? Should the saturated recordings be marked or removed?

- Report_ecoTT: which variables are the most important to extract?