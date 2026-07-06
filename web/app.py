from flask import Flask, render_template, request, jsonify, send_file
import subprocess, sys, os, re, io, zipfile
from pathlib import Path
import yaml

app = Flask(__name__)

BASE = Path(__file__).resolve().parent.parent
INPUTS = BASE / "inputs"
OUTPUT = BASE / "output"
COMPANIES = BASE / "companies"


def strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*[mGKHFJA-Za-z]', '', text)


def get_companies() -> list[dict]:
    result = []
    for d in sorted(COMPANIES.iterdir()):
        if d.is_dir():
            p = d / "profile.yaml"
            if p.exists():
                result.append(yaml.safe_load(p.read_text(encoding="utf-8")))
    return result


def run_acra(args: list[str]) -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE / "src")
    env["NO_COLOR"] = "1"
    env["TERM"] = "dumb"
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.run(
        [sys.executable, "-m", "acra_helper.cli"] + args,
        capture_output=True,
        text=True,
        cwd=str(BASE),
        env=env,
        encoding="utf-8",
        errors="replace",
    )
    output = strip_ansi((proc.stdout or "") + (proc.stderr or ""))
    return proc.returncode == 0, output.strip()


@app.errorhandler(Exception)
def handle_error(e):
    if request.path in ("/run", "/demo"):
        return jsonify({"success": False, "output": f"Server error: {e}"}), 200
    raise e


@app.route("/")
def index():
    return render_template("index.html", companies=get_companies())


@app.route("/run", methods=["POST"])
def run():
    uen = (request.form.get("uen") or "").strip()
    if not uen:
        return jsonify({"success": False, "output": "No UEN provided"}), 400

    mode = request.form.get("mode", "prefill")
    skip_val = request.form.get("skip_validation") == "1"

    for field, ext_map in [("excel_file", [".xlsx", ".xls"]), ("word_file", [".docx", ".doc"])]:
        f = request.files.get(field)
        if f and f.filename:
            ext = Path(f.filename).suffix.lower()
            target = INPUTS / f"{uen}{ext}"
            for old in INPUTS.glob(f"{uen}*{ext}"):
                if old == target:
                    continue
                try:
                    old.unlink()
                except OSError:
                    pass
            try:
                f.save(str(target))
            except OSError as e:
                return jsonify({"success": False, "output": f"Could not save {target.name}: {e}. Close the file if it is open elsewhere and retry."}), 200

    args = ["run", "--company", uen]
    if mode == "xbrl":
        args.append("--xbrl")
    if skip_val:
        args.append("--skip-validation")

    ok, output = run_acra(args)
    has_output = OUTPUT.exists() and any(OUTPUT.glob(f"{uen}*"))

    return jsonify({"success": ok, "output": output, "has_output": has_output, "uen": uen})


@app.route("/demo", methods=["POST"])
def demo():
    ok, output = run_acra(["demo"])
    uen = "201631437H"
    has_output = OUTPUT.exists() and any(OUTPUT.glob(f"{uen}*"))
    return jsonify({"success": ok, "output": output, "has_output": has_output, "uen": uen})


@app.route("/download/<uen>")
def download(uen):
    if not OUTPUT.exists():
        return "No output found", 404

    # Find XBRL package dir: pattern {uen}_{YYYY}
    xbrl_dir: Path | None = None
    for item in sorted(OUTPUT.iterdir()):
        parts = item.name.split("_")
        if item.is_dir() and item.name.startswith(uen) and len(parts) >= 2 and parts[-1].isdigit():
            xbrl_dir = item
            break

    buf = io.BytesIO()
    found = False
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if xbrl_dir:
            # XBRL package: all files at ZIP root (ACRA requirement — no subdirectory)
            for f in sorted(xbrl_dir.iterdir()):
                if f.is_file():
                    zf.write(f, f.name)
                    found = True
        else:
            # Pre-fill mode: include all non-zip output files for this UEN
            for item in sorted(OUTPUT.iterdir()):
                if item.name.startswith(uen) and item.suffix != ".zip" and item.is_file():
                    zf.write(item, item.name)
                    found = True

    if not found:
        return "No output found for this UEN", 404

    buf.seek(0)
    return send_file(
        buf,
        download_name=f"{uen}_xbrl.zip",
        as_attachment=True,
        mimetype="application/zip",
    )


@app.route("/output-files/<uen>")
def output_files(uen):
    if not OUTPUT.exists():
        return jsonify([])

    files = []
    for item in sorted(OUTPUT.iterdir()):
        if not item.name.startswith(uen) or item.suffix == ".zip":
            continue
        if item.is_dir():
            for f in sorted(item.rglob("*")):
                if f.is_file():
                    files.append({
                        "name": str(f.relative_to(OUTPUT)),
                        "size": f.stat().st_size,
                    })
        elif item.is_file():
            files.append({"name": item.name, "size": item.stat().st_size})
    return jsonify(files)


if __name__ == "__main__":
    print("\n  ACRA Helper — Web UI")
    print("  http://localhost:5000\n")
    app.run(debug=True, port=5000, host="0.0.0.0")
