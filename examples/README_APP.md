# Example App

A tiny local-first task tracker generated through Kodex write mode.

## Commands

```bash
tasker add "write SPEC"
tasker list
tasker done 1
```

## Safety

This app is generated through a guarded write pipeline:

```txt
spec → context → provider → write plan → approval → tests → diff guard
```
