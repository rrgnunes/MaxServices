@echo off
setlocal

set caminho_server=%~dp0

set NSSMPath=%caminho_server%nssm.exe
set PythonPath=%userprofile%\AppData\Local\Programs\Python\Python311\python.exe
set ScriptPath=%caminho_server%scheduler.py
set LogDir=%caminho_server%log
set LogFile=%LogDir%\instalador.log

:: Verificar se o NSSM existe
if not exist "%NSSMPath%" (
    echo NSSM nao encontrado em %NSSMPath%.
    pause
    exit /b
)

:: Verificar se o Python existe
if not exist "%PythonPath%" (
    echo Python nao encontrado em %PythonPath%.
    pause
    exit /b
)

:: Verificar se o script existe
if not exist "%ScriptPath%" (
    echo Script nao encontrado em %ScriptPath%.
    pause
    exit /b
)

:: Verificar se o diretório de log existe, caso contrário, criar
if not exist "%LogDir%" (
    mkdir "%LogDir%"
)

:: Instalar e configurar o serviço
"%NSSMPath%" install MaxServices "%PythonPath%" "%ScriptPath%"
"%NSSMPath%" set MaxServices DisplayName "MaxServices"
"%NSSMPath%" set MaxServices Description "Analise de dados MaxSuport"
"%NSSMPath%" set MaxServices Start SERVICE_AUTO_START
"%NSSMPath%" set MaxServices AppExit Default Restart
"%NSSMPath%" set MaxServices AppRestartDelay 10
"%NSSMPath%" set MaxServices AppStdout "%LogFile%"
"%NSSMPath%" set MaxServices AppStderr "%LogFile%"
"%NSSMPath%" set MaxServices AppRotateFiles 0
"%NSSMPath%" start MaxServices

echo Servico MaxServices configurado e iniciado com sucesso.
pause
endlocal
