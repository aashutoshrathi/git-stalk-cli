import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="git-stalk",
    version="0.0.1",
    author="Aashutosh Rathi",
    author_email="aashutoshrathi@gmail.com",
    description="For stalkers like Daddu",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aashutoshrathi/git-stalk-cli",
    packages=setuptools.find_packages(),
    install_requires=['bs4', 'request'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GENERAL PUBLIC License",
        "Operating System :: OS Independent",
    ),
)