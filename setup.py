import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="git_stalk",
    version="1.6.0",
    author="Aashutosh Rathi",
    author_email="aashutoshrathi@gmail.com",
    description="For stalkers like Daddu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aashutoshrathi/git-stalk-cli",
    packages=setuptools.find_packages(),
    install_requires=['requests', 'prettytable', 'python-dateutil', 'tox', 'docopt'],
    classifiers=(
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
    entry_points={
        'console_scripts': [
            'stalk = git_stalk.stalk:run',
        ],
    }
)
