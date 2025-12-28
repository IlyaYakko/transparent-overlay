from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="transparent-overlay",
    version="2.6.1",
    author="Илья Яковенко",
    author_email="ilya.a.yakovenko@gmail.com",
    description="High-performance transparent graphics overlay for Windows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/B-ZONE/transparent-overlay",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.7,<3.14",
    install_requires=[
        "numpy>=1.19.0",
        "Pillow>=8.0.0",
        "pywin32>=300;platform_system=='Windows'",
    ],
    extras_require={
        'examples': [
            'psutil>=5.8.0',
            'pyautogui>=0.9.0',
        ],
        'speedup': [
            'numba>=0.56.0'
        ]
    },
    keywords=["overlay", "graphics", "transparent", "windows", "gdi"],
)
