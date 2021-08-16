import setuptools


setuptools.setup(
    name="CICD infrastructure resources",
    version="0.0.1",
    description="CDK project for CICD infrastructure resources",
    long_description="CDK project for CICD infrastructure resources",
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "aws-cdk.core==1.100.0",
        "aws-cdk.aws-ecr==1.100.0",
        "aws-cdk.aws-s3==1.100.0",
        "aws-cdk.aws-iam==1.100.0",
        "aws-cdk.aws-codebuild==1.100.0",
        "aws-cdk.aws-logs==1.100.0",
        "aws-cdk.aws-ssm==1.100.0",
        "pyyaml>=5.4",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
