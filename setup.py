import sys
from setuptools import setup, find_packages

if sys.version_info.major < 2:
    sys.exit("Error: Please upgrade to Python3")

setup(name="bm_bot",
      version="0.1",
      description="Bill Murray bot",
      url="https://github.com/dmerejkowsky/bill-murray-bot",
      author="Dimitri Merejkowsky",
      author_email="d.merej@gmail.com",
      license="BSD",
      py_modules=["bm_bot"],
      install_requires=[
        "Mastodon.py",
        "path.py",
        "ruamel.yaml",
        "twitter",
      ],
      entry_points={
        "console_scripts": [
          "bill-murray-bot = bm_bot:main",
        ]
      })
