from setuptools import setup, find_packages
setup(
    name="Hegram",
    version="1.0.0",
    description="Telegram bot api via requests",
    url="https://github.com/metelity/Hegram",
    author="metelity",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
