# Audio Evaluation Tool
This project was developed as major part of a Bachelor's Thesis at Brno University of Technoloogy, Faculty of information technology - Comparison and analysis of speech synthesizers.
The author of this project and said Bachelor's theis is Roman Machala.

## Table of contents
- [Foreword](#foreword)
- [Must know](#must-know)
    - [Intrusive evaluation](#intrusive-evalaution)
    - [Used intrusive metrics](#used-intrusive-metrics)
    - [Non-intrusive evaluation](#non-intrusive-evaluation)
- [Installation](#installation)
- [Usage](#usage)
    - [Windows](#windows)
    - [Linux](#linux)
- [Input structure](#input-structure)
    - [Examples of structure](#examples-of-structure)
        - [Intrusive evaluation structure](#intrusive-evaluation-structure)
        - [Non-ntrusive evaluation structure](#non-intrusive-evaluation-structure)
- [Output structure](#output-structure)
- [Visualization](#visualization)
    - [Graphs section](#graphs-section)
    - [Tables section](#tables-section)
- [Adaptability](#adaptability)

## Foreword
Text-to-Speeh (TTS) is a system capable of synthesizing speech based on prived text input using the computer. These systems have made significant advancements in recent years, especially in nature, intelligibility, etc. This project aims to provide a **audio evaluation tool** for these systems to evaluate their capabilities concerning audio quality. This tool utilizes some **objective** evaluation metrics to assess audio. Compared to **subjective** metrics (such as MOS) that require human listeners, this approach is time and cost-friendly.

In short, this tool provides a simple, deterministic, reproducible, time- and cost-friendly audio assessment tool along with simple visualization.

## Must know
This system evaluates audio in intrusive and non-intrusive ways:
- **intrusive evaluation** - requires reference samples to compare reference and generated audio samples
- **non-intrusive** - requires only generated audio sample

![Evalaution flow chart](figs/evaluation_flow.svg)

### Intrusive evaluation
When performing an intrusive evaluation, the non-intrusive assessment is performed as well.

When using intrusive evaluation:
- compares reference and generated samples
    - make sure that you have your meta file set up correctly
    - make sure to use the exact transcriptions in reference and generated samples as different ones negatively affect results
> **_NOTE:_** The intrusive evaluation compares the quality of the reference audio sample to the quality of the generated sample. Based on the quality difference - intelligibility, etc., could be affected. This scenario is aimed explicitly at zero-shot systems, where you provide a reference sample of a speaker you want to match. High-quality synthesized audio is expected when providing a high-quality reference sample with the exact transcription. Thus, in this use case, the intrusive evaluation measures the capabilities of zero-shot systems to produce high-quality audio samples by comparing the reference and generated samples.
#### Used intrusive metrics
The intrusive metrics used in this system are:
- PESQ - available at: https://pypi.org/project/pesq/
- STOI and ESTOI - available at: https://pypi.org/project/pystoi/
- MCD - available at: https://github.com/ttslr/python-MCD

When comparing audio, they must be aligned first since the TTS system can produce faster/slower speech, different intonation, etc, which could negatively affect the evaluation. A FastDTW - Dynamic Time Warping function was used to align these audios, available at: https://pypi.org/project/fastdtw/.

### Non-intrusive evaluation
A MOS predictor, available at https://pypi.org/project/speechmos/, does the non-intrusive evaluation. This predictor is highly correlated with subjective evaluation metrics, thus providing reliable results regarding audio quality assessment. For each audio, the predictor returns:
ovrl_mos - overall audio quality
sig_mos - speech signal quality
bak_mos - background quality
p808_mos - reflects the overall quality of the audio sample based on subjective metrics
The **p808_mos** should be given the highest weight in this system.

## Installation 
It is recommended to create a conda environment as several dependencies are required for this system to run.

You can create an environment and install all dependencies using:
```
conda create --name AudioEval
conda activate AudioEval
pip install -r requirements.txt
```
## Usage
The system can be started in two modes:
- **command line mode** - starts evaluation and provides a result file in json format 
- **web mode** - provides a simple GUI for evaluation and visualization of results

If possible, the **web mode** approach is recommended.
It is also possible that the script might require *sudo*.
### Windows

### Linux
To use this system on linux, simply use the *start_eval.sh* script.

This command displays help on how to properly use this system along with example usages:
```bash
./start_eval --help
```

To start evaluation on a selected dataset and save results into test.json file use:
```bash
./start_eval.sh --dataset_path /path/to/dataset --meta_file /path/to/meta --save_path test.json
```

To start evaluation in **web mode** just simply use this command:
```bash
./start_eval.sh --web_mode true
```
The application will then be available at https://localhost:8000
## Input structure
The system expects a meta file (and optionally a path to a dataset).

**If the dataset path is not specified, the metafile must have absolute paths**
#### Examples of structure
This section shows examples of structures of datasets for intrusive and non-intrusive evaluations.

### Intrusive evaluation structure
The dataset structure could be as follows:
```
dataset/
    |---audios_gen/
            |---sample_01.wav
            |---sample_02.wav
            |---sample_03.wav
                ...
    |---audios_ref/
        |---sample_01.wav
        |---sample_02.wav
        |---sample_03.wav
                ...
    |---meta
```
Then the meta file should be in format:
```
audios_ref/sample_01.wav audios_gen/sample_01.wav
audios_ref/sample_02.wav audios_gen/sample_02.wav
audios_ref/sample_03.wav audios_gen/sample_03.wav
    ...
```
If using absolute paths in meta file, the structure should be:
```
/dataset_path/audios_ref/sample_01.wav /dataset_path/audios_gen/sample_01.wav
/dataset_path/audios_ref/sample_02.wav /dataset_path/audios_gen/sample_02.wav
/dataset_path/audios_ref/sample_03.wav /dataset_path/audios_gen/sample_03.wav
    ...
```

### Non-intrusive evaluation structure
The dataset structure could be as follows:
```
dataset/
    |---audios/
            |---sample_01.wav
            |---sample_02.wav
            |---sample_03.wav
                ...
    |---meta
```
Then the meta file should be in format:
```
audios/sample_01.wav
audios/sample_02.wav
audios/sample_03.wav
    ...
```
If using absolute paths in meta file, the structure should be:
```
/dataset_path/audios/sample_01.wav
/dataset_path/audios/sample_02.wav
/dataset_path/audios/sample_03.wav
    ...
```
## Output structure
The result of this system is then stored in a json file with format:
```
{
    "status": "completed",
    "path": "/dataset_path",
    "results": [
        {
            "file": "sample_01.wav",
            "Mcd": xy,
            "Pesq": xy,
            "Stoi": xy,
            "Estoi": xy,
            "Mos": {
                "ovrl_mos": xy,
                "sig_mos": xy,
                "bak_mos": xy,
                "p808_mos": xy
            }
        }
    ]
}
```
## Visualization
When using the web mode for this system, all results can be visualized directly in your browser.
### Graphs section

For each file containing evalaution a set of graphs are generated for each metric available. For example a graph for non-intrusive evaluation (only MOS) can be seen below.
![figs/example_graph.png](figs/example_graph.png)
### Tables section
Besides graphs a set of tables is generatd containig fundamental statistical values for easy intepretation. Reagrding MOS - returning four MOS scores for each audio, for each MOS score a table is generated. The format of all tables can be seen below.
| File | Mean | Median | Min | Max |
| - | - | - | - | - |
| example | xy | xy | xy | xy |

### Audio section
TODO !!!


## Adaptability
