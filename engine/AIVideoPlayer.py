from threading import Thread


runserver = lambda: exec(open("AIVideoPlayerBackend.py").read(), globals())

def start_browser():
    print('worked !!!')

# class MainWindow(QMainWindow):
#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#
#         self.show()
#         self.setWindowTitle("AIVideo Player")
#         self.setWindowIcon(QIcon(".png"))
#         self.browser = QWebView()
#
#         self.browser.setUrl(QUrl("http://127.0.0.1:5000/"))
#         self.setCentralWidget(self.browser)
#
# app =   QApplication()
# window = MainWindow()
# app.exec_()

Thread(target=runserver).start()
Thread(target=start_browser).start()