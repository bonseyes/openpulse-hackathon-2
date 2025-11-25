# openpulse-hackathon-2 : Reproducable AI

The goal of this projecct is that given a code repository with associated paper related to ML/AI artifacts (dataset, algrotihm, model, etc) to assess it's reproducability. Reproducability is measured by:
- Classifying the paper fulltext and a summary of the github code repository as markdown into a defined ML Reproducability Class (I/II/III) using OpenAI
- Collecting observations of ML Reproducability Realworld Evidence (RWE) and produce a score (0 to 1) from multiple dimensions including usage statistics from HuggingFace, Github, and Open Pulse open source insights on AI artificants identified in the paper and code repositories.

An JSON and HTML ML Reproducability Report is produced as output.

## Getting Started

Main script will fetch JSON information from paperid from openalex.org and fetch git repository statistics from github and output JSON

paper_id - Paper identifier from openalex (https://openalex.org/W4390875033)
github_id - Git repository identifier (https://github.com/M-3LAB/awesome-industrial-anomaly-detection)
```
PYTHONPATH=src python3 -m reproai.main run --paper_id https://openalex.org/W4390875033 --github_id https://github.com/M-3LAB/awesome-industrial-anomaly-detection
```

## JSON Output
TODO
```
TODO
```

## API / Database Querires
- OpenAlex API
- OpenPulse API
- Github API
- OpenAPI API
- HuggingFace API
