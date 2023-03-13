# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = [('data', 'data'), ('lexicons', 'lexicons'), ('src\\assets', 'src\\assets'), ('StopwordsList', 'StopwordsList'), ('models--arpanghoshal--EmoRoBERTa', 'models--arpanghoshal--EmoRoBERTa')]
datas += collect_data_files('beautifulsoup4')
datas += collect_data_files('dash')
datas += collect_data_files('dash-core-components')
datas += collect_data_files('dash-html-components')
datas += collect_data_files('dash-table')
datas += collect_data_files('Flask')
datas += collect_data_files('Flask-Compress')
datas += collect_data_files('google-auth')
datas += collect_data_files('google-auth-oauthlib')
datas += collect_data_files('google-pasta')
datas += collect_data_files('googletrans')
datas += collect_data_files('huggingface_hub')
datas += collect_data_files('ipykernel')
datas += collect_data_files('ipython')
datas += collect_data_files('ipywidgets')
datas += collect_data_files('NRCLex')
datas += collect_data_files('numpy')
datas += collect_data_files('pandas')
datas += collect_data_files('pandas-profiling')
datas += collect_data_files('pipenv')
datas += collect_data_files('plotly')
datas += collect_data_files('pwinput')
datas += collect_data_files('plotly')
datas += collect_data_files('pywin32')
datas += collect_data_files('pywin32-ctypes')
datas += collect_data_files('regex')
datas += collect_data_files('requests')
datas += collect_data_files('requests-oauthlib')
datas += collect_data_files('scikit-learn')
datas += collect_data_files('sklearn')
datas += collect_data_files('tensorboard')
datas += collect_data_files('tensorboard-data-server')
datas += collect_data_files('tensorboard-plugin-wit')
datas += collect_data_files('tensorflow')
datas += collect_data_files('tensorflow-cpu')
datas += collect_data_files('tensorflow-estimator')
datas += collect_data_files('tensorflow-hub')
datas += collect_data_files('tensorflow-intel')
datas += collect_data_files('tensorflow-io-gcs-filesystem')
datas += collect_data_files('tensorflow-text')
datas += collect_data_files('termcolor')
datas += collect_data_files('textblob')
datas += collect_data_files('textstat')
datas += collect_data_files('threadpoolctl')
datas += collect_data_files('tokenizers')
datas += collect_data_files('torch')
datas += collect_data_files('tornado')
datas += collect_data_files('transformers')
datas += collect_data_files('Unidecode')
datas += collect_data_files('urllib3')
datas += collect_data_files('vaderSentiment')
datas += collect_data_files('validators')
datas += collect_data_files('virtualenv')
datas += collect_data_files('virtualenv-clone')
datas += collect_data_files('visions')
datas += collect_data_files('Werkzeug')
datas += collect_data_files('yake')
datas += collect_data_files('yarl')


datas += copy_metadata('beautifulsoup4')
datas += copy_metadata('dash')
datas += copy_metadata('dash-core-components')
datas += copy_metadata('dash-html-components')
datas += copy_metadata('dash-table')
datas += copy_metadata('filelock')
datas += copy_metadata('Flask')
datas += copy_metadata('Flask-Compress')
datas += copy_metadata('google-auth')
datas += copy_metadata('google-auth-oauthlib')
datas += copy_metadata('google-pasta')
datas += copy_metadata('googletrans')
datas += copy_metadata('huggingface_hub')
datas += copy_metadata('ipykernel')
datas += copy_metadata('ipython')
datas += copy_metadata('ipywidgets')
datas += copy_metadata('NRCLex')
datas += copy_metadata('numpy')
datas += copy_metadata('packaging')
datas += copy_metadata('pandas')
datas += copy_metadata('pandas-profiling')
datas += copy_metadata('pipenv')
datas += copy_metadata('plotly')
datas += copy_metadata('pwinput')
datas += copy_metadata('plotly')
datas += copy_metadata('pywin32')
datas += copy_metadata('pywin32-ctypes')
datas += copy_metadata('regex')
datas += copy_metadata('requests')
datas += copy_metadata('requests-oauthlib')
datas += copy_metadata('scikit-learn')
datas += copy_metadata('sklearn')
datas += copy_metadata('tqdm')
datas += copy_metadata('tensorboard')
datas += copy_metadata('tensorboard-data-server')
datas += copy_metadata('tensorboard-plugin-wit')
datas += copy_metadata('tensorflow')
datas += copy_metadata('tensorflow-cpu')
datas += copy_metadata('tensorflow-estimator')
datas += copy_metadata('tensorflow-hub')
datas += copy_metadata('tensorflow-intel')
datas += copy_metadata('tensorflow-io-gcs-filesystem')
datas += copy_metadata('tensorflow-text')
datas += copy_metadata('termcolor')
datas += copy_metadata('textblob')
datas += copy_metadata('textstat')
datas += copy_metadata('threadpoolctl')
datas += copy_metadata('tokenizers')
datas += copy_metadata('torch')
datas += copy_metadata('tornado')
datas += copy_metadata('transformers')
datas += copy_metadata('Unidecode')
datas += copy_metadata('urllib3')
datas += copy_metadata('vaderSentiment')
datas += copy_metadata('validators')
datas += copy_metadata('virtualenv')
datas += copy_metadata('virtualenv-clone')
datas += copy_metadata('visions')
datas += copy_metadata('Werkzeug')
datas += copy_metadata('yake')
datas += copy_metadata('yarl')


block_cipher = None


a = Analysis(
    ['iniciarPrograma.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['tensorflow', 'pytorch', 'huggingface_hub'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='iniciarPrograma',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='iniciarPrograma',
)
