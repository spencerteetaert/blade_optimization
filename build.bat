rmdir dist /s /q
rmdir build /s /q
del main.spec 
pyinstaller --noconsole -F -i "source\welcome-logo.ico" --add-data "source\welcome-logo.png;source" main.py