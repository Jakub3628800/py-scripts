# File mapper

Use to hot-reload tests from changed files. See Makefile for usage.

1. Download and make available in your path:
```bash
curl -o ~/.local/bin/file_mapper.py https://raw.githubusercontent.com/Jakub3628800/gists/master/file_mapper/file_mapper.py
chmod +x ~/.local/bin/file_mapper.py
```

2. Use with `entr` to hot-reload tests
```bash
find . -type f -name "*.py" | entr -p python file_mapper.py /_
```
