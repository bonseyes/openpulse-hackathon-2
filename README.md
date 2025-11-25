# Reproducible AI

This project evaluates the reproducibility of ML/AI work by combining a paper with its associated code repository. The CLI ingests metadata, classifies the work into a reproducibility class, and produces a reproducibility report (JSON + HTML).

Reproducibility is measured by:
- Classifying the paper full text and a summary of the GitHub repository into a defined ML Reproducibility Class (I/II/III) using OpenAI.
- Collecting observations of real‑world evidence (RWE) and producing a score (0–1) using usage statistics from Hugging Face, GitHub, and OpenPulse insights on AI artifacts mentioned in the paper and repository.

## Getting Started

The main script will fetch JSON information from OpenAlex using the paper identifier and fetch repository statistics from GitHub before assembling the output payload.

Required identifiers:
- `paper_id`: Paper identifier from OpenAlex (e.g., `https://openalex.org/W4390875033`).
- `github_id`: Git repository identifier (e.g., `https://github.com/M-3LAB/awesome-industrial-anomaly-detection`).

Run the prototype CLI with the source tree on `PYTHONPATH`:
```
PYTHONPATH=src python3 -m reproai.main run \
  --paper_id https://openalex.org/W4390875033 \
  --github_id https://github.com/M-3LAB/awesome-industrial-anomaly-detection
```

## Example JSON Output

The following sample illustrates the structure expected from the CLI. Values are representative placeholders to guide implementation of a prototype.

```
{
  "metadata": {
    "paper": {
      "paper_id": "https://openalex.org/W4390875033",
      "title": "Awesome Industrial Anomaly Detection",
      "published_year": 2023,
      "authors": ["Jane Doe", "Alex Smith"],
      "venue": "ICML"
    },
    "repository": {
      "github_id": "https://github.com/M-3LAB/awesome-industrial-anomaly-detection",
      "default_branch": "main",
      "stars": 412,
      "forks": 97,
      "open_issues": 8,
      "primary_language": "Python"
    }
  },
  "reproducibility_assessment": {
    "class": "II",
    "classification_rationale": "Implements full training and evaluation pipeline; partial hyperparameter logging.",
    "rwe_score": 0.74,
    "rwe_dimensions": {
      "github_activity": 0.78,
      "huggingface_downloads": 0.69,
      "citations": 0.55,
      "community_adoption": 0.94
    }
  },
  "artifacts": {
    "datasets": [
      {"name": "MVTec AD", "source": "huggingface", "url": "https://huggingface.co/datasets/mvtec"}
    ],
    "models": [
      {"name": "AnomalyNet", "huggingface_model_id": "org/anomalynet", "downloads": 12345}
    ],
    "checkpoints": [
      {"name": "anomalynet-v1", "location": "s3://bucket/checkpoints/anomalynet-v1.pt", "sha256": "<hash>"}
    ]
  },
  "report": {
    "json_path": "reports/awesome-industrial-anomaly-detection.json",
    "html_path": "reports/awesome-industrial-anomaly-detection.html",
    "generated_at": "2025-02-15T12:34:56Z"
  }
}
```

## API / Database Queries
- OpenAlex API
- OpenPulse API
- GitHub API
- OpenAI API
- Hugging Face API
