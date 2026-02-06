import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

__version__ = "0.0.0"

REPO_NAME = "Actyv_AI"
AUTHOR_USER_NAME = "ArProvat"
SRC_REPO = "app" 
AUTHOR_EMAIL = "provatar0@gmail.com"

setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="The fitness app developing is designed to offer a comprehensive fitness experience, combining personalized coaching with social interaction and a multi-vendor marketplace. This app is not just about tracking workouts and nutrition;",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "app"}, 
    packages=setuptools.find_packages(where="app")
)