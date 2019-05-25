import json
import pathlib
import random
import tempfile
import urllib.request

import setuptools

config_path = pathlib.Path('config.json')
config = json.load(config_path.open('r'))

# TODO: give credit. thank you!
response = urllib.request.urlopen(config['top_pypi_packages_link'])
possible_packages = json.loads(response.read())['rows'][:config['top_x_packages']]
chosen_dep = random.choice([package['project'] for package in possible_packages])

dep_lock_path = pathlib.Path(tempfile.gettempdir()).joinpath(config['lockfile_name'])

if dep_lock_path.exists():
    chosen_dep = dep_lock_path.read_text().strip()
    dep_lock_path.unlink()
else:
    dep_lock_path.write_text(chosen_dep)

init_py_path = pathlib.Path('mystery')
init_py_path.mkdir(exist_ok=True)
init_py_path = init_py_path / '__init__.py'
init_py_path.write_text(
    f'''
def _import_guard():
    # I'd like to get rid of all the imports inside the function's scope.
    # Less headache during cleanup.
    import {chosen_dep}
    import sys
    sys.modules['mystery'] = {chosen_dep}
_import_guard()
del _import_guard
'''
)

setuptools.setup(
    name='mystery',
    description='It is a riddle, wrapped in a mystery, inside an enigma.',
    packages=setuptools.find_packages(),
    install_requires=[chosen_dep],
)
