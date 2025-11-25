# openpulse-hackathon-2 : Reproducable AI

The goal of this projecct is that given a code repository with associated paper related to ML/AI artifacts (dataset, algrotihm, model, etc) to assess it's reproducability.

## Input
- Git repository identifier
- Paper identifier (openalex)

## Intermediate Results
- Paper full text as markdown
- Github contents summary as markdown
- Huggingface dataset_id
- Huggingface model_id

## Output
- ML Reproducability Class (I/II/III) -> Label
- ML Reproducability Realworld Evidence (RWE) -> Various Dimensions -> Score (0 to 1)
- ML Reproducability Report

Format:
- JSON / API / HTML

## API / Database Querires
- OpenAlex API
- OpenPulse API
- Github API
- OpenAPI/Google API
- HuggingFace API
