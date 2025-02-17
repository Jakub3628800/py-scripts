# clipboardtools

https://github.com/cdown/clipnotify/tree/masterhttps://github.com/cdown/clipnotify/tree/master


search alias:
```bash
find ~/.clipboard_history -type f -mtime -30 -print0 | xargs -0 rg --no-heading --color=always . | sort -u | fzf --ansi --delimiter : --preview 'bat --style=numbers --color=always $(echo {} | cut -d: -f1)' | cut -d: -f1 | xargs cat
``
