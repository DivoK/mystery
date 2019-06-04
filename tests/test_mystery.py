import importlib
import json
import pathlib
import tempfile
import typing

import findimports

import mystery

# Imports that appear in mystery's __init__.py that are not the mystery package import.
ALLOWED_IMPORTS = ['sys']


def teardown_module(_):
    # Load the configuration file.
    config_path = pathlib.Path('config.json')
    config = json.load(config_path.open('r'))
    dep_lock_path = pathlib.Path(tempfile.gettempdir()).joinpath(
        config['lockfile_name']
    )
    try:
        dep_lock_path.unlink()
    except FileNotFoundError:
        pass


def test_mystery_package():
    package_imports: typing.List[findimports.ImportInfo] = findimports.find_imports(
        mystery.__mystery_init_py__
    )
    for package_import in package_imports:
        if package_import.name in ALLOWED_IMPORTS:
            continue
        try:
            importlib.import_module(package_import.name)
        except ModuleNotFoundError:
            # Package listed (PyPI) name is different than it's actual package name (the one you import).
            assert package_import.name == mystery.__mystery_package_name__
        else:
            # No exception - package is importable and mystery should have worked.
            assert package_import.name == mystery.__name__
