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
  +--------------+-----------------------+----------+--------------------------------------------------------------------------+
  |     Type     |       Repository      |   Time   |                                 Details                                  |
  +--------------+-----------------------+----------+--------------------------------------------------------------------------+
  | Pull Request | fossasia/chat.susi.ai | 18:44:38 |                          Simplify login Dialog                           |
  | Pull Request | fossasia/chat.susi.ai | 11:27:35 | Fixes #1296: Resolve bug of settings menu item appearing on other routes |
  |    Issues    | fossasia/chat.susi.ai | 09:59:25 |   BUG: Settings option is available on some pages for logged out users   |
  | Pull Request | fossasia/chat.susi.ai | 00:11:11 |          Fixes 1288: User email should be visible on all routes          |
  +--------------+-----------------------+----------+--------------------------------------------------------------------------+
  anshumanv have made 4 public contribution(s) today.

  Starred today:
  +--------------------------------+------------+----------+
  |           Repository           |  Language  |   Time   |
  +--------------------------------+------------+----------+
  |     ZachSaucier/Just-Read      | JavaScript | 23:42:25 |
  |          reach/router          | JavaScript | 21:39:28 |
  | pburtchaell/react-notification | JavaScript | 21:38:14 |
  |       SevenOutman/Hubble       |    Vue     | 21:36:14 |
  |   KyleAMathews/typography.js   | JavaScript | 21:36:02 |
  |  aashutoshrathi/git-stalk-cli  |   Python   | 03:40:08 |
  |     eamodio/vscode-gitlens     | TypeScript | 00:19:13 |
  +--------------------------------+------------+----------+
  anshumanv have starred 7 repo(s) today.
```

## Limitations

Stalking too much might lead to "API Rate Limit Exceeded for your IP".


<p align="center"> Made from scratch by <a href="https://github.com/aashutoshrathi">Aashutosh Rathi</a> </p>
