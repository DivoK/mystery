import json
import pathlib
import random
import tempfile
import urllib.request
import typing

import setuptools

# Load the configuration file.
CONFIG_PATH = pathlib.Path('config.json')
CONFIG = json.load(CONFIG_PATH.open('r'))


def get_package_list() -> typing.List[str]:
    """
    Get a list of possible packages.

    :return: list of package names.
    :rtype: typing.List[str]
    """
    try:
        # Get the top PyPI packages and use one of them.
        response = urllib.request.urlopen(
            CONFIG['top_pypi_packages_link']
        )  # TODO: give credit. thank you!
        possible_packages_raw = response.read()
    except urllib.request.URLError:
        # Use the offline backup file.
        with open(CONFIG['top_pypi_packages_offline_backup'], 'r') as backup_file:
            possible_packages_raw = backup_file.read()
    return json.loads(possible_packages_raw)['rows'][: CONFIG['top_x_packages']]


def choose_mystery_package() -> str:
    """
    Choose the underlying mysterious package.

    :return: mystery package name.
    :rtype: str
    """
    # To keep the chosen dependency consistent in between setup.py runs, 'mystery' uses a temporary lockfile.
    dep_lock_path = pathlib.Path(tempfile.gettempdir()).joinpath(
        CONFIG['lockfile_name']
    )
    if dep_lock_path.exists():
        # Use the locked package and unlink the lockfile.
        chosen_package = dep_lock_path.read_text().strip()
        dep_lock_path.unlink()
    else:
        # Choose a package and create the lockfile.
        possible_packages = get_package_list()
        chosen_package = random.choice(
            [package['project'] for package in possible_packages]
        )
        dep_lock_path.write_text(chosen_package)  # Lock the chosen package of course.
    return chosen_package


def write_init_py(package_name: str) -> None:
    """
    Dynamically write the __init__.py for the package using the chosen package.

    :param chosen_package: mystery package name.
    :type chosen_package: str
    :rtype: None
    """
    package_name = package_name.replace('-', '_')  # Transform to eligible package name.
    init_py_path = pathlib.Path('mystery')
    init_py_path.mkdir(exist_ok=True)
    init_py_path = init_py_path / '__init__.py'
    init_py_path.write_text(
        f'''
def _import_guard():
    # I'd like to get rid of all the imports inside the function's scope.
    # Less headache during cleanup.
    try:
        import {package_name}
    except ImportError as error:
        print('Internal error:', error)
        print("The mystery module wasn't playing nice. Sorry!")
    import sys
    sys.modules['mystery'] = {package_name}
_import_guard()
del _import_guard
'''
    )


CHOSEN_PACKAGE = choose_mystery_package()
write_init_py(CHOSEN_PACKAGE)

setuptools.setup(
    name='mystery',
    description='It is a riddle, wrapped in a mystery, inside an enigma.',
    packages=setuptools.find_packages(),
    install_requires=[CHOSEN_PACKAGE],
    include_package_data=True,
)
