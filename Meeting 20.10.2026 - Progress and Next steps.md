**Answers of the professor (email 07/10/2026):**

- New 12 lead: for now we keep all of them. By "the most recent ones" he meant the ECGs taken close to the day of the exam (auscultation), some may have been taken far from it. One option for later is to keep only the ECGs taken a few days before or after the auscultation, and remove the others.

- The 5 ECGs that are more than 5 days from the evaluation (3, 24, 69, 70 and 199) may be more suspicious, but for now we keep them too.

- Patient 199: the evaluation date `202-04-23` in the DB is just a typo, the correct date is `2025-04-23`.

- Quality annotations (`ULSGE_manual_SQA_ver_2.xlsx`): the number follows the order of the recordings, with `1` (or no number) being the first. His words: "Quando usamos a app antiga (até o paciente 108), quem descarregou os dados deve ter usado a "notação" PV, PV2, etc. Doutro lado, a nossa app automáticamente deve estar a chamar os ficheiros AV1, AV2, etc."

---

**Done:**

- New notebook `Data_Preparation.ipynb`, the shared code (paths, readers, recording index) is in `src/multiscope.py`, and `Data_Processing.ipynb` stays as the analysis that led to the decisions.

- Moved Samsung, compiled_dataset.pkl, Old 12 lead, ECGs and Patients_Multiscope to a folder "Unused" (`scripts/organize_data.py`).

- Using the new DB_Multiscope (18.09.2026) and compared it with the one from 21.07: same 301 patients and 39 columns, only some values changed (Ritmo, Report_ecoTT, FEVE4C, PSAP...).

- `NO_SIGNAL_IDS` is now 71–77, 131, 132, 273, 274 and 275.

- Ignored the Rijuven files of the patients with ID greater than 108, so 118, 119, 121 and 122 keep only their new app recordings. In total there are 1350 recordings of 289 patients, and all of them are in the DB.

- The 314 zero-filled packets are removed, at the same positions in the ECG and the PCG, like the other lost packets.

- Missing data of the DB, for the patients with recordings. The hemodynamic data (AoMeanP, mPAP, pCWP...) is missing in more than 90%, HTP Probability in 39%, PSAP in 38% and Report_ecoTT in 12%.

- Quality annotations joined to the recordings with the confirmed naming: 1191 of 1350 recordings have a score, and every score has its recording. The 31 patients from 268 to 301 have no scores (the file ends at 267).

- Repeated recordings: there are 152 repeated sites with scores. Comparing the last with the first, the last one is better in 70, equal in 53 and worse in 29. The last one is the best (or tied) in 121 of the 152, so the last one is usually the best, but not always, like the professor said.

- Patient 199 date corrected in the code (the Excel stays the same). Now only 3, 24, 69 and 70 are more than 5 days away.

- Report_ecoTT de-identified: the reports had the name of the patient (`Nome:` field) and the health number (`NSC:`). The names and the identifier numbers were replaced by `[NAME]` and `[ID]`, and none of the reports that can be checked still has the name. Patients 292, 299, 300 and 301 have no real report, so there are 252 reports, saved in `data/processed/` (not pushed to GitHub).

---

**Next steps:**

- Count how many recordings have the ECG saturated at 4095 (the R peaks are cut flat at the limit of the device).

- Decide which recording to keep when there are repeats (the last one, the best score, or keep all of them), and what to do with the patients without scores (268+).

- Extract the important elements and variables of the Report_ecoTT (for example, using an LLM, maybe a local model like **MedGemma 27B**, or an API).

- Check missing data on the signals side (sites, apps, scores and 12 lead per patient).

- Create a global dataset with everything per patient (signals, scores, DB variables, report variables and 12 lead).

- Clustering on the reports only.

- Perform clustering on the data to see whether the patients cluster together, using PCG and ECG.

- Analyze which type of labels to use later on.

- The impact of alignment: what changes when aligning the different combinations, and whether they cluster in different ways.

- Apply pre-trained LLMs to the raw data.

- Foundation models for tabular data: a step much further ahead, after meeting my teammate.

---

**Questions for the professor:**

- Is there a newer version of the quality annotations with the patients from 268 to 301? If not, should we use the algorithm of my thesis group, or consider their quality unknown?

- Repeated recordings: should we keep only the last one, the one with the best score, or all of them (more data and different qualities)?

- Report_ecoTT: which variables are the most important to extract? Can I use an API (with the de-identified reports), or should it be a local model?

- Is the ECG saturation at 4095 known? Should the saturated recordings be marked or removed?
