from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import traceback, sys
import logging


# Make this threadsafe
class QtHandler(logging.Handler):
    def __init__(self, output_widget: QTextEdit):
        logging.Handler.__init__(self)
        self.widget: QTextEdit = output_widget
        self.widget.setReadOnly(True)  

    def emit(self, record):
        try:
            msg = self.format(record)
            print(f"emiting: {msg}")
            self.widget.appendPlainText(msg)

        except:
            print("something bad happened")

def setup_logs(logger, output_widget=None):
    # to Gui
    qtLogHandler = QtHandler(output_widget)
    qtLogHandler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(qtLogHandler)

logger = logging.getLogger(__name__)
# to console
syslog = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s.%(msecs)03d %(threadName)10s] -- %(funcName)20s() -> %(levelname)5s: %(message)s',"%H:%M:%S")
syslog.setFormatter(formatter)
logger.addHandler(syslog)

logger.setLevel(logging.DEBUG)



# thanks https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress 

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        # self.kwargs['progress_callback'] = self.signals.progress        

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        
        # Retrieve args/kwargs here; and fire processing using them
        try:
            print(self.fn, self.args, self.kwargs)
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
        
