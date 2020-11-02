@rem Run a unit test for a particular sample file
@setlocal

cd samples
@set key=%1
@set z=C:\Progra~1\7-Zip\7z.exe
del %key%.zip
python ../src/main.py %key%.qq
if errorlevel 1 exit /B %ERRORLEVEL%
cd out
rmdir /S /Q %key%
mkdir %key%
cd %key%
%z% x ..\..\%key%.zip
cd ..
cd ..
cd ..

@endlocal
