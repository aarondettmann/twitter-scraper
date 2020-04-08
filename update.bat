:: Turn off command echoing feature
@echo off

WHERE git >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO ERROR: please install git... Exit.
    EXIT
)

:: Change into script directory
CD %root% >nul

ECHO INFO: updating twitter-scraper... & echo.
git pull
