# clipboardtools

clipnotify from: https://github.com/cdown/clipnotify/tree/masterhttps://github.com/cdown/clipnotify/tree/master


search alias:
```bash
rg --no-heading --color=always . ~/.clipboard_history | fzf --ansi --delimiter : --preview 'bat --style=numbers --color=always $(echo {} | cut -d: -f1)' | cut -d: -f1 | xargs cat
```
