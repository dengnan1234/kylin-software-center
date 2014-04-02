#!/usr/bin/python
# -*- coding: utf-8 -*-

### BEGIN LICENSE

# Copyright (C) 2013 National University of Defense Technology(NUDT) & Kylin Ltd

# Author:
#     Shine Huang<shenghuang@ubuntukylin.com>
# Maintainer:
#     Shine Huang<shenghuang@ubuntukylin.com>

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from backend.sourcelist import SourceList
from ui.confw import Ui_ConfigWidget
from models.enums import Signals


class ConfigWidget(QWidget):
    sourcelist = ''

    def __init__(self, parent=None):
        QWidget.__init__(self,parent)
        self.ui_init()

        self.sourcelist = SourceList()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.bg.lower()
        self.move(173, 138)

        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.All, QPalette.Base, brush)
        self.ui.pageListWidget.setPalette(palette)
        self.ui.sourceWidget.setPalette(palette)
        self.ui.sourceListWidget.setPalette(palette)

        self.ui.pageListWidget.setFocusPolicy(Qt.NoFocus)
        self.ui.sourceListWidget.setFocusPolicy(Qt.NoFocus)
        self.ui.btnUpdate.setFocusPolicy(Qt.NoFocus)
        self.ui.btnAdd.setFocusPolicy(Qt.NoFocus)
        self.ui.btnReset.setFocusPolicy(Qt.NoFocus)
        self.ui.btnClose.setFocusPolicy(Qt.NoFocus)
        self.ui.cbhideubuntu.setFocusPolicy(Qt.NoFocus)
        self.ui.btnCancel.setFocusPolicy(Qt.NoFocus)

        self.ui.btnClose.clicked.connect(self.hide)
        self.ui.btnUpdate.clicked.connect(self.slot_click_update)
        self.ui.btnAdd.clicked.connect(self.slot_click_add)
        self.ui.lesource.textChanged.connect(self.slot_le_input)
        self.ui.cbhideubuntu.stateChanged.connect(self.slot_checkstate_changed)
        self.ui.btnCancel.clicked.connect(self.slot_click_cancel)

        self.ui.text1.setText("软件源列表")
        self.ui.cbhideubuntu.setText("隐藏ubuntu源")
        self.ui.btnUpdate.setText("    更新软件源")
        self.ui.btnAdd.setText("    添加软件源")
        self.ui.btnReset.setText("恢复默认设置")
        self.ui.btnClose.setText("关闭")
        sourceitem = QListWidgetItem("软件源设置")
        sourceitem.setIcon(QIcon("res/source.png"))
        self.ui.pageListWidget.addItem(sourceitem)

        self.ui.bg.setStyleSheet("QLabel{background-image:url('res/configwidget.png');}")
        self.ui.text1.setStyleSheet("QLabel{color:#1E66A4;font-size:14px;}")
        self.ui.line1.setStyleSheet("QLabel{background-color:#E0E0E0;}")
        self.ui.pageListWidget.setStyleSheet("QListWidget{border:0px;}QListWidget::item{height:25px;padding-left:5px;margin-top:0px;border:0px;}QListWidget::item:selected{background-color:#6BB8DD;color:#E6F1F7;}")
        self.ui.sourceWidget.setStyleSheet("QListWidget{border:0px;}")
        self.ui.sourceListWidget.setStyleSheet("QListWidget{border:0px;}QListWidget::item{height:25px;margin-top:0px;margin-left:1px;border:0px;}QListWidget::item:selected{background-color:#E4F1F8;;}")
        self.ui.lesource.setStyleSheet("QLineEdit{border:1px solid #6BB8DD;border-radius:1px;color:#497FAB;font-size:13px;}")
        self.ui.btnUpdate.setStyleSheet("QPushButton{border:0px;color:#1E66A4;font-size:14px;background:url('res/btnupdate.png') no-repeat;}")
        self.ui.btnAdd.setStyleSheet("QPushButton{border:0px;color:gray;font-size:14px;background:url('res/btnadd.png') no-repeat;}")
        self.ui.btnReset.setStyleSheet("QPushButton{border:0px;color:gray;font-size:14px;}")
        self.ui.btnClose.setStyleSheet("QPushButton{border:0px;color:#1E66A4;font-size:14px;background:url('res/btn2-1.png');}QPushButton:hover{background:url('res/btn2-2.png');}QPushButton:pressed{background:url('res/btn2-3.png');}")
        self.ui.cbhideubuntu.setStyleSheet("QCheckBox{border:0px;color:#1E66A4;font-size:14px;}")
        self.ui.btnCancel.setStyleSheet("QPushButton{background-image:url('res/cancel.png');border:0px;}")
        self.ui.progressBar.setStyleSheet("QProgressBar{background-image:url('res/progressbg.png');border:0px;border-radius:0px;text-align:center;color:#1E66A4;}"
                                          "QProgressBar:chunk{background-image:url('res/progress2.png');}")
        self.ui.sourceListWidget.verticalScrollBar().setStyleSheet("QScrollBar:vertical{width:11px;background-color:black;margin:0px,0px,0px,0px;padding-top:0px;padding-bottom:0px;}"
                                                                 "QScrollBar:sub-page:vertical{background:qlineargradient(x1: 0.5, y1: 1, x2: 0.5, y2: 0, stop: 0 #D4DCE1, stop: 1 white);}QScrollBar:add-page:vertical{background:qlineargradient(x1: 0.5, y1: 0, x2: 0.5, y2: 1, stop: 0 #D4DCE1, stop: 1 white);}"
                                                                 "QScrollBar:handle:vertical{background:qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #CACACA, stop: 1 #818486);}QScrollBar:add-line:vertical{background-color:green;}")

        self.ui.pageListWidget.setItemSelected(self.ui.pageListWidget.item(0), True)
        self.ui.btnAdd.setEnabled(False)
        self.ui.btnReset.setEnabled(False)
        self.ui.cbhideubuntu.setChecked(True)
        self.set_process_visiable(False)

        self.ui.progressBar.setRange(0,100)
        self.ui.progressBar.reset()

        self.hide()

    def ui_init(self):
        self.ui = Ui_ConfigWidget()
        self.ui.setupUi(self)
        self.show()

    def fill_sourcelist(self):
        self.ui.sourceListWidget.clear()
        slist = ''
        if(self.ui.cbhideubuntu.isChecked()):
            slist = self.sourcelist.get_sources_except_ubuntu()
        else:
            slist = self.sourcelist.get_sources()
        for one in slist:
            item = QListWidgetItem()
            itemw = SourceItemWidget(one, self)
            self.ui.sourceListWidget.addItem(item)
            self.ui.sourceListWidget.setItemWidget(item, itemw)

    def set_process_visiable(self, flag):
        if(flag == True):
            self.ui.processwidget.setVisible(True)
            self.ui.btnUpdate.setVisible(False)
            self.ui.btnReset.setVisible(False)
            self.ui.cbhideubuntu.setVisible(False)
        else:
            self.ui.processwidget.setVisible(False)
            self.ui.btnUpdate.setVisible(True)
            self.ui.btnReset.setVisible(True)
            self.ui.cbhideubuntu.setVisible(True)

    def slot_click_cancel(self):
        self.emit(Signals.update_source_cancel)

    def slot_click_update(self):
        self.ui.progressBar.reset()
        self.set_process_visiable(True)
        self.emit(Signals.click_update_source)

    def slot_update_status_change(self, percent):
        self.ui.progressBar.setValue(percent)

    def slot_update_finish(self):
        self.set_process_visiable(False)

    def slot_click_add(self):
        sourcetext = str(self.ui.lesource.text().toUtf8())
        self.sourcelist.add_source(sourcetext)
        self.fill_sourcelist()

    def slot_le_input(self, text):
        sourcetext = str(text.toUtf8())
        if(sourcetext.strip() == ""):
            self.ui.btnAdd.setStyleSheet("QPushButton{border:0px;color:gray;font-size:14px;background:url('res/btnadd.png') no-repeat;}")
            self.ui.btnAdd.setEnabled(False)
        else:
            self.ui.btnAdd.setStyleSheet("QPushButton{border:0px;color:#1E66A4;font-size:14px;background:url('res/btnadd.png') no-repeat;}")
            self.ui.btnAdd.setEnabled(True)

    def slot_checkstate_changed(self):
        self.fill_sourcelist()


class SourceItemWidget(QWidget):
    confw = ''
    type = ''

    def __init__(self, source, parent=None):
        QWidget.__init__(self,parent)

        self.confw = parent
        self.resize(414, 25)

        self.sourcetype = QLabel(self)
        self.sourcetype.setGeometry(10, 4, 8, 17)
        self.sourcetext = QLabel(self)
        self.sourcetext.setGeometry(25, 4, 345, 17)
        self.btnremove = QPushButton(self)
        self.btnremove.setGeometry(377, 4, 18, 18)

        self.btnremove.clicked.connect(self.slot_remove_source)

        self.btnremove.setFocusPolicy(Qt.NoFocus)

        self.sourcetype.setStyleSheet("QLabel{font-size:13px;color:#1E66A4;}")
        self.sourcetext.setStyleSheet("QLabel{font-size:13px;color:#5E5B67;}")
        self.btnremove.setStyleSheet("QPushButton{border:0px;background-image:url('res/cancel.png');}")

        self.type = source.type
        typestr = ''
        if(source.type == "deb"):
            typestr = "D"
        if(source.type == "deb-src"):
            typestr = "S"
        self.sourcetype.setText(typestr)

        compstr = " "
        for comp in source.comps:
            compstr += comp
            compstr += " "
        compstr = compstr[:-1]
        text = str(source.uri) + " " + str(source.dist) + compstr
        self.sourcetext.setText(text)

    def slot_remove_source(self):
        source = str(self.type) + " " + str(self.sourcetext.text().toUtf8())
        self.confw.sourcelist.remove_source(source)
        self.confw.fill_sourcelist()


def main():
    import sys
    app = QApplication(sys.argv)

    QTextCodec.setCodecForTr(QTextCodec.codecForName("UTF-8"))
    QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF-8"))

    globalfont = QFont()
    globalfont.setFamily("文泉驿微米黑")
    app.setFont(globalfont)
    a = ConfigWidget()
    a.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()