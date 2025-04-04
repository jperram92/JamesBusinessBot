from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="business-meeting-assistant",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive meeting assistant bot that can join meetings, take notes, update JIRA tickets, and generate documentation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/business-meeting-assistant",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "botframework-connector>=4.14.0",
        "google-api-python-client>=2.0.0",
        "openai>=1.0.0",
        "python-docx>=0.8.11",
        "python-pptx>=0.6.21",
        "jira>=3.5.1",
        "python-dotenv>=0.19.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.2",
        "python-multipart>=0.0.5",
        "azure-cognitiveservices-speech>=1.20.0",
        "requests>=2.31.0",
        "python-jose>=3.3.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.16.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.2",
            "flake8>=3.9.2",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "meeting-bot=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.docx", "templates/*.pptx"],
    },
) 