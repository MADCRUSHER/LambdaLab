@echo off
setlocal
cd /d %~dp0
where sam >nul 2>nul
if errorlevel 1 (
  echo AWS SAM CLI was not found. Install AWS SAM CLI first.
  echo https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
  pause
  exit /b 1
)
call sam build
if errorlevel 1 goto fail
call sam deploy --guided
if errorlevel 1 goto fail
echo.
echo Deployment complete. Copy the ApiUrl output into frontend config.js.
pause
exit /b 0
:fail
echo Deployment failed. Read the error above.
pause
