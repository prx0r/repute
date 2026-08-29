# Mech Client

[![PyPI](https://img.shields.io/pypi/v/mech-client)](https://pypi.org/project/mech-client/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mech-client)](https://pypi.org/project/mech-client/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/mech-client)](https://pypi.org/project/mech-client/)
[![License](https://img.shields.io/pypi/l/mech-client)](https://github.com/valory-xyz/mech-client/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/mech-client)](https://pypi.org/project/mech-client/)

[![Sanity checks and tests](https://github.com/valory-xyz/mech-client/actions/workflows/workflow.yml/badge.svg?branch=main)](https://github.com/valory-xyz/mech-client/actions/workflows/workflow.yml)
[![Coverage](https://img.shields.io/codecov/c/github/valory-xyz/mech-client)](https://codecov.io/gh/valory-xyz/mech-client)
[![flake8](https://img.shields.io/badge/lint-flake8-yellow)](https://flake8.pycqa.org)
[![mypy](https://img.shields.io/badge/static%20check-mypy-blue)](https://github.com/python/mypy)
[![Black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![bandit](https://img.shields.io/badge/security-bandit-lightgrey)](https://github.com/PyCQA/bandit)

A client to interact with Mechs - AI agents providing services - on the [Olas Marketplace](https://olas.network/mech-marketplace). It allows users to post requests for AI tasks on-chain, and get their result delivered.

## Requirements

- Python >=3.10, <3.12 (Python 3.10 or 3.11)

## Developing, running and deploying Mechs and Mech tools

The easiest way to create, run, deploy and test your own Mech and Mech tools is to follow the Mech and Mech tool docs [here](https://stack.olas.network/mech-tools-dev/). The [Mech tools dev repo](https://github.com/valory-xyz/mech-tools-dev) used in those docs greatly simplifies the development flow and dev experience.

Only continue reading this README if you know what you are doing and you are specifically interested in this repo.

## Quickstart Guide
For a fast and straightforward setup, follow the instructions provided on the website [here](https://build.olas.network/hire). 
This guide will walk you through the essential steps to get up and running without requiring an in-depth understanding of the system.

## Installation

Find the latest available release on [PyPi](https://pypi.org/project/mech-client/).

We recommend that you create a virtual Python environment using [uv](https://docs.astral.sh/uv/). Set up your virtual environment as follows:

```bash
uv init my_project
cd my_project
uv add mech-client
```

Alternatively, you can also install the Mech Client in your local Python installation:

```bash
pip install mech-client
```

If you require to use the Mech Client programmatically, please see [this section](#programmatic-usage) below.

## CLI Usage

Display the available options:

```bash
mechx --help
```

```bash
Usage: mechx [OPTIONS] COMMAND [ARGS]...

  Command-line tool for interacting with AI Mechs on-chain.

  Mech Client enables you to send AI task requests to on-chain AI agents
  (mechs) via the Olas (Mech) Marketplace. Supports multiple payment methods,
  tool discovery, and both agent mode (Safe multisig) and client mode (EOA).

Options:
  --version      Show the version and exit.
  --client-mode  Enables client mode (EOA-based). Default is agent mode (Safe-
                 based).
  --help         Show this message and exit.

Commands:
  deposit       Manage prepaid balance deposits.
  ipfs          IPFS utility operations.
  mech          Manage and query AI mechs on the marketplace.
  request       Send an AI task request to a mech on-chain.
  setup         Setup agent mode for on-chain interactions via Safe...
  subscription  Manage Nevermined (NVM) subscriptions.
  tool          Manage and query mech tools.

```

## Mech Marketplace

Learn more about mech marketplace [here](https://olas.network/mech-marketplace)

### Supported Chains

**Supported chains:** `gnosis`, `base`, `polygon`, `optimism`

All commands require `--chain-config` with one of these four chain names.

| Chain | Marketplace | Agent Mode | Native Payment | NVM Subscriptions | OLAS Payments | USDC Payments |
|-------|-------------|------------|----------------|-------------------|---------------|---------------|
| Gnosis | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Base | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Polygon | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Optimism | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |

**Notes:**
- **Marketplace**: Chains with marketplace contracts deployed. All supported chains have marketplace support.
- **Agent Mode**: All supported chains support on-chain agent registration via `setup`.
- **Native Payment**: Chains that support `deposit native` command for prepaid native token deposits.
- **NVM Subscriptions**: Chains that support `subscription purchase` command for Nevermined subscription-based payments (Gnosis, Base only).
- **OLAS/USDC Payments**: Chains that support `deposit toke