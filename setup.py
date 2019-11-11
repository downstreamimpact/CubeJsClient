from setuptools import setup

setup(
    name="cubejsclient",
    version="0.1.0",
    description="Cube.js Client for Python",
    url="https://github.com/downstreamimpact/CubeJsClient",
    author="Matt Ferrante",
    author_email="matt@downstreamimpact.com",
    license="MIT",
    packages=["CubeJsClient"],
    install_requires=[
        "cryptography>=2.5",
        "PyJWT>=1.6.4",
        "requests>=2.20.0",
    ],
    download_url='https://github.com/downstreamimpact/CubeJsClient/tarball/master',
    zip_safe=False,
    tests_require=[
        "black==19.10b0",
        "pylint==2.4.3",
    ],
)
