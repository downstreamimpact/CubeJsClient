from setuptools import setup

setup(
    name="CubeJsClient",
    version="0.1.0",
    description="Cube.js Client for Python",
    url="https://github.com/downstreamimpact/CubeJsClient",
    author="Matt Ferrante",
    author_email="matt@downstreamimpact.com",
    license="MIT",
    packages=["CubeJsClient"],
    install_requires=[
        "cryptography==2.8",
        "PyJWT==1.7.1",
        "requests==2.22.0",
    ],
    download_url='https://github.com/downstreamimpact/CubeJsClient/tarball/master',
    zip_safe=False,
    tests_require=[
        "black==19.10b0",
        "pylint==2.4.3",
    ],
)
