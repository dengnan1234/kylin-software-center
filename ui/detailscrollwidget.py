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


import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui.detailw import Ui_DetailWidget
from ui.starwidget import StarWidget
from ui.reviewwidget import ReviewWidget
from ui.listitemwidget import ListItemWidget
from ui.loadingdiv import *
from models.enums import UBUNTUKYLIN_RES_TMPICON_PATH, UBUNTUKYLIN_RES_SCREENSHOT_PATH, Signals

class DetailScrollWidget(QScrollArea):
    mainwindow = ''
    app = ''
    sshotcount = 0
    bigsshot = ''
    reviewpage = ''
    currentreviewready = ''

    def __init__(self, parent=None):
        QScrollArea.__init__(self,parent.ui.centralwidget)
        self.detailWidget = QWidget()
        self.ui_init()

        self.mainwindow = parent
        self.setGeometry(QRect(46, 113, 815, 479))
        self.setWidget(self.detailWidget)

        self.bigsshot = ScreenShotBig()

        self.ui.detailHeader.setAlignment(Qt.AlignCenter)
        self.ui.detailHeader.setText("详细信息")
        self.ui.detailHeader.lower()
        self.ui.btnCloseDetail.setText("返回")

        self.ui.btnCloseDetail.setFocusPolicy(Qt.NoFocus)
        self.ui.btnInstall.setFocusPolicy(Qt.NoFocus)
        self.ui.btnUpdate.setFocusPolicy(Qt.NoFocus)
        self.ui.btnUninstall.setFocusPolicy(Qt.NoFocus)
        self.ui.btnSshotBack.setFocusPolicy(Qt.NoFocus)
        self.ui.btnSshotNext.setFocusPolicy(Qt.NoFocus)
        self.ui.reviewListWidget.setFocusPolicy(Qt.NoFocus)
        self.ui.thumbnail.setFocusPolicy(Qt.NoFocus)
        self.ui.sshot.setFocusPolicy(Qt.NoFocus)
        self.ui.summary.setReadOnly(True)
        self.ui.description.setReadOnly(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.ui.btnCloseDetail.clicked.connect(self.slot_close_detail)
        self.ui.btnInstall.clicked.connect(self.slot_click_install)
        self.ui.btnUpdate.clicked.connect(self.slot_click_update)
        self.ui.btnUninstall.clicked.connect(self.slot_click_uninstall)
        self.ui.thumbnail.clicked.connect(self.slot_show_sshot)
        self.ui.sshot.clicked.connect(self.ui.sshot.hide)

        self.verticalScrollBar().valueChanged.connect(self.slot_scroll_end)

        # style
        self.detailWidget.setAutoFillBackground(True)
        palette = QPalette()
        palette.setColor(QPalette.Background, Qt.white)
        self.detailWidget.setPalette(palette)

        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.verticalScrollBar().setStyleSheet("QScrollBar:vertical{width:12px;background-color:black;margin:0px,0px,0px,0px;padding-top:0px;padding-bottom:0px;}"
                                               "QScrollBar:sub-page:vertical{background:qlineargradient(x1: 0.5, y1: 1, x2: 0.5, y2: 0, stop: 0 #D4DCE1, stop: 1 white);}QScrollBar:add-page:vertical{background:qlineargradient(x1: 0.5, y1: 0, x2: 0.5, y2: 1, stop: 0 #D4DCE1, stop: 1 white);}"
                                               "QScrollBar:handle:vertical{background:qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #CACACA, stop: 1 #818486);}QScrollBar:add-line:vertical{background-color:green;}")
        self.ui.name.setStyleSheet("QLabel{font-size:16px;font-weight:bold;}")
        self.ui.splitText1.setStyleSheet("QLabel{color:#1E66A4;font-size:16px;}")
        self.ui.splitText2.setStyleSheet("QLabel{color:#1E66A4;font-size:16px;}")
        self.ui.splitText3.setStyleSheet("QLabel{color:#1E66A4;font-size:16px;}")
        self.ui.splitLine1.setStyleSheet("QLabel{background-color:#E0E0E0;}")
        self.ui.splitLine2.setStyleSheet("QLabel{background-color:#E0E0E0;}")
        self.ui.splitLine3.setStyleSheet("QLabel{background-color:#E0E0E0;}")
        self.ui.detailHeader.setStyleSheet("QLabel{background-image:url('res/detailheadbg.png');color:black;font-size:14px;padding-top:17px;}")
        self.ui.btnCloseDetail.setStyleSheet("QPushButton{background-image:url('res/btn2-1.png');border:0px;color:#497FAB;}QPushButton:hover{background:url('res/btn2-2.png');}QPushButton:pressed{background:url('res/btn2-3.png');}")
        self.ui.candidateVersion.setStyleSheet("QLabel{color:#FF7D15;}")
        self.ui.gradeBG.setStyleSheet("QLabel{background-image:url('res/gradebg.png')}")
        self.ui.grade.setStyleSheet("QLabel{font-size:30px;color:#1E66A4;}")
        self.ui.gradeText2.setStyleSheet("QLabel{font-size:13px;}")
        self.ui.gradeText3.setStyleSheet("QLabel{font-size:13px;color:#9AA2AF;}")
        self.ui.summary.setStyleSheet("QTextEdit{border:0px;}")
        self.ui.description.setStyleSheet("QTextEdit{border:0px;}")
        self.ui.description.verticalScrollBar().setStyleSheet("QScrollBar:vertical{width:11px;background-color:black;margin:0px,0px,0px,0px;padding-top:0px;padding-bottom:0px;}"
                                                                 "QScrollBar:sub-page:vertical{background:qlineargradient(x1: 0.5, y1: 1, x2: 0.5, y2: 0, stop: 0 #D4DCE1, stop: 1 white);}QScrollBar:add-page:vertical{background:qlineargradient(x1: 0.5, y1: 0, x2: 0.5, y2: 1, stop: 0 #D4DCE1, stop: 1 white);}"
                                                                 "QScrollBar:handle:vertical{background:qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 #CACACA, stop: 1 #818486);}QScrollBar:add-line:vertical{background-color:green;}")
        self.ui.sshotBG.setStyleSheet("QLabel{background-image:url('res/sshotbg.png')}")
        self.ui.btnSshotBack.setStyleSheet("QPushButton{border:0px;background-image:url('res/btn-sshot-back-1.png')}QPushButton:hover{background-image:url('res/btn-sshot-back-2')}QPushButton:pressed{background-image:url('res/btn-sshot-back-3')}")
        self.ui.btnSshotNext.setStyleSheet("QPushButton{border:0px;background-image:url('res/btn-sshot-next-1.png')}QPushButton:hover{background-image:url('res/btn-sshot-next-2')}QPushButton:pressed{background-image:url('res/btn-sshot-next-3')}")
        self.ui.reviewListWidget.setStyleSheet("QListWidget{border:0px;}QListWidget::item{height:85px;margin-top:-1px;border:0px;}")

        self.ui.thumbnail.hide()

        self.hide()

        # mini loading div
        self.sshotload = MiniLoadingDiv(self.ui.sshotBG, self.detailWidget)
        self.reviewload = MiniLoadingDiv(self.ui.reviewListWidget, self.detailWidget)

    def ui_init(self):
        self.ui = Ui_DetailWidget()
        self.ui.setupUi(self.detailWidget)

    # fill fast property, show ui, request remote property
    def showSimple(self, app):
        # clear reviews
        self.reviewpage = 1
        self.currentreviewready = False
        self.ui.reviewListWidget.clear()
        self.detailWidget.resize(805, 790)
        self.ui.reviewListWidget.resize(805, 0)
        self.reviewload.move(self.ui.reviewListWidget.x(), self.ui.reviewListWidget.y())
        # clear sshot
        self.sshotcount = 0
        self.ui.thumbnail.hide()

        self.app = app
        self.ui.name.setText(app.name)
        self.ui.installedVersion.setText("当前版本: " + app.installed_version)
        self.ui.candidateVersion.setText("最新版本: " + app.candidate_version)
        self.ui.summary.setText(app.summary)
        self.ui.description.setText(app.description)

        if(os.path.isfile(UBUNTUKYLIN_RES_TMPICON_PATH + app.name + ".png")):
            self.ui.icon.setStyleSheet("QLabel{background-image:url('" + UBUNTUKYLIN_RES_TMPICON_PATH + app.name + ".png')}")
        elif(os.path.isfile(UBUNTUKYLIN_RES_TMPICON_PATH + app.name + ".jpg")):
            self.ui.icon.setStyleSheet("QLabel{background-image:url('" + UBUNTUKYLIN_RES_TMPICON_PATH + app.name + ".jpg')}")
        else:
            self.ui.icon.setStyleSheet("QLabel{background-image:url('" + UBUNTUKYLIN_RES_TMPICON_PATH + "default.png')}")

        size = app.packageSize
        sizek = size / 1024
        self.ui.size.setText("软件大小: " + str(sizek) + " K")

        self.ui.gradeText1.setText("我的评分: ")
        self.ui.gradeText2.setText("评分" + (str(app.ratings_total)) + "次")
        self.ui.commentNumber.setText("共 " + str(app.ratings_total) + " 条评论")
        self.ui.gradeText3.setText("满分5分")
        self.ui.grade.setText(str(app.ratings_average))
        self.star = StarWidget('big', app.ratings_average, self.detailWidget)
        self.star.move(500, 94)

        if(app.is_installed):
            self.ui.status.setStyleSheet("QLabel{background-image:url('res/installed.png')}")
            self.ui.status.show()

            if(app.is_upgradable):
                self.ui.btnInstall.setText("已安装")
                self.ui.btnUpdate.setText("可升级")
                self.ui.btnUninstall.setText("可卸载")
                self.ui.btnInstall.setEnabled(False)
                self.ui.btnUpdate.setEnabled(True)
                self.ui.btnUninstall.setEnabled(True)
                self.ui.btnInstall.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")
                self.ui.btnUpdate.setStyleSheet("QPushButton{background-image:url('res/btn4-1.png');border:0px;color:white;}QPushButton:hover{background:url('res/btn4-2.png');}QPushButton:pressed{background:url('res/btn4-3.png');}")
                self.ui.btnUninstall.setStyleSheet("QPushButton{background-image:url('res/btn5-1.png');border:0px;color:white;}QPushButton:hover{background:url('res/btn5-2.png');}QPushButton:pressed{background:url('res/btn5-3.png');}")
            else:
                self.ui.btnInstall.setText("已安装")
                self.ui.btnUpdate.setText("不可升级")
                self.ui.btnUninstall.setText("可卸载")
                self.ui.btnInstall.setEnabled(False)
                self.ui.btnUpdate.setEnabled(False)
                self.ui.btnUninstall.setEnabled(True)
                self.ui.btnInstall.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")
                self.ui.btnUpdate.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")
                self.ui.btnUninstall.setStyleSheet("QPushButton{background-image:url('res/btn5-1.png');border:0px;color:white;}QPushButton:hover{background:url('res/btn5-2.png');}QPushButton:pressed{background:url('res/btn5-3.png');}")
        else:
            # self.ui.status.setStyleSheet("QLabel{background-image:url('res/notinstall.png')}")
            self.ui.status.hide()

            self.ui.btnInstall.setText("安装")
            self.ui.btnUpdate.setText("不可升级")
            self.ui.btnUninstall.setText("不可卸载")
            self.ui.btnInstall.setEnabled(True)
            self.ui.btnUpdate.setEnabled(False)
            self.ui.btnUninstall.setEnabled(False)
            self.ui.btnInstall.setStyleSheet("QPushButton{background-image:url('res/btn3-1.png');border:0px;color:white;}QPushButton:hover{background:url('res/btn3-2.png');}QPushButton:pressed{background:url('res/btn3-3.png');}")
            self.ui.btnUpdate.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")
            self.ui.btnUninstall.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")

        self.show()

        # show loading
        self.sshotload.start_loading()
        self.reviewload.start_loading()
        # send request
        self.mainwindow.appmgr.get_application_reviews(app.name)
        self.mainwindow.appmgr.get_application_screenshots(app.name,UBUNTUKYLIN_RES_SCREENSHOT_PATH)

    def add_review(self, reviewlist):
        # print len(reviewlist)
        for review in reviewlist:
            # not this app's review  break
            if(review.package_name != self.app.name):
                break
            self.add_one_review(review)

        self.reviewpage += 1
        self.currentreviewready = True
        self.reviewload.stop_loading()

    def add_one_review(self, review):
        count = self.ui.reviewListWidget.count()
        reviewHeight = (count + 1) * 85
        self.detailWidget.resize(805, 790 + reviewHeight)
        self.ui.reviewListWidget.resize(805, reviewHeight)

        oneitem = QListWidgetItem()
        rliw = ReviewWidget(review)
        self.ui.reviewListWidget.addItem(oneitem)
        self.ui.reviewListWidget.setItemWidget(oneitem, rliw)

    def add_sshot(self, sclist):
        self.sshotcount = len(sclist)
        if(self.sshotcount > 0):
            img = QPixmap(self.app.thumbnailfile)
            self.ui.thumbnail.resize(img.width(), img.height())
            self.ui.thumbnail.setStyleSheet("QPushButton{background-image:url('" + self.app.thumbnailfile + "');border:0px;}")
            self.ui.thumbnail.move(400 - img.width() / 2, 521 - img.height() / 2)
            self.ui.thumbnail.show()
        if(self.sshotcount > 1):
            img = QPixmap(self.app.screenshotfile)
            self.bigsshot.resize(img.width(), img.height())
            self.bigsshot.bg.resize(img.width(), img.height())
            self.bigsshot.bg.setStyleSheet("QLabel{background-image:url('" + self.app.screenshotfile + "');}")

        self.sshotload.stop_loading()

    def slot_show_sshot(self):
        if(self.sshotcount > 1):
            self.bigsshot.move_to_center()
            self.bigsshot.show()

    def slot_close_detail(self):
        self.hide()

    def slot_click_install(self):
        self.emit(Signals.install_app, self.app)
        self.ui.btnInstall.setText("处理中")
        self.ui.btnInstall.setEnabled(False)

    def slot_click_update(self):
        self.emit(Signals.upgrade_app, self.app)
        self.ui.btnUpdate.setText("处理中")
        self.ui.btnUpdate.setEnabled(False)

    def slot_click_uninstall(self):
        self.emit(Signals.remove_app, self.app)
        self.ui.btnUninstall.setText("处理中")
        self.ui.btnUninstall.setEnabled(False)

    def slot_work_finished(self, newPackage):
        self.app.package = newPackage
        if(self.app.mark == "install" or self.app.mark == "update"):
            self.ui.status.show()
            self.ui.btnInstall.setText("已安装")
            self.ui.btnUpdate.setText("不可升级")
            self.ui.btnUninstall.setText("可卸载")
            self.ui.btnInstall.setEnabled(False)
            self.ui.btnUpdate.setEnabled(False)
            self.ui.btnUninstall.setEnabled(True)
            self.ui.btnInstall.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")
            self.ui.btnUpdate.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")
            self.ui.btnUninstall.setStyleSheet("QPushButton{background-image:url('res/btn5-1.png');border:0px;color:white;}QPushButton:hover{background:url('res/btn5-2.png');}QPushButton:pressed{background:url('res/btn5-3.png');}")
        elif(self.app.mark == "remove"):
            self.ui.status.hide()
            self.ui.btnInstall.setText("安装")
            self.ui.btnUpdate.setText("不可升级")
            self.ui.btnUninstall.setText("不可卸载")
            self.ui.btnInstall.setEnabled(True)
            self.ui.btnUpdate.setEnabled(False)
            self.ui.btnUninstall.setEnabled(False)
            self.ui.btnInstall.setStyleSheet("QPushButton{background-image:url('res/btn3-1.png');border:0px;color:white;}QPushButton:hover{background:url('res/btn3-2.png');}QPushButton:pressed{background:url('res/btn3-3.png');}")
            self.ui.btnUpdate.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")
            self.ui.btnUninstall.setStyleSheet("QPushButton{background-image:url('res/btn-notenable.png');border:0px;color:#9AA2AF;}")

    def slot_scroll_end(self, now):
        # current page not ready
        if(self.currentreviewready == False):
            pass
        else:
            max = self.verticalScrollBar().maximum()
            if(now == max):
                self.currentreviewready = False
                reviewcount = self.ui.reviewListWidget.count()
                self.reviewload.move(self.reviewload.x(), self.ui.reviewListWidget.y() + 84 * reviewcount)
                self.reviewload.start_loading()
                self.mainwindow.appmgr.get_application_reviews(self.app.name, page=self.reviewpage)

class ScreenShotBig(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.ToolTip)
        self.bg = QLabel(self)
        self.bg.move(0, 0)
        self.bg.installEventFilter(self)
        self.hide()

    def eventFilter(self, obj, event):
        if(obj == self.bg and event.type() == QEvent.MouseButtonRelease):
            self.hide()
        return True

    def move_to_center(self):
        windowWidth = QApplication.desktop().width()
        windowHeight = QApplication.desktop().height()
        self.move((windowWidth - self.width()) / 2, (windowHeight - self.height()) / 2)
