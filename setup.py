from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name='coinbase-advancedtrade-python',
    version='0.1.0',
    description='The unofficial Python client for the AlphaSquared API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Rhett Reisman',
    author_email='rhett@rhett.blog',
    license='MIT',
    url='https://github.com/rhettre/alphasquared-py',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    keywords=['alphasquared', 'coinbase', 'gemini', 'kraken', 'orderbook', 'trade', 'bitcoin', 'ethereum', 'BTC', 'ETH',
              'client', 'api', 'wrapper', 'exchange', 'crypto', 'currency', 'trading', 'trading-api', 'coinbase',
              'advanced-trade', 'prime', 'coinbaseadvancedtrade', 'coinbase-advanced-trade','fear-and-greed-index'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.9',
)