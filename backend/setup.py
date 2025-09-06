from setuptools import setup, find_packages

setup(
    name="advanced-url-scanner",
    version="1.0.0",
    description="Professional URL monitoring and vulnerability assessment tool",
    author="Security Researcher",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "colorama>=0.4.6",
        "rich>=13.0.0",
        "click>=8.1.0",
    ],
    entry_points={
        'console_scripts': [
            'url-scanner=backend.app:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
