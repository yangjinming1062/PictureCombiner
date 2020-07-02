import setuptools

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="PictureCombiner",
    version="1.0.1",
    author="YangJinming",
    author_email="944596544@qq.com",
    description="提供图片拼接功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yangjinming1062/PictureCombiner",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)