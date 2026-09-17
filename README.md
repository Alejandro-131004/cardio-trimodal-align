# cardio-trimodal-align

**Trimodal representation alignment of heart sounds, electrocardiograms, and clinical reports for cardiac diagnosis**

MSc dissertation — Faculty of Sciences, University of Porto (FCUP), Department of Computer Science
Author: Alejandro Gonçalves · Supervisor: Prof. Francesco Renna
Clinical data partner: Unidade Local de Saúde de Gaia e Espinho

---

## Motivation

Cardiac auscultation and the electrocardiogram (ECG) are the two most widely available, non-invasive tools for first-line assessment of cardiac function. They capture complementary views of the same cardiac cycle, the ECG records the electrical activation of the heart, while the phonocardiogram (PCG) records its mechanical events (valve closures, blood-flow turbulence). In clinical practice, however, they are usually interpreted separately, and reliable interpretation still requires substantial expertise.

Deep learning models trained purely on PCG or ECG signals learn statistical patterns associated with disease, but they remain *semantically blind*, that is, their internal representations are not grounded in the clinical concepts and terminology that clinicians use to reason about a case.

## Goal

This project investigates **language-guided representation learning** for **synchronous PCG + ECG recordings paired with echocardiography reports**. Building on recent work that uses a frozen medical language model as a *semantic teacher* for medical audio encoders, de-identified and curated report summaries are encoded and aligned with PCG, ECG and fused PCG–ECG representations.

Supervision is modality-specific:

| Representation | Aligned primarily with |
|---|---|
| PCG | Acoustically relevant valvular findings |
| ECG | Rhythm and cardiac remodelling findings |
| Fused PCG + ECG | Overall echocardiographic phenotype |

## Objectives

1. Investigate representation alignment strategies that jointly leverage PCG and ECG signals, extending recent audio–language alignment frameworks (guided by a pre-trained clinical language model) to a trimodal PCG–ECG–report setting.
2. Design and compare lightweight alignment methods for PCG, ECG and fused PCG–ECG representations using a frozen medical language encoder as semantic teacher.
3. Evaluate the learned representations through cross-modal retrieval, label-efficiency analysis and prediction of selected echocardiographic phenotypes, with patient-level validation.

## Methodology (planned)

Given the size of the available clinical cohort, the work favours:

- **Pretrained signal encoders** for PCG and ECG, with lightweight projection and fusion modules.
- **Alignment objectives**: centered kernel alignment (CKA), contrastive / supervised contrastive alignment, combined with self-supervised signal losses that preserve temporal and morphological information.
- **ECG-guided cardiac cycle segmentation** enabled by synchronous acquisition, allowing beat-level multimodal aggregation.
- **Patient-level validation** throughout.

## Evaluation

The representations are evaluated through retrieval and downstream prediction tasks derived from echocardiography data, such as:

- Pulmonary hypertension probability
- Clinically significant valvular regurgitation
- Reduced left ventricular ejection fraction

Baselines: PCG-only, ECG-only, multimodal without language alignment, and in-domain signal adaptation. The comparison aims to establish whether report-based semantic supervision improves **accuracy, robustness and label efficiency**.

## What is new

The project explores a clinically structured form of language alignment in which synchronized electrical and acoustic cardiac representations receive complementary supervision from echocardiography reports. Its main contribution is the combination of ECG-guided beat-level modelling with modality-specific and patient-level semantic alignment, while explicitly testing which improvements arise from synchronization, from multimodal fusion and from report-based supervision.

## Repository structure

```
TO BE DEFINED
```

> Clinical data is **not** included in this repository. Recordings and reports are de-identified and used under agreement with Unidade Local de Saúde de Gaia e Espinho.

## Data

Each patient has **8 synchronous recordings**: one PCG and one ECG for each of the four auscultation sites (aortic, pulmonary, tricuspid, mitral valves). Two acquisition versions coexist in the cohort:

| Patients | PCG | ECG | Notes |
|---|---|---|---|
| 1–108 | `.mp3` audio | `.raw` (comma-separated samples, 500 Hz) | First device version |
| 109 onwards | `.csv` (numeric samples, 3000 Hz) | `.csv` (numeric samples, 500 Hz) | Newer app export, timestamped rows |

Each recording is paired with the patient's echocardiography report, which provides the textual supervision for alignment. The exact structure is still being verified and will be documented as the data pipeline is built.

## Related work at FCUP

This dissertation continues a line of work on multimodal PCG–ECG deep learning supervised by Prof. Francesco Renna:

- H. Vieira, *Multimodal deep learning for heart sound and electrocardiogram classification*, MSc Data Science, FCUP, 2023.
- B. Oliveira, *Deep learning for heart sounds and electrocardiogram signal analysis: On the impact of multimodal data for explainable AI*, MSc Data Science, FCUP, 2024.

## References

1. T.-N. Wang, L.-L. Chen, N. Zeghidour, A. Saeed. *Language Models as Semantic Teachers: Post-Training Alignment for Medical Audio Understanding.* arXiv:2512.04847, 2026.
2. A. Radford et al. *Learning transferable visual models from natural language supervision.* ICML, 2021.
3. S. Kornblith, M. Norouzi, H. Lee, G. Hinton. *Similarity of neural network representations revisited.* ICML, 2019.
4. G. Hinton, O. Vinyals, J. Dean. *Distilling the knowledge in a neural network.* arXiv:1503.02531, 2015.
5. M. Klum et al. *Wearable cardiorespiratory monitoring employing a multimodal digital patch stethoscope.* Sensors, 20(7):2033, 2020.
6. Y. Zeng et al. *A multimodal parallel method for left ventricular dysfunction identification based on PCG and ECG signals synchronous analysis.* Math. Biosci. Eng., 19(9):9612–9635, 2022.
7. F. Renna, J. Oliveira, M. T. Coimbra. *Deep convolutional neural networks for heart sound segmentation.* IEEE JBHI, 23(6):2435–2445, 2019.
8. P. Li, Y. Hu, Z. P. Liu. *Prediction of cardiovascular diseases by integrating multi-modal features with machine learning methods.* Biomed. Signal Process. Control, 66:102474, 2021.
9. H. Zhang et al. *Discrimination of patients with varying degrees of coronary artery stenosis by ECG and PCG signals based on entropy.* Entropy, 23(7):823, 2021.
10. J. Oliveira, F. Renna, P. D. Costa, M. Nogueira, C. Oliveira, C. Ferreira, A. Jorge, S. Mattos, T. Hatem, T. Tavares, A. Elola, A. Bahrami Rad, R. Sameni, G. D. Clifford, M. T. Coimbra. *The CirCor DigiScope Dataset: From Murmur Detection to Murmur Classification.* IEEE JBHI, 26(6):2524–2535, 2022.
