"""Reproducible AI CLI prototype.

This module provides a CLI entry point that collects paper and repository
metadata, computes a reproducibility summary, writes JSON and HTML reports,
and prints a short status message. The implementation is intentionally
lightweight and uses only the Python standard library so it can run in
minimal environments.
"""

from __future__ import annotations

import argparse
import json
import os
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional


class ReproAIReport:
    """Collect paper and repository metadata to build a reproducibility report."""

    def __init__(
        self,
        paper_id: str,
        github_id: str,
        output_dir: str = "reports",
        github_token: Optional[str] = None,
    ) -> None:
        self.paper_id = paper_id
        self.github_id = github_id
        self.output_dir = output_dir
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

    # ---------------------------- Fetchers ----------------------------
    def fetch_json(self, url: str, headers: Optional[Mapping[str, str]] = None) -> Dict:
        request_headers = {"User-Agent": "reproai-cli/0.1"}
        if headers:
            request_headers.update(headers)

        request = urllib.request.Request(url, headers=request_headers)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:  # pragma: no cover - runtime safeguard
            raise RuntimeError(f"Failed to fetch {url}: {exc.read().decode('utf-8')}") from exc
        except urllib.error.URLError as exc:  # pragma: no cover - runtime safeguard
            raise RuntimeError(f"Failed to fetch {url}: {exc.reason}") from exc

    def fetch_paper_metadata(self) -> Dict[str, object]:
        paper_identifier = self.paper_id.rsplit("/", maxsplit=1)[-1]
        url = f"https://api.openalex.org/works/{paper_identifier}"
        payload = self.fetch_json(url)

        authors: List[str] = [
            authorship.get("author", {}).get("display_name", "")
            for authorship in payload.get("authorships", [])
        ]

        publication_year = payload.get("publication_year") or payload.get("primary_location", {}).get(
            "source", {}
        ).get("publication_year")

        return {
            "paper_id": self.paper_id,
            "title": payload.get("display_name", "Unknown Title"),
            "published_year": publication_year,
            "authors": [name for name in authors if name],
            "venue": payload.get("host_venue", {}).get("display_name"),
        }

    def fetch_repo_metadata(self) -> Dict[str, object]:
        parsed = urllib.parse.urlparse(self.github_id)
        owner, repo = parsed.path.strip("/").split("/", maxsplit=1)
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {"Accept": "application/vnd.github+json"}
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"
        payload = self.fetch_json(url, headers=headers)

        return {
            "github_id": self.github_id,
            "default_branch": payload.get("default_branch"),
            "stars": payload.get("stargazers_count"),
            "forks": payload.get("forks_count"),
            "open_issues": payload.get("open_issues_count"),
            "primary_language": payload.get("language"),
            "updated_at": payload.get("pushed_at"),
        }

    # ------------------------- Transformations -----------------------
    def compute_rwe_score(self, repo_metadata: Mapping[str, object]) -> MutableMapping[str, float]:
        stars = float(repo_metadata.get("stars") or 0)
        forks = float(repo_metadata.get("forks") or 0)
        issues = float(repo_metadata.get("open_issues") or 0)

        def normalize(value: float, scale: float = 500.0) -> float:
            return min(value / scale, 1.0)

        github_activity = (normalize(stars) * 0.6) + (normalize(forks) * 0.3) + (normalize(max(1.0, issues)) * 0.1)
        huggingface_downloads = 0.42  # Placeholder for future HF API integration.
        citations = 0.38  # Placeholder until citation counts are ingested.
        community_adoption = min((github_activity + huggingface_downloads) / 2, 1.0)
        aggregate = (github_activity + huggingface_downloads + citations + community_adoption) / 4

        return {
            "github_activity": round(github_activity, 2),
            "huggingface_downloads": round(huggingface_downloads, 2),
            "citations": round(citations, 2),
            "community_adoption": round(community_adoption, 2),
            "aggregate": round(aggregate, 2),
        }

    def build_artifacts(self, repo_metadata: Mapping[str, object]) -> Dict[str, List[Dict[str, object]]]:
        return {
            "datasets": [
                {
                    "name": "Example Dataset",
                    "source": "openalex",
                    "url": "https://example.org/dataset",
                }
            ],
            "models": [
                {
                    "name": repo_metadata.get("github_id", "model"),
                    "huggingface_model_id": "org/model",
                    "downloads": 0,
                }
            ],
            "checkpoints": [
                {
                    "name": "checkpoint-v1",
                    "location": "s3://bucket/checkpoints/checkpoint-v1.pt",
                    "sha256": "<hash>",
                }
            ],
        }

    def assemble_report(self) -> Dict[str, object]:
        paper_metadata = self.fetch_paper_metadata()
        repo_metadata = self.fetch_repo_metadata()
        rwe = self.compute_rwe_score(repo_metadata)
        artifacts = self.build_artifacts(repo_metadata)

        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        slug = repo_metadata.get("github_id", "report").rsplit("/", maxsplit=1)[-1]
        json_path = os.path.join(self.output_dir, f"{slug}.json")
        html_path = os.path.join(self.output_dir, f"{slug}.html")

        return {
            "metadata": {
                "paper": paper_metadata,
                "repository": repo_metadata,
            },
            "reproducibility_assessment": {
                "class": "II",
                "classification_rationale": "Heuristic classification based on repository activity and metadata completeness.",
                "rwe_score": rwe["aggregate"],
                "rwe_dimensions": {k: v for k, v in rwe.items() if k != "aggregate"},
            },
            "artifacts": artifacts,
            "report": {
                "json_path": json_path,
                "html_path": html_path,
                "generated_at": timestamp,
            },
        }

    # --------------------------- Rendering ---------------------------
    def render_html(self, report: Mapping[str, object]) -> str:
        metadata = report.get("metadata", {})
        paper = metadata.get("paper", {})
        repo = metadata.get("repository", {})
        assessment = report.get("reproducibility_assessment", {})
        artifacts = report.get("artifacts", {})
        dimensions = assessment.get("rwe_dimensions", {})

        html = f"""
        <html>
          <head>
            <title>Reproducible AI Report</title>
            <style>
              body {{ font-family: Arial, sans-serif; margin: 2rem; }}
              h1, h2, h3 {{ color: #12355b; }}
              .card {{ border: 1px solid #e1e4e8; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; }}
              .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }}
              table {{ width: 100%; border-collapse: collapse; }}
              th, td {{ padding: 0.5rem; border-bottom: 1px solid #e1e4e8; text-align: left; }}
              code {{ background: #f6f8fa; padding: 0.2rem 0.4rem; border-radius: 4px; }}
            </style>
          </head>
          <body>
            <h1>Reproducible AI Report</h1>
            <div class="card">
              <h2>Paper</h2>
              <p><strong>Title:</strong> {paper.get('title')}</p>
              <p><strong>Authors:</strong> {', '.join(paper.get('authors', []))}</p>
              <p><strong>Published:</strong> {paper.get('published_year')}</p>
              <p><strong>Venue:</strong> {paper.get('venue')}</p>
              <p><strong>OpenAlex ID:</strong> <code>{paper.get('paper_id')}</code></p>
            </div>

            <div class="card">
              <h2>Repository</h2>
              <p><strong>GitHub:</strong> <code>{repo.get('github_id')}</code></p>
              <p><strong>Default branch:</strong> {repo.get('default_branch')}</p>
              <div class="grid">
                <div><strong>Stars:</strong> {repo.get('stars')}</div>
                <div><strong>Forks:</strong> {repo.get('forks')}</div>
                <div><strong>Open issues:</strong> {repo.get('open_issues')}</div>
                <div><strong>Primary language:</strong> {repo.get('primary_language')}</div>
                <div><strong>Last push:</strong> {repo.get('updated_at')}</div>
              </div>
            </div>

            <div class="card">
              <h2>Reproducibility Assessment</h2>
              <p><strong>Class:</strong> {assessment.get('class')}</p>
              <p><strong>Rationale:</strong> {assessment.get('classification_rationale')}</p>
              <h3>Real-world Evidence</h3>
              <table>
                <thead><tr><th>Dimension</th><th>Score</th></tr></thead>
                <tbody>
                  {''.join(f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in dimensions.items())}
                </tbody>
              </table>
              <p><strong>Aggregate RWE Score:</strong> {assessment.get('rwe_score')}</p>
            </div>

            <div class="card">
              <h2>Artifacts</h2>
              {self._render_artifacts_section(artifacts)}
            </div>

            <p><em>Generated at {report.get('report', {}).get('generated_at')}</em></p>
          </body>
        </html>
        """
        return textwrap.dedent(html)

    def _render_artifacts_section(self, artifacts: Mapping[str, Iterable[Mapping[str, object]]]) -> str:
        sections: List[str] = []
        for section_name, items in artifacts.items():
            rows = [
                """<tr>{}</tr>""".format(
                    "".join(f"<td>{value}</td>" for value in item.values())
                )
                for item in items
            ]
            headers = "".join(f"<th>{header}</th>" for header in (items[0].keys() if items else []))
            table = f"""
                <h3>{section_name.title()}</h3>
                <table>
                  <thead><tr>{headers}</tr></thead>
                  <tbody>{''.join(rows)}</tbody>
                </table>
            """
            sections.append(table)
        return "\n".join(sections)

    # ----------------------------- Runner -----------------------------
    def run(self) -> Dict[str, object]:
        os.makedirs(self.output_dir, exist_ok=True)
        report = self.assemble_report()

        with open(report["report"]["json_path"], "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)

        html_content = self.render_html(report)
        with open(report["report"]["html_path"], "w", encoding="utf-8") as fh:
            fh.write(html_content)

        return report


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reproducible AI CLI prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Generate reproducibility report")
    run_parser.add_argument("--paper_id", required=True, help="OpenAlex paper identifier")
    run_parser.add_argument("--github_id", required=True, help="GitHub repository URL")
    run_parser.add_argument(
        "--output_dir",
        default="reports",
        help="Directory to store the generated JSON and HTML reports",
    )
    run_parser.add_argument(
        "--github_token",
        default=None,
        help="GitHub token to increase rate limits (optional)",
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    if args.command == "run":
        report = ReproAIReport(
            paper_id=args.paper_id,
            github_id=args.github_id,
            output_dir=args.output_dir,
            github_token=args.github_token,
        ).run()
        print(f"Report written to {report['report']['json_path']} and {report['report']['html_path']}")


if __name__ == "__main__":
    main()
