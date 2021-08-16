# Serverless guru code challenge CI/CD infra

This repository contains an infrastructure CDK project to create and manage all Serverless guru code challenge CI/CD infrastructure.

- [Serverless guru code challenge CI/CD infra](#serverless-guru-code-challenge-cicd-infra)
  - [Project setup](#project-setup)
    - [Pre-commit](#pre-commit)
      - [Use pre-commit](#use-pre-commit)
  - [Useful commands](#useful-commands)
  - [References](#references)

## Project setup

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the .env
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```bash
python -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```bash
source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```bash
.env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```bash
pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```bash
cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

### Pre-commit

A pre-commit configuration file is provided in this repo to perform some linterns, validations and so on in order to avoid commit code to the repo that later will fail in validations step in the build pipeline.

The first execution can be slower because of installation of dependencies. Further executions will use the pre-commit cache.

#### Use pre-commit

Once you have all the requirements achieved, you have to install pre-commit in the local repository:

```shell
pre-commit install
```

And you can test it's working with the following:

```shell
➜ pre-commit run --all-files

Trim Trailing Whitespace.................................................Passed
Check for added large files..............................................Passed
Check python ast.........................................................Passed
Check for case conflicts.................................................Passed
Check that executables have shebangs.................(no files to check)Skipped
Check JSON...............................................................Passed
Check for merge conflicts................................................Passed
Check vcs permalinks.....................................................Passed
Detect AWS Credentials...................................................Passed
Don't commit to branch...................................................Passed
Check github workflows format............................................Passed
Shell Syntax Check.......................................................Passed
Yaml lintern.............................................................Passed
Dockerfile linter........................................................Passed
Markdownlint.............................................................Passed
Python dependencies security check.......................................Passed
Flake8 linter............................................................Passed
Pycodestyle linter.......................................................Passed
Black python formatter...................................................Passed
```

## Useful commands

- `cdk ls`                                        list all stacks in the app
- `cdk synth`                                     emits the synthesized CloudFormation template
- `cdk deploy`                                    deploy this stack to your default AWS account/region
- `cdk diff`                                      compare deployed stack with current state
- `cdk docs`                                      open CDK documentation
- `pycodestyle . --exclude .env`                  performs pycodestyle linter (requires pycodestyle to be installed)

Enjoy!

## References

- [CDK reference](https://docs.aws.amazon.com/cdk/api/latest/python/index.html)
