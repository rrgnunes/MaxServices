set caminho=%~dp0
cd %caminho%

python.exe connection.py stop

python.exe connection.py remove

pause