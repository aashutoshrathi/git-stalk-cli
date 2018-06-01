# git-stalk-cli


[![PyPI](https://img.shields.io/pypi/v/git-stalk.svg)](https://pypi.org/project/git-stalk/)
[![Build Status](https://travis-ci.com/aashutoshrathi/git-stalk-cli.svg?token=x5wHaKpXyy9apivkjrhr&branch=master)](https://travis-ci.com/aashutoshrathi/git-stalk-cli)

A command line interface for checking your/peer's activity today.


## Installation

```sh
 pip install git-stalk
```

## Using

```sh
$ stalk anshumanv
  Name: Anshuman Verma
  Company: @iiitv @fossasia
  Followers: 103
  Following: 154
  Public Repos: 72
  Contributions Today:
  +--------------+-----------------------+-----------------------------------------------------------------------+
  |     Type     |       Repository      |                                Details                                |
  +--------------+-----------------------+-----------------------------------------------------------------------+
  | Pull Request | fossasia/chat.susi.ai |         Fixes #1287: Do not show themes option on other routes        |
  |    Issues    | fossasia/chat.susi.ai | User email should be visible on all routes rather than the index page |
  |    Issues    | fossasia/chat.susi.ai |        Themes option should only be available on the chat page        |
  +--------------+-----------------------+-----------------------------------------------------------------------+
  anshumanv have made 3 public contribution(s) today.

  Starred today:
  +---------------------+----------+
  |      Repository     | Language |
  +---------------------+----------+
  | senorprogrammer/wtf |    Go    |
  +---------------------+----------+
  anshumanv have starred 1 repo(s) today.
```

## Limitations

Stalking too much might lead to "API Rate Limit Exceeded for your IP".


<p align="center"> Made from scratch by <a href="https://github.com/aashutoshrathi">Aashutosh Rathi</a> </p>
