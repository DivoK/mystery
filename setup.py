import setuptools
import random
import pathlib
import tempfile

POSSIBLE_DEPS = [
    'requests',
    'colorama',
    'loguru',
    'pygments',
    'pytest',
    'freezegun',
]

dep = random.choice(POSSIBLE_DEPS)

dep_lock_path = pathlib.Path(f'{tempfile.gettempdir()}/._pkg_dep.lock')

if dep_lock_path.exists():
    dep = dep_lock_path.read_text().strip()
    dep_lock_path.unlink()
else:
    dep_lock_path.write_text(dep)

init_py_path = pathlib.Path('mystery')
init_py_path.mkdir(exist_ok=True)
init_py_path = init_py_path / '__init__.py'
init_py_path.write_text(
    f'''
def _import_guard():
    import {dep}
    import sys
    sys.modules['mystery'] = {dep}
_import_guard()
del _import_guard
'''
)

setuptools.setup(
    name='mystery',
    description='It is a riddle, wrapped in a mystery, inside an enigma.',
    packages=setuptools.find_packages(),
    install_requires=[dep],
)
