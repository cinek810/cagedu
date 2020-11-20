import pathlib
import os
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
#README = (HERE / "README.md").read_text()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read(str(HERE)+"/README.md")

# This call to setup() does all the work
setup(
    name="du-analyzer",
    version="0.0.1",
    description="Read the latest Real Python tutorials",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/realpython/reader",
    author="Real Python",
    author_email="office@realpython.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3.6"
        "Programming Language :: Python :: 2.7"
    ],
    packages=["cagedu"],
    include_package_data=True,
    install_requires=["anytree"],
    entry_points={
        "console_scripts": [
            "du-analyzer = cagedu.command_line:main",
        ]
    },
)

