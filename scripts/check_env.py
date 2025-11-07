"""Quick environment diagnostics: prints versions of core packages.
Run: python scripts/check_env.py
"""
from importlib import import_module
from textwrap import indent

CORE_PACKAGES = [
    ("python", None),
    ("pandas", "__version__"),
    ("numpy", "__version__"),
    ("streamlit", "__version__"),
    ("scikit_learn", "__version__"),  # module name is sklearn, attribute __version__
    ("sklearn", "__version__"),  # real import; kept separate for clarity
    ("tqdm", "__version__"),
    ("pydantic", "__version__"),
    ("PyPDF2", "__version__"),
    ("python_docx", None),  # docx package has no simple __version__
    ("docx", None),  # actual import name
    ("openpyxl", "__version__"),
    ("requests", "__version__"),
    ("yaml", "__version__"),  # PyYAML
]

def get_version(mod_name: str, attr: str | None):
    try:
        m = import_module(mod_name)
    except Exception as e:  # noqa: BLE001
        return f"NOT INSTALLED ({e.__class__.__name__}: {e})"
    if attr and hasattr(m, attr):
        return getattr(m, attr)
    # Fallbacks for known packages without __version__
    if mod_name in {"python_docx", "docx"}:
        return "installed"
    return "UNKNOWN"

if __name__ == "main" or __name__ == "__main__":
    import platform, sys
    print("Environment summary:\n")
    print(f"Python: {platform.python_version()} ({sys.executable})")
    rows = []
    for name, attr in CORE_PACKAGES:
        rows.append(f"{name:15} -> {get_version(name, attr)}")
    print(indent("\n".join(rows), prefix="  "))
    print("\nTip: keep versions aligned across requirements.* files to avoid resolution conflicts.")
