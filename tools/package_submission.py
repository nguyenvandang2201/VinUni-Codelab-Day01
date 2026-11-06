"""Create the LMS ZIP from an explicit list of submission files."""

import argparse
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.student_id):
        parser.error("Student ID must contain only letters, numbers, underscores or hyphens.")
    files = [ROOT / "solution/solution.py", ROOT / "solution/exercises.md"]
    evidence = ROOT / "reports/temperature_results.json"
    output_dir = ROOT / "dist"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / f"{args.student_id}_lab_1.zip"
    for source in files:
        if not source.is_file():
            raise SystemExit(f"Missing submission file: {source.name}")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in files:
            archive.write(source, source.relative_to(ROOT).as_posix())
        if evidence.is_file():
            archive.write(evidence, "solution/temperature_results.json")
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise SystemExit("ZIP integrity check failed")
        print("Contents:", ", ".join(archive.namelist()))
    print(output)


if __name__ == "__main__":
    main()
