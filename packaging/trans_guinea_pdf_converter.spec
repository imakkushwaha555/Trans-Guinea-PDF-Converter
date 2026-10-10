from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_all, collect_submodules


project_root = Path(SPECPATH).resolve().parent
datas = [
    (str(project_root / "templates"), "templates"),
    (str(project_root / "static"), "static"),
]
binaries = []
hiddenimports = []

for package_name in ("pdf2docx", "pdfplumber", "pymupdf", "pandas", "openpyxl", "docx", "webview"):
    package_datas, package_binaries, package_hiddenimports = collect_all(package_name)
    datas.extend(package_datas)
    binaries.extend(package_binaries)
    hiddenimports.extend(package_hiddenimports)

hiddenimports.extend(collect_submodules("pdf2docx"))

analysis = Analysis(
    [str(project_root / "run.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(analysis.pure)
executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="Trans-Guinea PDF Converter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=str(project_root / "assets" / ("app.icns" if sys.platform == "darwin" else "app.ico")),
)

collection = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Trans-Guinea PDF Converter",
)

if sys.platform == "darwin":
    app_bundle = BUNDLE(
        collection,
        name="Trans-Guinea PDF Converter.app",
        icon=str(project_root / "assets" / "app.icns"),
        bundle_identifier="io.github.imakkushwaha555.transguineapdfconverter",
        info_plist={"CFBundleShortVersionString": "0.1.0", "NSHighResolutionCapable": True},
    )