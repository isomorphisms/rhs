#!/usr/bin/env python3
"""Exercise counterexamples and corrected controls; this is NOT an RHS detector."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile


def execute(command, timeout):
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=timeout, check=False)
        return {"command": command, "returncode": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"command": command, "returncode": None,
                "stdout": "", "stderr": str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cc", action="append", help="compiler executable; repeatable")
    parser.add_argument("--opt", choices=("0", "2"), action="append")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    cases = sorted(root.glob("[0-9][0-9]_*.c"))
    if not cases:
        parser.error("no C cases found")
    build_root = root / "_"
    build_root.mkdir(exist_ok=True)
    sources = cases + [root / "fixture.h", Path(__file__).resolve()]
    receipt = {
        "schema": "underhanded-c-reductions-v1",
        "scope": "standalone C counterexamples, NOT RHS detection or full entries",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "environment": {"system": platform.system(), "machine": platform.machine(),
                        "release": platform.release(),
                        "distribution": platform.freedesktop_os_release()
                        if Path("/etc/os-release").exists() else {}},
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sources},
        "compilers": [], "runs": [],
    }
    failures = unsupported = bad_rejected = corrected_accepted = 0
    with tempfile.TemporaryDirectory(prefix="run-", dir=build_root) as build:
        for index, compiler in enumerate(args.cc or [os.environ.get("CC", "cc")]):
            receipt["compilers"].append(execute([compiler, "--version"], 10))
            for optimization in args.opt or ["0", "2"]:
                for source in cases:
                    for corrected in (0, 1):
                        target = str(Path(build) / f"{index}-{optimization}-{source.stem}-{corrected}")
                        command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Wpedantic",
                                   "-Wconversion", f"-O{optimization}",
                                   f"-DUSE_CORRECTED={corrected}", str(source), "-lm", "-o", target]
                        compilation = execute(command, 30)
                        run = {"case": source.stem, "compiler": compiler,
                               "optimization": optimization, "corrected": bool(corrected),
                               "compilation": compilation, "execution": None, "status": "FAIL"}
                        if compilation["returncode"] == 0:
                            outcome = execute([target], 5)
                            run["execution"] = outcome
                            expected = "CONTRACT_PASS" if corrected else "CONTRACT_FAIL"
                            if (outcome["returncode"] == (0 if corrected else 1)
                                    and outcome["stdout"] == f"CONTROL_OK\n{expected} {source.stem}\n"
                                    and outcome["stderr"] == ""):
                                run["status"] = "EXPECTED"
                                corrected_accepted += corrected
                                bad_rejected += 1 - corrected
                            elif outcome["returncode"] == 77 and outcome["stdout"].startswith("UNSUPPORTED:"):
                                run["status"] = "UNSUPPORTED"
                                unsupported += 1
                        if run["status"] == "FAIL":
                            failures += 1
                        receipt["runs"].append(run)
                        print(f'{run["status"]}: {compiler} -O{optimization} {source.stem} '
                              f'{"corrected" if corrected else "underhanded"}')
    receipt["summary"] = {"bad_rejected": bad_rejected,
                          "corrected_accepted": corrected_accepted,
                          "unsupported": unsupported, "failures": failures}
    destination = args.receipt or build_root / "receipt.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt["summary"], sort_keys=True))
    print(f"Receipt: {destination}")
    return 1 if failures else 3 if unsupported else 0


if __name__ == "__main__":
    raise SystemExit(main())
