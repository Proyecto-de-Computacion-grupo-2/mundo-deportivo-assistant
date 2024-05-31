from setuptools import setup, find_packages

setup(
    name = "scrape-demo",
    version = "1.2.4",
    packages = find_packages(),
    install_requires = ["beautifulsoup4", "deprecated", "matplotlib", "mysql-connector-python", "numpy", "pandas",
                        "Pillow", "pycryptodome", "python-telegram-bot","requests", "scikit-learn", "selenium",
                        "statsmodels", "tensorflow==2.16.1", "tf-keras", "transformers", "tqdm"
                        ],
    package_data = {"scrape-demo": ["fonts/DejaVuSerifCondensed-Italic.ttf"]},
    author = "Lekker",
    author_email = "NoneType@NotCallable.com",
    description = "General use functions used in scrape-demo project."
)
