from setuptools import setup, find_packages
import io

# 使用 UTF-8 编码读取 README.md
with io.open("README.md", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="Postman2Jmeter",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt5>=5.15.10",
        "jinja2>=3.1.3",
    ],
    entry_points={
        "console_scripts": [
            "Postman2Jmeter=Postman2Jmeter.main:main",
        ],
    },
    author="程序员七平",
    author_email="z7ping@outlook.com",
    description="Convert Postman/ApiPost collections to JMeter test plans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/z7ping/Postman2Jmeter",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        'Postman2Jmeter': [
            'resources/*',
            'templates/*',  # 如果有模板文件
        ],
    },
) 