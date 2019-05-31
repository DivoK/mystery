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


def _get_package_list() -> typing.List[str]:
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


def _choose_mystery_package() -> str:
    """
    Choose the underlying mysterious package and handle the lockfile's state.

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
        possible_packages = _get_package_list()
        chosen_package = random.choice(
            [package['project'] for package in possible_packages]
        )
        dep_lock_path.write_text(chosen_package)  # Lock the chosen package of course.
    return chosen_package


def _fix_package_name(package_name: str) -> str:
    """
    Fix the package name so it could be placed in the __init__.py file.

    :param package_name: mystery package name.
    :type package_name: str
    :return: fixed mystery package name.
    :rtype: str
    """
    # Transform to eligible package name.
    fixed_package_name = package_name.replace('-', '_')
    # special case for the 'backports' modules.
    if fixed_package_name.startswith('backports_'):
        fixed_package_name.replace('_', '.', count=1)
    return fixed_package_name


def _write_init_py(package_name: str) -> None:
    """
    Dynamically write the __init__.py for the package using the chosen package.

    :param chosen_package: mystery package name.
    :type chosen_package: str
    :rtype: None
    """
    package_name = _fix_package_name(package_name)
    init_py_path = pathlib.Path('mystery')
    init_py_path.mkdir(exist_ok=True)
    init_py_path = init_py_path / '__init__.py'
    init_py_path.write_text(
        f'''
# I'd like not to affect the current imported modules (besides 'mystery' of course).
# Using a function's scope to contain the imports makes it less of a headache during cleanup.
def _import_guard():
    """
    Attempt to import the chosen package and add it to sys.modules.
    """
    try:
        import {package_name}
    except ImportError as error:
        print('Internal error:', error)
        print("The mystery module wasn't playing nice. Sorry!")
        return
    import sys
    sys.modules['mystery'] = {package_name}
_import_guard()
del _import_guard
'''
    )


def _get_long_description_data() -> typing.Tuple[str, str]:
    """
    Get data regarding the long description of the package.

    :return: tuple of the README.md text and the long_description type.
    :rtype: typing.Tuple[str, str]
    """
    with open('README.md', 'r') as readme:
        return (readme.read(), 'text/markdown')


CHOSEN_PACKAGE = _choose_mystery_package()
_write_init_py(CHOSEN_PACKAGE)
LONG_DESCRIPTION, LONG_DESCRIPTION_CONTENT_TYPE = _get_long_description_data()

setuptools.setup(
    name='mystery',
    description='It is a riddle, wrapped in a mystery, inside an enigma.',
    packages=setuptools.find_packages(),
    install_requires=[CHOSEN_PACKAGE],
    include_package_data=True,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
)
