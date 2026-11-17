from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mewmatrix",
    version="2.2.0",
    description="A cmatrix alternative with multi-color mixing and cat mode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zagadka298-design/mewmatrix",
    author="zagadka298",
    license="MIT",
    py_modules=["mewmatrix"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mewmatrix=mewmatrix:main",
            "meowmatrix=mewmatrix:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Terminals",
    ],
)
