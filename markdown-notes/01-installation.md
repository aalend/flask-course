## Introduction

Flask is a small framework — small enough to be called a "micro-framework".
But "micro" does not mean Flask is limited, or that your app has to fit in a single file.
It means Flask keeps a small, unopinionated core and leaves the bigger decisions to you:
the database layer, form validation, authentication, and other high-level tasks are added through extensions only when you need them.

Flask was designed as an extensible framework from the ground up.
It ships a solid core with a few basic services, and extensions provide the rest.
Because you pick only the extensions you want, you end up with a lean stack that has no bloat and does exactly what your project needs.

Flask has two main dependencies:

- **Werkzeug** — provides routing, debugging, and the Web Server Gateway Interface (WSGI) subsystem.
- **Jinja2** — provides template support.

Both were originally created by **Armin Ronacher** (the creator of Flask) and are today maintained by the **Pallets** organization.

Flask has no native support for accessing databases, validating web forms, or authenticating users.
As a developer, you have the power to cherry-pick the extensions that work best for your project — or even write your own if you feel inclined to.

> [!NOTE]
> Modern Flask also pulls in a few smaller dependencies (`click`, `itsdangerous`, `markupsafe`, `blinker`).
> Since Flask 2.3, `blinker` is required as well — it powers Flask's **signals** (a mechanism for subscribing to in-app events such as `request_started` or `template_rendered`).
> Thinking of Werkzeug and Jinja2 as the "two main" ones is a fine mental model while learning.

### The cost of "micro"

Every design decision has a price. Flask's minimal core is no exception:

- **Benefit** — a lean stack with no bloat; you assemble exactly the pieces you need, the way you understand them.
- **Cost** — more decisions land on you. Frameworks like Django ship an ORM, auth, an admin panel, and forms out of the box; in Flask you choose, install, and wire each of those yourself. That means more setup and boilerplate, and — especially while learning — a higher risk of assembling an inconsistent or insecure stack if you pick the wrong extensions.

Freedom and responsibility are two sides of the same coin.

## Using Virtual Environments

The most convenient way to install Flask is to use a virtual environment.

A virtual environment (VE) is an **isolated Python environment with its own `site-packages` directory**.
Rather than fully copying the interpreter, a modern VE typically **links back to a base Python interpreter** while keeping its installed packages separate from the system — so the isolation happens at the **package level**, not as a full duplicate of Python. This is why a VE costs only a few KB instead of tens of MB.

Virtual environments are useful because they prevent package clutter and version conflicts in the system's Python interpreter.
Creating a VE for each application means:

- Each app has access to **only** the packages it actually uses.
- The global interpreter stays neat and clean.
- The global interpreter serves only as a source from which more VEs are created.

> [!NOTE]
> **Why isolation actually works.** Each VE has its **own** `site-packages` folder. App A can keep Flask 3.x in *its* `site-packages` while App B keeps Flask 2.x in *its own* — two physically separate directories that never touch. There is no shared location where their versions could collide.

> [!NOTE]
> **What actually lives inside `.venv`:**
> - `lib/.../site-packages/` — the installed packages for this project.
> - `pyvenv.cfg` — a small config file pointing back to the base Python interpreter.
> - `bin/` (`Scripts/` on Windows) — symlinks to `python` plus console-script wrappers (e.g. the `flask` command itself).

Traditionally, virtual environments are created with Python's built-in **`venv`** module (in the standard library since Python 3.3) or the third-party **`virtualenv`** utility.
In this course we use the **uv** package manager, created by Astral.

uv is a Rust-based tool that replaces several separate tools at once. Why we use it:

- **Replaces `pip`, `virtualenv`, and more** with a single tool.
- **10–100× faster** than pip.
- **Disk-space efficient** — a global cache deduplicates dependencies.

For everything else, check the docs on [their website](https://docs.astral.sh/uv/).

### Installation

> [!NOTE]
> This guide assumes Python is already installed.
> If it isn't, grab it from the official Python website and install it for your operating system.

> [!TIP]
> uv can install and manage Python for you, so a system Python isn't strictly required.

uv is easy to install — just follow the instructions on their website.
It installs everything we need to create our virtual environment.
On the install page you can pick macOS, Linux, or Windows:

- [uv installation instructions](https://docs.astral.sh/uv/#__tabbed_1_1)

After installing uv, every Python project lives in its own folder.
The `uv init <name>` command creates that folder **and** initializes the project in one step, so you don't need a separate `mkdir`:

```bash
uv init flask-course && cd flask-course
```

This gives us a Python project where we can start learning Flask — but first we need to install Flask itself:

```bash
uv add flask
```

With this command Flask is installed, recorded in `pyproject.toml`, and locked in `uv.lock`.

> [!NOTE]
> `uv add` will **create the `.venv` automatically** if one doesn't exist yet. There is no separate "make the venv" step — this is part of why the uv workflow is shorter than the classic `python -m venv .venv` → `activate` → `pip install` sequence.

We are now ready to start writing Flask applications.

> [!TIP]
> Use `uv run` to run anything inside the project's environment without activating it manually,
> for example: `uv run flask --app app run --debug`.

### `uv run` vs. manual activation

These two achieve a similar result through very different mechanisms:

- **Activation** (`source .venv/bin/activate`) **persistently** modifies your shell's `PATH` so that `python` points at the interpreter inside `.venv`. That state lasts until you close the terminal or run `deactivate`.
- **`uv run`** injects the environment's paths for **a single command only**, runs it, and leaves your shell untouched. It also checks that `.venv` matches `uv.lock` first, syncing if needed.

> [!TIP]
> Mental model: *activation* = flip your whole shell into the environment. *`uv run`* = execute one command **inside** the environment without changing your shell.

## `pyproject.toml` vs. `uv.lock`

`uv add flask` writes Flask into **both** files, but they serve different roles:

| File | Written by | Contains | Purpose |
|------|-----------|----------|---------|
| `pyproject.toml` | **You** (human-edited) | Your declared dependencies, often with loose constraints (e.g. `flask>=3.0`) | States your **intent** — *what* you want |
| `uv.lock` | **uv** (machine-generated) | Exact pinned versions of **everything**, including transitive deps (Werkzeug, Jinja2, click, blinker…) + hashes | Guarantees a **reproducible** install — everyone gets the identical set |

The reason there are two files: one captures *intent* (human, loose), the other captures *reproducible reality* (machine, exact).

> [!WARNING]
> Never hand-edit `uv.lock` — it is regenerated automatically. Edit `pyproject.toml`, then let uv update the lock.
