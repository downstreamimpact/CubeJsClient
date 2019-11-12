from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="CubeJsClient",
    version="0.1.1",
    description="Cube.js Client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/downstreamimpact/CubeJsClient",
    author="Matt Ferrante",
    author_email="matt@downstreamimpact.com",
    license="MIT",
    packages=["cube_js_client"],
    install_requires=[
        "cryptography>=2.5",
        "PyJWT>=1.6.4",
        "requests>=2.20.0",
    ],
    tests_require=[
        "black==19.10b0",
        "pylint==2.4.3",
    ],
)
