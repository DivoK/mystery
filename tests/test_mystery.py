import mystery
import findimports
import typing
import json
import pathlib
import tempfile

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
    # print(f'mystery_file: {mystery.__file__}')
    # print(f'mystery_name: {mystery.__name__}')
    package_imports: typing.List[findimports.ImportInfo] = findimports.find_imports(mystery.__mystery_init_py__)
    for package_import in package_imports:
        if package_import.name in ALLOWED_IMPORTS:
            continue
        assert package_import.name == mystery.__name__
