@echo off
REM Setup script for custom git hooks on Windows

echo Setting up custom git hooks...

REM Configure git to use our custom hooks directory
git config core.hooksPath .githooks

echo.
echo Custom git hooks configured!
echo.
echo Branch protection status:

REM Check current setting in .env
set ALLOW_DIRECT_PUSH=true
if exist .env (
    for /f "tokens=1,2 delims==" %%a in ('findstr /r "^ALLOW_DIRECT_PUSH_TO_MAIN=" .env') do (
        set ALLOW_DIRECT_PUSH=%%b
    )
)

if "%ALLOW_DIRECT_PUSH%"=="true" (
    echo   Warning: Direct pushes to main: ALLOWED [development mode]
    echo   To enable protection: Set ALLOW_DIRECT_PUSH_TO_MAIN=false in .env
) else (
    echo   Success: Direct pushes to main: BLOCKED [protected mode]
    echo   To disable protection: Set ALLOW_DIRECT_PUSH_TO_MAIN=true in .env
)

echo.
echo Note: You still have pre-commit hooks for code quality.
pause