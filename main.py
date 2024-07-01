from LogViewer import *

def main():
    
    LogView.logviewer.mainloop()


if __name__ == '__main__':
    main()

# pyinstall build command
# pyinstaller --onefile --noconsole --icon=icon.ico main.py
# or
# pyinstaller --onefile --noconsole --icon=icon.ico main.spec
