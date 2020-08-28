rmdir dist /s /q
rmdir build /s /q
del main.spec 

pyinstaller --noconsole -F -i "C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\welcome-logo.ico" main.py