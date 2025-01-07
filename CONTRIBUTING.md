# Griptape Development Process

This document describes the development process for Griptape. It is intended for
anyone considering opening an **issue** or **pull request**. If in doubt,
please open a [discussion](https://github.com/orgs/griptape-ai/discussions);
we can always convert that to an issue later.

## Quick Guide

**I'd like to contribute!**

All issues are actionable. Pick one and start working on it.
If you need help or guidance, comment on the issue. Issues that are extra
friendly to new contributors are tagged with "good first issue".

**I have a bug!**

1. Search the issue tracker and discussions for similar issues.
2. If you don't have steps to reproduce, open a discussion.
3. If you have steps to reproduce, open an issue.

**I have an idea for a feature!**

1. Open a discussion.

**I've implemented a feature!**

1. If there is an issue for the feature, open a pull request.
2. If there is no issue, open a discussion and link to your branch.

**I have a question!**

1. Open a discussion or use Discord.

## General Patterns

### Issues are Actionable

The Griptape [issue tracker](https://github.com/griptape-ai/griptape/issues)
is for _actionable items_.

Unlike some other projects, Griptape **does not use the issue tracker for
discussion or feature requests**. Instead, we use GitHub
[discussions](https://github.com/orgs/griptape-ai/discussions) for that.
Once a discussion reaches a point where a well-understood, actionable
item is identified, it is moved to the issue tracker. **This pattern
makes it easier for maintainers or contributors to find issues to work on
since _every issue_ is ready to be worked on.**

If you are experiencing a bug and have clear steps to reproduce it, please
open an issue. If you are experiencing a bug but you are not sure how to
reproduce it or aren't sure if it's a bug, please open a discussion.
If you have an idea for a feature, please open a discussion.

### Pull Requests Implement an Issue

Pull requests should be associated with a previously accepted issue.
**If you open a pull request for something that wasn't previously discussed,**
it may be closed or remain stale for an indefinite period of time.


> [!NOTE]
>
> **Pull requests are NOT a place to discuss feature design.** Please do
> not open a WIP pull request to discuss a feature. Instead, use a discussion
> and link to your branch.

## Griptape Extensions

Griptape's extensibility allows anyone to develop and distribute functionality independently.
All new integrations, including Tools, Drivers, Tasks, etc., should initially be developed as extensions and then can be upstreamed into Griptape core if discussed and approved.

The [Griptape Extension Template](https://github.com/griptape-ai/griptape-extension-template) provides the recommended structure, step-by-step instructions, basic automation, and usage examples for new integrations.

## Dev Environment

Install all dependencies via Make:
```shell
make install
```

Run tests:
```shell
make test/unit
```

Run checks:
```shell
make check
```

Review [Makefile](https://github.com/griptape-ai/griptape/blob/main/Makefile) for more commands.
