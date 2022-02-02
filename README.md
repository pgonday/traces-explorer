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

# TODO

Add expand/collapse for tree with only the error path expanded
