##### Every output string should be written in english
EG :
log.append(_("unknown bayer pattern"))

Use pygettext to generate .pot file :
pygettext -o als.pot als.py preprocess.py stack.py

##### Open xxx/locale/fr/LC_MESSAGES/als.po with poedit :
- import previously generated .pot file
- translate new strings


