set caminho=%~dp0
cd %caminho%

python.exe connection.py install

sc config MaxSuport_BuscaPreco start=auto

python.exe connection.py start

pause