# Contributing

Welcome to `espec_pr3j` contributor's guide.

This document focuses on getting any potential contributor familiarized with
the development processes, but [other kinds of contributions] are also appreciated.

If you are new to using [git] or have never collaborated in a project previously,
please have a look at [contribution-guide.org]. Other resources are also
listed in the excellent [guide created by FreeCodeCamp] [^contrib1].

Please notice, all users and contributors are expected to be **open,
considerate, reasonable, and respectful**. When in doubt,
[Python Software Foundation's Code of Conduct] is a good reference in terms of
behavior guidelines.

## Issue Reports

If you experience bugs or general issues with `espec_pr3j`, please have a look
on the [issue tracker].
If you don't see anything useful there, please feel free to fire an issue report.

:::{tip}
Please don't forget to include the closed issues in your search.
Sometimes a solution was already reported, and the problem is considered
**solved**.
:::

New issue reports should include information about your programming environment
(e.g., operating system, Python version) and steps to reproduce the problem.
Please try also to simplify the reproduction steps to a very minimal example
that still illustrates the problem you are facing. By removing other factors,
you help us to identify the root cause of the issue.

## Documentation Improvements

You can help improve `espec_pr3j` docs by making them more readable and coherent, or
by adding missing information and correcting mistakes.

`espec_pr3j` documentation uses [Sphinx] as its main documentation compiler.
This means that the docs are kept in the same repository as the project code, and
that any documentation update is done in the same way was a code contribution.

When working on documentation changes in your local machine, you can
compile them using [uv] and [poethepoet]:

```
uv run poe docs
```

and use Python's built-in web server for a preview in your web browser
(`http://localhost:8000`):

```
python3 -m http.server --directory 'docs/_build/html'
```

## Code Contributions

Note that to open a pull request, you need a GitHub account and a fork of the repository.

### Submit an issue

Before you work on any non-trivial code contribution it's best to first create
a report in the [issue tracker] to start a discussion on the subject.
This often provides additional considerations and avoids unnecessary work.

### Create an environment

Before you start coding, install [uv] if you haven't already:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

[uv] manages the virtual environment and all dependencies automatically.

### Clone the repository

1. Clone this repository to your local disk:

   ```
   git clone git@github.com:leandrolanzieri/espec_pr3j.git
   cd espec_pr3j
   ```

2. Install all dependencies (including dev tools) with [uv]:

   ```
   uv sync
   ```

   This creates a virtual environment and installs the package in editable mode.

3. Install [pre-commit] hooks:

   ```
   uv run pre-commit install
   ```

   `espec_pr3j` comes with hooks configured to automatically help the
   developer to check the code being written.

### Implement your changes

1. Create a branch to hold your changes:

   ```
   git checkout -b my-feature
   ```

   and start making changes. Never work on the main branch!

2. Start your work on this branch. Don't forget to add [docstrings] to new
   functions, modules and classes, especially if they are part of public APIs.

3. Add yourself to the list of contributors in `AUTHORS.md`.

4. When you’re done editing, do:

   ```
   git add <MODIFIED FILES>
   git commit
   ```

   to record your changes in [git].

   Please make sure to see the validation messages from [pre-commit] and fix
   any eventual issues.
   This should automatically use [ruff] to check/fix the code style
   in a way that is compatible with the project.

   :::{important}
   Don't forget to add unit tests and documentation in case your
   contribution adds an additional feature and is not just a bugfix.

   Moreover, writing a [descriptive commit message] is highly recommended.
   In case of doubt, you can check the commit history with:

   ```
   git log --graph --decorate --pretty=oneline --abbrev-commit --all
   ```

   to look for recurring communication patterns.
   :::

5. Please check that your changes don't break any unit tests with:

   ```
   uv run poe test
   ```

   You can also run the linter and pre-commit checks with:

   ```
   uv run poe pre_commit
   ```

### Submit your contribution

1. If everything works fine, push your local branch to the remote server with:

   ```
   git push -u origin my-feature
   ```

2. Go to the web page of your fork on GitHub and click "Compare & pull request"
   to send your changes for review.
   Find more detailed information in [creating a pull request]. You might also want to open
   the pull request as a draft first and mark it as ready for review after the feedbacks
   from the continuous integration (CI) system or any required fixes.


### Troubleshooting

The following tips can be used when facing problems to build or test the
package:

1. Make sure to fetch all the tags from the upstream [repository].
   The command `git describe --abbrev=0 --tags` should return the version you
   are expecting. If you are trying to run CI scripts in a fork repository,
   make sure to push all the tags.

2. If dependencies are out of sync after pulling new changes, refresh the
   environment with:

   ```
   uv sync
   ```

3. [Pytest can drop you] in an interactive session in the case an error occurs.
   In order to do that you need to pass a `--pdb` option (for example by
   running `uv run pytest -k <NAME OF THE FAILING TEST> --pdb`).
   You can also setup breakpoints manually instead of using the `--pdb` option.

[^contrib1]: Even though, these resources focus on open source projects and
    communities, the general ideas behind collaborating with other developers
    to collectively create software are general and can be applied to all sorts
    of environments, including private companies and proprietary code bases.


[commonmark]: https://commonmark.org/
[contribution-guide.org]: http://www.contribution-guide.org/
[creating a pull request]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request
[descriptive commit message]: https://chris.beams.io/posts/git-commit
[docstrings]: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
[git]: https://git-scm.com
[guide created by freecodecamp]: https://github.com/freecodecamp/how-to-contribute-to-open-source
[other kinds of contributions]: https://opensource.guide/how-to-contribute
[poethepoet]: https://poethepoet.natn.io/
[pre-commit]: https://pre-commit.com/
[pypi]: https://pypi.org/
[pytest can drop you]: https://docs.pytest.org/en/stable/usage.html#dropping-to-pdb-python-debugger-at-the-start-of-a-test
[python software foundation's code of conduct]: https://www.python.org/psf/conduct/
[restructuredtext]: https://www.sphinx-doc.org/en/master/usage/restructuredtext/
[ruff]: https://docs.astral.sh/ruff/
[sphinx]: https://www.sphinx-doc.org/en/master/
[uv]: https://docs.astral.sh/uv/
[repository]: https://github.com/leandrolanzieri/espec_pr3j
[issue tracker]: https://github.com/leandrolanzieri/espec_pr3j/issues
