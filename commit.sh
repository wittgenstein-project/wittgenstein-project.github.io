#!/bin/sh
set -u

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"
git add epub/
git add markdown/
git commit -am 'Auto-commit'; git push -u origin HEAD
