@echo off
echo Fixing %1...
python __main__.py fix %1 --show-diff
pause
