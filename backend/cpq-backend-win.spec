# -*- mode: python ; coding: utf-8 -*-
"""
CPQ Agent Windows PyInstaller Spec
- One-file mode: 输出单个 cpq-backend.exe
- 包含 skills/ 目录作为资源数据
- 排除无用库以缩小体积
"""
block_cipher = None

a = Analysis(
    ['backend_bin.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('skills', 'skills'),
    ],
    hiddenimports=[
        'langchain_community',
        'langchain_core',
        'langchain_deepseek',
        'pydantic.v1',
        'httpx',
        'openai',
        'tiktoken',
        'tiktoken_ext',
        'uvicorn.logging',
        'uvicorn.loops.auto',
        'uvicorn.lifespan.on',
        'uvicorn.protocols.http.auto',
        'deepagents',
        'langgraph',
        'langgraph.checkpoint',
        'langgraph.prebuilt',
        'langgraph.pregel',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx',
        'matplotlib', 'pandas', 'numpy', 'scipy', 'sympy',
        'IPython', 'jupyter', 'jupyter_client', 'notebook',
        'nbformat', 'nbconvert', 'qtconsole',
        'test', 'tests', 'unittest', 'setuptools', 'pip', 'wheel', 'distutils',
        'Cython', 'Cython.Plex',
        'PIL', 'cv2', 'torch', 'tensorflow', 'transformers', 'nltk', 'gensim', 'spacy',
        'dash', 'plotly',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='cpq-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
