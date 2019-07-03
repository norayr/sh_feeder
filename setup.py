import setuptools, os

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pod-feeder-v2",
    version=os.environ["CI_COMMIT_TAG"],
    author="Brian Ó",
    author_email="brian@pancrypticon.net",
    description="A utility to publish RSS/Atom feeds to Diaspora*",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/brianodonnell/pod_feeder_v2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3",
    install_requires=["diaspy-api", "feedparser", "html2text", "urllib3"],
    entry_points={
        "console_scripts": [
            "pod-feeder=pod_feeder_v2.pod_feeder:main",
            "pf-clean-db=pod_feeder_v2.clean_db:main",
        ]
    },
    keywords="atom bot diaspora feeds newsfeeds rss social syndication",
)
