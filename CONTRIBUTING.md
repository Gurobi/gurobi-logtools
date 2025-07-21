# Contributing to gurobi-logtools

Welcome to Gurobi gurobi-logtools!

We value your experience in using gurobi-logtools and would like to encourage you to
contribute directly to this project.

## How to report bugs or submit feature requests
If you encounter a bug, or you think there is a need for a new feature, we recommend to
first add the bug report or feature request to the gurobi-logtools' [GitHub issue
tracker](https://github.com/Gurobi/gurobi-logtools/issues).

It would be great if you add a minimal reproducible example when reporting a bug, or
include reasoning on how the new requested feature improves the gurobi-logtools.

## Creating a development environment

The first steps are to create a fork of gurobi-logtools in your github account, then clone
your fork to your machine.

This repository has been setup to use [uv](https://github.com/astral-sh/uv).  You are not
required to use uv but you are encouraged.

With uv installed run `uv sync --locked` to install the project and its (dev) dependencies
into a virtual environment.

Then run `uv run pre-commit install` to install pre-commit.

If your machine is setup to use the `make` command then you can execute both of the above
commands using `make init`.  Additionally the [Makefile](./Makefile) contains other shortcuts
to perform tasks such as:

- linting
- formatting
- type checking (with Mypy)
- testing (with or without tox)

If you are not using `make` you should still familiarize yourself with the underlying
uv commands.


## Submitting changes
We welcome your contribution in directly tackling some of the issues.

We use the GitHub pull request workflow. Once your pull request is ready for review, one
of the core maintainers of gurobi-logtools will review your pull request.

A pull request should contain tests for the changes made to the code behavior, should
include a clear message outlining the changes done, and should be linked to an existing
issue.

Before submitting a pull request:
- install the [pre-commit](https://pre-commit.com) package to enable the automatic
  running of the pre-commit hooks in the `.pre-commit-configuration.yaml` file,
- make sure all tests pass by running `make testnb` or `pytest` in the root folder of
  the `gurobi-logtools`.

After a pull request is submitted, the tests will be run automatically, and the status
will appear on the pull request page. If the tests failed, there is a link which can be
used to debug the failed tests.

## Code reviews
The pull request author should respond to all comments received. If the
comment has been accepted and appropriate changes applied, the author should respond by
a short message such as "Done" and then resolve the comment. If more discussion is
needed on a comment, it should remain open until a solution can be figured out.

## Merging changes

Explicit approval and passing tests are required before merging. The pull request author
should always merge via "Squash and Merge" and the remote pull request branch should be
deleted.
