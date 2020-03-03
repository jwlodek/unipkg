from setuptools import setup, find_packages

with open('requirements.txt', 'r') as req_fp:
    required_packages = req_fp.readlines()

# Use README for long description
with open('README.md', 'r') as readme_fp:
    long_description = readme_fp.read()

setup(
    name="unipkg",
    version="0.0.1",
    author="Jakub Wlodek",
    author_email="jwlodek.dev@gmail.com",
    description="A command line user interface for managing all the installed package managers on your system.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="BSD 3-Clause",
    keywords="tui command-line cli cui curses packager pip apt npm yum",
    url="https://github.com/jwlodek/unipkg",
    packages = find_packages(exclude=['tests', 'docs']),
    entry_points={
        'console_scripts': [
            'unipkg = unipkg:main',
        ],
    },
    install_requires=required_packages,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

)