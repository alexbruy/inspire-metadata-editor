# coding=utf-8
from builtins import object
from qgis.PyQt.QtCore import QDate, QDateTime
from qgis.PyQt.QtWidgets import QAbstractSpinBox

from EditorMetadadosMarswInforbiomares import CONSTANTS as cons

NULLDATE = QDate.fromString('1800-01-01', cons.DATE_FORMAT)
NULLDATETIME = QDateTime.fromString('1800-01-01 00:00:00', cons.DATE_TIME_FORMAT)


class NullQDateEditWrapper(object):
    """

    """

    def __init__(self, qdate_edit):
        self.qdate_edit = qdate_edit
        self.callable_results = []
        self.qdate_edit.setDisplayFormat(cons.DATE_FORMAT)
        self.qdate_edit.setMinimumDate(NULLDATE)
        self.qdate_edit.setSpecialValueText(u"Não Definido")
        self.qdate_edit.setDate(NULLDATE)
        self.qdate_edit.setCalendarPopup(True)
        self.qdate_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.qdate_edit.editingFinished.connect(self.correct_date)

    def correct_date(self):
        if self.qdate_edit.date() == NULLDATE:
            self.qdate_edit.setDate(QDate.currentDate())

    def __getattr__(self, attr):
        ret = getattr(self.qdate_edit, attr)
        if hasattr(ret, "__call__"):
            return self.FunctionWrapper(self, ret)
        return ret

    class FunctionWrapper(object):
        def __init__(self, parent, callable):
            self.parent = parent
            self.callable = callable

        def __call__(self, *args, **kwargs):
            ret = self.callable(*args, **kwargs)
            self.parent.callable_results.append(ret)
            return ret

    def clear(self):
        """
        Sets Date To Minimum date that represents None Date
        """
        self.qdate_edit.setDate(NULLDATE)

    def get_date(self):
        """

        :return: None if no date is defined otherwise return a QDate
        :rtype:QDate or None
        """
        if self.qdate_edit.date().toString(cons.DATE_FORMAT) == NULLDATE.toString(cons.DATE_FORMAT):
            return None
        else:
            return self.qdate_edit.date()

    def set_date(self, date):

        self.qdate_edit.setDate(date)

    def get_original(self):
        return self.qdate_edit

    def setDisabled(self, x):
        if x:
            self.clear()
        self.qdate_edit.setDisabled(x)

    def is_null_date(self):
        if self.qdate_edit.date() == NULLDATE:
            return True
        else:
            return False


class NullQDateTimeEditWrapper(object):
    """

    """

    def __init__(self, qdateTime_edit):
        self.qdateTime_edit = qdateTime_edit
        self.callable_results = []
        self.qdateTime_edit.setDisplayFormat(cons.DATE_TIME_FORMAT)
        self.qdateTime_edit.setMinimumDateTime(NULLDATETIME)
        self.qdateTime_edit.setSpecialValueText(u"Não Definido")
        self.qdateTime_edit.setDateTime(NULLDATETIME)
        self.qdateTime_edit.setCalendarPopup(True)
        self.qdateTime_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.qdateTime_edit.editingFinished.connect(self.correct_dateTime)

    def correct_dateTime(self):
        if self.qdateTime_edit.dateTime() == NULLDATETIME:
            self.qdateTime_edit.setDateTime(QDateTime.currentDateTime())

    def __getattr__(self, attr):
        ret = getattr(self.qdateTime_edit, attr)
        if hasattr(ret, "__call__"):
            return self.FunctionWrapper(self, ret)
        return ret

    class FunctionWrapper(object):
        def __init__(self, parent, callable):
            self.parent = parent
            self.callable = callable

        def __call__(self, *args, **kwargs):
            ret = self.callable(*args, **kwargs)
            self.parent.callable_results.append(ret)
            return ret

    def clear(self):
        """
        Sets DateTime To Minimum dateTime that represents None DateTime
        """
        self.qdateTime_edit.setDateTime(NULLDATETIME)

    def get_dateTime(self):
        """

        :return: None if no dateTime is defined otherwise return a QDatetime
        :rtype:QDate or None
        """
        if self.qdateTime_edit.dateTime().toString(cons.DATE_TIME_FORMAT) == NULLDATETIME.toString(cons.DATE_TIME_FORMAT):
            return None
        else:
            return self.qdateTime_edit.dateTime()

    def set_dateTime(self, dateTime):

        self.qdateTime_edit.setDateTime(dateTime)

    def get_original(self):
        return self.qdateTime_edit

    def setDisabled(self, x):
        if x:
            self.clear()
        self.qdateTime_edit.setDisabled(x)

    def is_null_date(self):
        if self.qdateTime_edit.dateTime() == NULLDATETIME:
            return True
        else:
            return False
