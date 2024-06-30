from LogViewer import *


def main():
    
    LogView.logviewer.mainloop()


if __name__ == '__main__':
    main()

# pyinstaller --onefile --noconsole --icon=icon.ico main.py