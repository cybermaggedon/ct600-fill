import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ct600-fill",
    version="1.0",
    author="Cybermaggedon",
    author_email="mark@cyberapocalypse.co.uk",
    description="Fill in a CT600 PDF form",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cybermaggedon/ct600-fill",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
    ],
    scripts=[
        "scripts/ct600-fill"
    ]
)
