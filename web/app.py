from flask import Flask, render_template, request, jsonify, send_file
import contextlib, io, os, re, socket, sys, threading, webbrowser, zipfile
from pathlib import Path
import yaml

FROZEN = getattr(sys, "frozen", False)

if FROZEN:
    # windowed (--noconsole) builds have no real stdio; print()/Console()
    # writes to None would crash without a sink to redirect to.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

# Packaged (.exe): keep companies/inputs/output next to the executable, not in
# PyInstaller's transient extraction folder. Dev/source run: repo root.
BASE = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent.parent
INPUTS = BASE / "inputs"
OUTPUT = BASE / "output"
COMPANIES = BASE / "companies"

if not FROZEN:
    sys.path.insert(0, str(BASE / "src"))

import acra_helper.cli as acra_cli  # noqa: E402

# acra_helper.cli resolves company/input/output paths off its own module-level
# BASE (repo-root-relative) — override it to match this app's BASE so a
# packaged build reads/writes next to the .exe instead of inside the bundle.
acra_cli.BASE = BASE

app = Flask(
    __name__,
    template_folder=str(Path(sys._MEIPASS) / "templates") if FROZEN else "templates",
)

for d in (INPUTS, OUTPUT, COMPANIES):
    d.mkdir(parents=True, exist_ok=True)


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


def run_acra(fn, *args, **kwargs) -> tuple[bool, str]:
    """Run an acra_helper.cli entry point in-process, capturing its console output.

    Runs in-process (rather than spawning sys.executable as a subprocess) so
    this works both from source and inside a frozen .exe, where sys.executable
    is the app itself, not a Python interpreter.
    """
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            returncode = fn(*args, **kwargs)
        ok = returncode == 0
    except Exception as e:
        buf.write(f"\nError: {e}")
        ok = False
    return ok, strip_ansi(buf.getvalue()).strip()


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

    ok, output = run_acra(
        acra_cli.run_company, uen, skip_validation=skip_val, generate_xbrl=(mode == "xbrl")
    )
    has_output = OUTPUT.exists() and any(OUTPUT.glob(f"{uen}*"))

    return jsonify({"success": ok, "output": output, "has_output": has_output, "uen": uen})


@app.route("/demo", methods=["POST"])
def demo():
    ok, output = run_acra(acra_cli.demo)
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


def _free_port(preferred: int = 5000) -> int:
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return preferred


if __name__ == "__main__":
    port = _free_port(5000)
    url = f"http://localhost:{port}"
    print("\n  ACRA Helper — Web UI")
    print(f"  {url}\n")

    if FROZEN:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        app.run(debug=False, use_reloader=False, port=port, host="127.0.0.1")
    else:
        app.run(debug=True, port=port, host="0.0.0.0")
