# Agent Double-O Web

This agent is a smart agent that utilizes models that understands visuals, and perform tasks on a browser given tools related to Playwright APIs like finding elements, clicking, typing, etc.

## Install deps

```
uv sync
```

## How to run this agent?

1. launch an Edge browser (to have access to Default Work profile):

```
> "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --profile-directory=Default --remote-debugging-port=9222
```

or on Mac: 

```
$ msedge --profile-directory=Default --remote-debugging-port=9222
```

2. Run the `main.py`

```
$ uv run main.py
```