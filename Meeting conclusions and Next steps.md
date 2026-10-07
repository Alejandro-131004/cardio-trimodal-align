**Meeting conclusions:**

- When there are several Excel files for the same thing (e.g., two for Mitral_ECG and two for Mitral_PCG), the professor says the last one is usually the best, though this is not a fixed rule. For AV1, it is the second one.

- The professor sent a newer, updated DB_mulitscope (18.09.2026), and that is the one we will use. His words of the meeting "Ficheiro excel atualizado: pode ter informações de pacientes aos quais não tens acesso (porque têm PCG+ECG+PPG). Assumimos que não temos: de 71 a 77 e 131 e 132, 273, 274 e 275."

- Disregard Samsung.

- Disregard compiled_dataset.pkl.

- New 12 lead: keep the most recent ones, as they may be useful. Or check also which ones are useful

- Disregard old 12 lead.

- Disregard ECGs, since new 12 lead is a compiled version of them.

- Disregard patients multiscope, or only use them to know which columns to ignore.

- Consider the whole signal. My thesis group, which works on other things, is trying to develop an algorithm that extracts only the good part of each signal. I had also thought about this, but it is complex, so we will use the whole signal. According to the professor this should not be a problem, and losing some samples can be ignored. About the 314 zero-filled packets that are fake flat lines inside the signal, and they could matter for embeddings, I don't know what to do. Help.

- Transmission is via Bluetooth, and the timestamp shown is the time the data is received.

- The 0's in some reports are normal. The device is extremely sensitive, so any small movement by the doctor or the patient changes everything.

---

**Next steps:**

- After this data analysis, once everything is understood, extract the important elements and variables of the Report_ecoTT in the new DB_Multiscope (for example, using an LLM, maybe a local model, but if that's to difficult, I will ask Francesco about an API).

- Check missing data across the different variations.

- Clustering on the reports only.

- Perform clustering on the data to see whether the 300 patients cluster together, using PCG and ECG.

- Analyze which type of labels to use later on.

- The impact of alignment: what changes when aligning the different combinations, and whether they cluster in different ways.

- Apply pre-trained LLMs to the raw data.

- Foundation models for tabular data: this is a step much further ahead, because a teammate is working on foundation models and I will meet with her to find out which models work best.

- Create a global dataset containing everything I need?


---

**What to do first:** 

- fix the notebook, such as deleting the folders I've said in the meeting conclusions. For this, I would move that data to a folder "Unused". 

- Use the new DB_Multiscope or add a new cell code for this new DB. In particular, change `CLINICAL_DB_GLOB`, and add it to the Section 5.4. comparison so it shows what changed since `21.07`.

- `NO_SIGNAL_IDS` becomes 71–77, 131, 132, 273, 274 and 275.

- ignore the loose files from Rijuven of the patients which their ID is greater than 108, in particular drop the `Rijuven recordings` of 118, 119, 121 and 122, so those patients keep only their new-app recordings.

- If i'm escaping something, please tell me

- For all of this I think its better to use a different notebook. 

- Start the "Next Steps" section


---

**Questions for claude:**

- I did not understand this "ECG saturation at 4095. This wasn't discussed. It's worth a quick count of how many recordings clip."

- About this "Choosing between repeats: my proposal is the best SQA score, with ties going to the most recent recording, and simply the most recent one for patients without scores (268+). Or would you rather always take the most recent, as Francesco suggested?" I think it needs a study first, I want to analyze the vantages and advantages. I mean the most recent implies that we have a variation of quality scores, isn't that better instead of having only good scores? 