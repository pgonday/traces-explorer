# traces-explorer
Dapp / Forge traces enhancer

# Usage

traces.py and pattern_* files should be in the same directory

```
> make test > traces.txt
> py traces.py traces.txt
```

It will generate an html file traces.txt.html with:
- token addresses replaced by token symbols
- function addresses replaced by function names
- contract addresses replaced by contract names

The nodes are expandables, at start only the error path is expanded.
