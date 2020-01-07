from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback, sys

from threadingHelpers import WorkerSignals, Worker, logger,setup_logs
from node import start

Ui_MainWindow, QtBaseClass = uic.loadUiType("QTDesigner.ui")


BUTTON_MAP = {
    'addBtn': 'addNewNodeFn',
    'connectBtn': 'connectWithNodeFn',
    'disconnectBtn': 'disconnectNodeFn',
    'discoveryBtn': 'startDiscoveryFn',
    'becomeServerBtn': 'becomeMainServerFn'
}

class MainWindow(Ui_MainWindow, QtBaseClass):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # super(QtBaseClass, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setupButtons()

        setup_logs(logger, self.debugArea)
        self.show()

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.recurring_timer)
        # self.timer.start()
    def printToScreen(self, msg):
        logger.info(msg)
        # self.debugArea.moveCursor(QTextCursor.End);
        # self.debugArea.appendPlainText(msg)    

    def setupButtons(self):
        [getattr(self, b).pressed.connect(getattr(self, fn)) for b,fn in BUTTON_MAP.items()]

    def progress_fn(self, n):
        print("%d%% done" % n)
 
    def print_output(self, s):
        print(s)
        
    def thread_complete(self):
        print("THREAD COMPLETE!")
 
    def becomeServer(self): pass
    def becomeClient(self): pass

 
    def addNewNodeFn(self, nodeId=None): 
        self.printToScreen(f'addNewNodeFn called')
    def connectWithNodeFn(self, nodeId=None): 
        self.printToScreen(f'connectWithNodeFn called')
    def disconnectNodeFn(self, nodeId=None): 
        self.printToScreen(f'disconnectNodeFn called')
    def startDiscoveryFn(self, nodeId=None): 
        self.printToScreen(f'startDiscoveryFn called')
        self.startOnNewThread(start)
    def becomeMainServerFn(self, nodeId=None): 
        self.printToScreen(f'becomeMainServerFn called')

    def startOnNewThread(self, fn):
        # Pass the function to execute
        worker = Worker(fn) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        
        # Execute
        self.threadpool.start(worker) 

    

app = QApplication([])
window = MainWindow()
app.exec_() 


# class MainWindow(QMainWindow):

#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
    
#         self.counter = 0
    
#         layout = QVBoxLayout()
        
#         self.l = QLabel("Start")
#         b = QPushButton("DANGER!")
#         b.pressed.connect(self.startOnNewThread)
    
#         layout.addWidget(self.l)
#         layout.addWidget(b)
    
#         w = QWidget()
#         w.setLayout(layout)
    
#         self.setCentralWidget(w)
    
#         self.show()

#         self.threadpool = QThreadPool()
#         print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

#         self.timer = QTimer()
#         self.timer.setInterval(1000)
#         self.timer.timeout.connect(self.recurring_timer)
#         self.timer.start()
    
#     def progress_fn(self, n):
#         print("%d%% done" % n)

#     def execute_this_fn(self, progress_callback):
#         for n in range(0, 5):
#             time.sleep(1)
#             progress_callback.emit(n*100/4)
            
#         return "Done."
 
#     def print_output(self, s):
#         print(s)
        
#     def thread_complete(self):
#         print("THREAD COMPLETE!")
 
#     def startOnNewThread(self):
#         # Pass the function to execute
#         worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
#         worker.signals.result.connect(self.print_output)
#         worker.signals.finished.connect(self.thread_complete)
#         worker.signals.progress.connect(self.progress_fn)
        
#         # Execute
#         self.threadpool.start(worker) 

        
#     def recurring_timer(self):
#         self.counter +=1
#         self.l.setText("Counter: %d" % self.counter)
    

# app = QApplication([])
# window = MainWindow()
# app.exec_() 

# import sys
# from PyQt5 import uic
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtWidgets import QApplication, QMessageBox
# from PyQt5.QtCore import QThread
# from PyQt5 import uic


# # Form, Window = uic.loadUiType("QTDesigner.ui")
# Ui_MainWindow, QtBaseClass = uic.loadUiType("QTDesigner.ui")


# class Gui(Ui_MainWindow, QtBaseClass):
#     def __init__(self, parent = None):
#         super(QtBaseClass, self).__init__(parent)
#         self.setupUi(self)
#         self.threading = ThreadClass()
 
 
# def main():
#     app = QApplication(sys.argv)
#     window = Gui()
#     window.show()
#     sys.exit(app.exec_())
 
 
# # if __name__ == "__main__":
#     # main()
#     #!/usr/bin/python3
# # Threading example with QThread and moveToThread (PyQt5)
# import sys
# import time
# from PyQt5 import QtWidgets, QtCore
 
# class WorkerThread(QtCore.QObject):
#     signal = QtCore.pyqtSignal(str, int)
 
#     def __init__(self):
#         super().__init__()
 
#     @QtCore.pyqtSlot()
#     def run(self):
#         while True:
#             print("hello Thread 1")
#             # Long running task ...
#             self.signal.emit("Leet 1", 333)
#             time.sleep(5)
 
# class WorkerThread2(QtCore.QObject):
#     signal = QtCore.pyqtSignal(str, int)
 
#     def __init__(self):
#         super().__init__()
 
#     @QtCore.pyqtSlot()
#     def run(self):
#         while True:
#             print("hello Thread 2")
#             # Long running task ...
#             self.signal.emit("Leet 2", 555)
#             time.sleep(5)

# class Main(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.worker = WorkerThread()
#         self.worker = WorkerThread()
#         self.workerThread = QtCore.QThread()
#         self.workerThread.started.connect(self.worker.run)  # Init worker run() at startup (optional)
#         self.worker.signal.connect(self.signalHandler)  # Connect your signals/slots
#         self.worker.moveToThread(self.workerThread)  # Move the Worker object to the Thread object
#         self.workerThread.start()
 
#     def signalHandler(self, text, number):
#         print(text)
#         print(number)
 
# if __name__== '__main__':
#     app = QtWidgets.QApplication([])
#     gui = Main()
#     sys.exit(app.exec_())