# -*- mode: python ; coding: utf-8 -*-
"""
CPQ Agent Windows PyInstaller Spec
- One-file mode: 输出单个 cpq-backend.exe
- 隐藏导入补全: langchain_community, pydantic.v1, httpx, openai, tiktoken, uvicorn.logging
- 排除 GUI 库缩小体积
- 注入 skills/ 目录作为资源数据
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
        # deepagents / langchain 隐式依赖
        'langchain_community',
        'langchain_core',
        'langchain_deepseek',
        'pydantic.v1',
        'httpx',
        'openai',
        'tiktoken',
        'tiktoken_ext',
        # uvicorn 子模块（Windows 上有时检测不到）
        'uvicorn.logging',
        'uvicorn.loops.auto',
        'uvicorn.lifespan.on',
        'uvicorn.protocols.http.auto',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # GUI 框架（不依赖，排除可大幅减少体积）
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
        # 数据科学库（不依赖）
        'matplotlib',
        'pandas',
        'numpy',
        'scipy',
        'sympy',
        # Jupyter 生态（不依赖）
        'IPython',
        'jupyter',
        'jupyter_client',
        'notebook',
        'nbformat',
        'nbconvert',
        'qtconsole',
        # 开发工具（不依赖）
        'test',
        'tests',
        'unittest',
        'setuptools',
        'pip',
        'wheel',
        'distutils',
        'Cython',
        'Cython.Plex',
        # 其他大体积但不需要的
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
        'transformers',
        'nltk',
        'gensim',
        'spacy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 单文件 exe（不含 COLLECT → 输出为单个 cpq-backend.exe）
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
