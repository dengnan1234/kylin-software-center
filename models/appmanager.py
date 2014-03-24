#!/usr/bin/python
# -*- coding: utf-8 -*-

### BEGIN LICENSE

# Copyright (C) 2013 National University of Defense Technology(NUDT) & Kylin Ltd

# Author:
#     maclin <majun@ubuntukylin.com>
#     Shine Huang<shenghuang@ubuntukylin.com>  
# Maintainer:
#     maclin <majun@ubuntukylin.com>

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

import apt
import locale
import os
import time
import logging

from PyQt4.QtCore import *

from category import Category
from application import Application
from advertisement import Advertisement
from backend.reviewratingspawn import SpawnProcess,Review,RatingSortMethods,ReviewRatingStat
from database import Database

from enums import (UBUNTUKYLIN_RES_PATH,UBUNTUKYLIN_DATA_PATH,UBUNTUKYLIN_DATA_CAT_PATH,UBUNTUKYLIN_RES_SCREENSHOT_PATH)
from enums import Signals,UnicodeToAscii,CheckChineseWords,CheckChineseWordsForUnicode

import threading
import multiprocessing
import Queue

from operator import itemgetter

LOG = logging.getLogger("uksc")

class WorkerItem:
     def __init__(self, funcname, kwargs):
        self.funcname = funcname
        self.kwargs = kwargs


class ThreadWorkerDaemon(threading.Thread):

    def __init__(self, appmgr):
        threading.Thread.__init__(self)
        self.appmgr = appmgr

    def run(self):
        while True:
            worklen = len(self.appmgr.worklist)
            if worklen == 0:
                time.sleep(1)
                continue

            self.appmgr.mutex.acquire()
            item = self.appmgr.worklist.pop()
            self.appmgr.mutex.release()

            if item is None:
                continue

            reslist = []
            if item.funcname == "update_models":
                self.appmgr._update_models()
            elif item.funcname == "init_models":
                self.appmgr._init_models()
            else:
                event = multiprocessing.Event()
                queue = multiprocessing.Queue()
                spawn_helper = SpawnProcess(item.funcname,item.kwargs, event, queue)
                spawn_helper.daemon = True
                spawn_helper.start()
                event.wait()

                resLen = queue.qsize()
                while resLen:
                    try:
                        count  = 0
#                        print "@@@@@@@@@:",queue.qsize(),item
                        while queue.qsize():
             #               print "@@enter while"
                            resitem = queue.get_nowait()
             #               print "@@after get no wait"
                            reslist.append(resitem)
#                            print "&&&&&&get an item:",count,resitem
                            count += 1
                        #queue.close()
                    except Queue.Empty:
#                        print "&&&&&&&&&&get error:",queue.qsize()
                        count  += 1

                    resLen = queue.qsize()
                print "receive data from backend process, func, qlen, len=",item.funcname,queue.qsize(),len(reslist)
            LOG.debug("receive data from backend process, len=%d",len(reslist))
            self.appmgr.dispatchWorkerResult(item,reslist)

#This class is the abstraction of application management
class AppManager(QObject):

    #
    def __init__(self):
        #super(AppManager, self).__init__()
        QObject.__init__(self)
        self.name = "Ubuntu Kylin Software Center"
        self.apt_cache = None
        self.cat_list = {}
        self.rnrStatList = {}
        self.language = 'zh_CN'      #'any' for all
        self.distroseries = 'any'  #'any' for all
        self.db = Database()

        self.worklist = []
        self.mutex = threading.RLock()
        self.worker_thread = ThreadWorkerDaemon(self)
        self.worker_thread.setDaemon(True)
        self.worker_thread.start()

    #open the apt cache and get the package count
    def open_cache(self):
        locale.setlocale(locale.LC_ALL, "zh_CN.UTF-8")
        if not self.apt_cache:
            self.apt_cache = apt.Cache()
        self.apt_cache.open()
        self.pkgcount = len(self.apt_cache)

    def _init_models(self):
        self.open_cache()

        #self.cat_list = self.download_category_list()
        self.cat_list = self.get_category_list_from_db()
#        print "&&&&&&&&&&&:\n",self.cat_list

        self.emit(Signals.init_models_ready,"ok","获取分类信息完成")

    def _init_toprated(self,reslist):
        #init db rank
        self.db.init_toprated_table(reslist)

    def init_models(self):

        self._init_models()
        return #????

        item  = WorkerItem("init_models",None)
        self.mutex.acquire()
        self.worklist.append(item)
        self.mutex.release()

    def _update_models(self):
        self.open_cache()

        for cname,citem in self.cat_list.iteritems():
            apps = citem.apps
            for aname,app in apps.iteritems():
                app.update_cache(self.apt_cache)

    def update_models(self,action,pkgname=""):
        kwargs = {"packagename": pkgname,
                  "action": action,
                  }

        item  = WorkerItem("update_models",kwargs)
        self.mutex.acquire()
        self.worklist.append(item)
        self.mutex.release()

    def get_category_list_from_db(self):
        list = self.db.query_categories()
        cat_list = {}
        for item in list:
#            print "categories:",item,item[0],item[1]
            c = UnicodeToAscii(item[0])
            zhcnc = item[1]
            index = item[2]
            visible = (item[3]==1)
#            print "trans:",c, zhcnc

            icon = UBUNTUKYLIN_RES_PATH + c + ".png"
            cat = Category(c, zhcnc, index, visible, icon, self.get_category_apps_from_db(c))
            cat_list[c] = cat

        return cat_list

    def download_category_list(self,catdir=""):
        #first load the categories from directory
        if not catdir:
            catdir = UBUNTUKYLIN_DATA_CAT_PATH

        cat_list = {}
        index = 0
        for c in os.listdir(catdir):
            visible = True
            zhcnc = ''
            if(c == 'ubuntukylin'):
                zhcnc = 'Ubuntu Kylin'
                index = 0
            if(c == 'necessary'):
                zhcnc = '装机必备'
                index = 1
            if(c == 'office'):
                zhcnc = '办公软件'
                index = 2
            if(c == 'devel'):
                zhcnc = '编程开发'
                index = 3
            if(c == 'graphic'):
                zhcnc = '图形图像'
                index = 4
            if(c == 'multimedia'):
                zhcnc = '影音播放'
                index = 5
            if(c == 'internet'):
                zhcnc = '网络工具'
                index = 6
            if(c == 'game'):
                zhcnc = '游戏娱乐'
                index = 7
            if(c == 'profession'):
                zhcnc = '专业软件'
                index = 8
            if(c == 'other'):
                zhcnc = '其他软件'
                index = 9
            if(c == 'recommend'):
                zhcnc = '热门推荐'
                index = 10
                visible = False
            if(c == 'toprated'):
                zhcnc = '排行榜'
                index = 11
                visible = False

            icon = UBUNTUKYLIN_RES_PATH + c + ".png"
            cat = Category(c, zhcnc, index, visible, icon, self.download_category_apps(c,catdir))
            cat_list[c] = cat

        #self.cat_list = cat_list
        return cat_list

    #get category list
    def get_category_list(self, reload=False, catdir=""):
        if reload is False:
            return self.cat_list

        #cat_list = self.download_category_list(catdir)
        cat_list = self.get_category_list_from_db()

        return cat_list

    def get_category_apps_from_db(self,cat,catdir=""):
        list = self.db.query_category_apps(cat)
        apps = {}
        for item in list:
            pkgname = UnicodeToAscii(item[0])
            displayname = item[1]
#            print "get_category_apps_from_db:",pkgname
            app = Application(pkgname,displayname, cat, self.apt_cache)
            if app.package:
                apps[pkgname] = app

                #if there has special information in db, get them
                #get_category_apps_from_db: 0 0
                #display_name, summary, description, rating_average,rating_total,review_total,download_total
                appinfo = self.db.query_application(pkgname)
                summary = appinfo[1]
                description = appinfo[2]
                rating_average = appinfo[3]
                rating_total = appinfo[4]
                review_total = appinfo[5]
                rank = appinfo[6]

#                if CheckChineseWords(app.summary) is False and CheckChineseWordsForUnicode(summary) is True:
                if summary is not None:
                    app.summary = summary
#                if CheckChineseWords(app.description) is False and CheckChineseWordsForUnicode(description) is True:
                if description is not None:
                    app.description = description
                if rating_average is not None:
                    app.ratings_average = float(rating_average)
                if rating_total is not None:
                    app.ratings_total = int(rating_total)
                if review_total is not None:
                    app.review_total = int(review_total)
                if rank is not None:
                    app.rank = int(rank)
        return apps

    def download_category_apps(self,cat,catdir=""):
        #load the apps from category file
        count = 0
        sumapp = 0
        apps = {}
        file = open(catdir + cat, 'r')
        for line in file:
            pkgname = line.strip('\n')
            app = Application(pkgname,cat, self.apt_cache)
            if app.package:
                apps[pkgname] = app
                sumapp = sumapp + 1
            else:
                count = count + 1
        return apps

    #get app list for a category
    def get_category_apps(self, cat, load=False, catdir=""):
        apps = {}
        if not cat:
            for catName,catItem in self.cat_list.iteritems():
                if len(apps) == 0:
                    apps = dict(catItem.apps.items())
                else:
                    apps = dict(apps.items() + catItem.apps.items())
        else:
            #get the apps from category list
            if not load:
                if not self.cat_list[cat]:
                    apps = []
                else:
                    apps = self.cat_list[cat].apps
            else:
                apps = self.download_category_apps(cat,catdir)

        return apps

    #get category list
    def get_category_byname(self, cat):
        return self.cat_list[cat]

    #get application object by appname
    def get_application_by_name(self,pkgname):
        #print "get_application_by_name:", pkgname
        if not pkgname:
            return None
        if self.cat_list is None:
            return None
        #
        for (catname, cat) in self.cat_list.iteritems():
            app = cat.get_application_byname(pkgname)
            if app is not None:
                return app

        return None

    def get_application_count(self,cat_name=""):
        sum_inst = 0
        sum_up = 0
        sum_all = 0

        if len(cat_name)>0:
            cat = self.cat_list[cat_name]
            (sum_inst,sum_up, sum_all) = cat.get_application_count()
        else:
            for (catname, cat) in self.cat_list.iteritems():
                (inst,up, all) = cat.get_application_count()
                sum_inst = sum_inst + inst
                sum_up = sum_up + up
                sum_all = sum_all + all

        return (sum_inst,sum_up, sum_all)

    def get_application_rnrstat(self,pkgname):
        if self.rnrStatList is None:
            return None
        rnrStat = None
        try:
            rnrStat = self.rnrStatList[pkgname]
        except:
            rnrStat = None
        return rnrStat

    #get recommend apps, this is now implemented with local config file
    def get_recommend_apps(self):
        print "we need to get the applications by condition recommend"
        applist = []
        apps = self.get_category_apps("recommend")
        if(apps is not None):
            for appname,app in apps.iteritems():
                applist.append(app)

        self.emit(Signals.recommend_ready,applist)

    #get advertisements, this is now implemented locally
    def get_advertisements(self):
        print "we need to get the advertisements"
        tmpads = []
        tmpads.append(Advertisement("qq", "url", "ad1.png", "http://www.ubuntukylin.com/ukylin/forum.php?mod=viewthread&tid=7688&extra=page%3D1"))
        tmpads.append(Advertisement("wps", "pkg", "ad2.png", "wps-office"))
        tmpads.append(Advertisement("dota2", "url", "ad3.png", "http://www.ubuntukylin.com/ukylin/forum.php?mod=viewthread&tid=7687&extra=page%3D1"))
        tmpads.append(Advertisement("pps", "url", "ad4.png", "http://dl.pps.tv/pps_linux_download.html"))
        self.emit(Signals.ads_ready,tmpads)

    #get apps in ubuntukylin archives, this is now implemented with config file
    #then we can sync with the archive
    def get_ubuntukylin_apps(self):
        print "we need to get the applications by condition recommend"
        return self.get_category_apps("ubuntukylin")

    #get toprated apps
    def get_toprated_stats_from_db(self, topcount=10, callback=None):
        print "We need to get the top 10 applications"
        list = self.db.query_app_toprated()
        rnrStatList = []
        for item in list:
            pkgname = UnicodeToAscii(item[0])

            rnrStat = ReviewRatingStat(pkgname)
            rnrStat.ratings_average = item[1]
            rnrStat.ratings_total = item[2]
            rnrStat.reviews_total = 0
            rnrStat.useful = 0

            rnrStatList.append(rnrStat)

        return rnrStatList


    #get toprated apps
    def get_toprated_stats(self, topcount=100, callback=None):
        print "We need to get the top 10 applications"

        rnrStatList = self.get_toprated_stats_from_db(topcount,callback)
        if(rnrStatList) >= 10:
            self.emit(Signals.toprated_ready,rnrStatList)
            return

        kwargs = {"topcount": topcount,
                  "sortingMethod": RatingSortMethods.INTEGRATE,
                  }

        item  = WorkerItem("get_toprated_stats",kwargs)
        self.mutex.acquire()
        self.worklist.append(item)
        self.mutex.release()

        return []

    #get rating and review status
    def get_rating_review_stats(self,callback=None):
        print "we need to get the ratings and reviews stat"
        item  = WorkerItem("get_rating_review_stats",None)
        self.mutex.acquire()
        self.worklist.append(item)
        self.mutex.release()

        return []

    #get reviews for a package
    def get_application_reviews(self,pkgname,page=1,callback=None):
        kwargs = {"language": self.language,
                  "distroseries": self.distroseries,
                  "packagename": pkgname, #multiarch..
                  "page": int(page),
                  }

        item  = WorkerItem("get_reviews",kwargs)

        app = self.get_application_by_name(pkgname)
        reviews = app.get_reviews(page)
        if reviews is not None:
            print "get_application_reviews:directly get"
            self.dispatchWorkerResult(item,reviews)
            return reviews

        self.mutex.acquire()
        self.worklist.append(item)
        self.mutex.release()

    #get screenshots
    def get_application_screenshots(self,pkgname, cachedir=UBUNTUKYLIN_RES_SCREENSHOT_PATH, callback=None):
        LOG.debug("request to get screenshots:%s",pkgname)
        app = self.get_application_by_name(pkgname)
        if app is None:
            return False

        kwargs = {"packagename": pkgname,
                  "thumbnail":app.thumbnail,
                  "screenshot":app.screenshot,
                  "thumbnailfile":app.thumbnailfile,
                  "screenshotfile":app.screenshotfile,
                  "version": app.version,
                  "cachedir": cachedir, #result directory
                  }

        item  = WorkerItem("get_screenshots",kwargs)

        if app.screenshots:
            self.dispatchWorkerResult(item,app.screenshots)
            return app.screenshots

        self.mutex.acquire()
        self.worklist.append(item)
        self.mutex.release()

        return []

    def dispatchWorkerResult(self,item,reslist):
        if item.funcname == "get_reviews":
            # convert into our review objects
            LOG.debug("reviews ready:%s",len(reslist))
            reviews = reslist
            page = item.kwargs['page']

            app = self.get_application_by_name(item.kwargs['packagename'])
            app.add_reviews(page,reviews)

            self.emit(Signals.app_reviews_ready,reviews)
        elif item.funcname == "get_screenshots":
            LOG.debug("screenshots ready:%s",len(reslist))
            screenshots = reslist
            app = self.get_application_by_name(item.kwargs['packagename'])
            app.screenshots = screenshots

            self.emit(Signals.app_screenshots_ready,screenshots)
        elif item.funcname == "get_rating_review_stats":
            LOG.debug("rating review stats ready:%d",len(reslist))
            rnrStats = reslist
            self.rnrStatList = reslist


            for rnrStat in rnrStats:
                app = self.get_application_by_name(str(rnrStat.pkgname))
                if app is not None:
                    app.ratings_average = rnrStat.ratings_average
                    app.ratings_total = rnrStat.ratings_total
                if(str(rnrStat.pkgname) == "gparted"):
                    print "######gparted ....", rnrStat.ratings_average,rnrStat.ratings_total, app


            self.emit(Signals.rating_reviews_ready,rnrStats)
        elif item.funcname == "get_toprated_stats":
            LOG.debug("toprated stats ready:%d",len(reslist))
            topRated = reslist

            self.emit(Signals.toprated_ready,topRated)
        elif item.funcname == "update_models":
            LOG.debug("update apt cache ready")
            pkgname = item.kwargs["packagename"]
            action = item.kwargs["action"]
            print "update apt cache ready:",len(reslist),pkgname

            self.emit(Signals.apt_cache_update_ready,action, pkgname)
        elif item.funcname == "init_models":
            LOG.debug("init models ready")
            self.emit(Signals.init_models_ready,"ok","获取分类信息完成")
            print "init models ready"

    def update_rating_reviews(self,rnrStats):
        print "update_rating_reviews:",len(rnrStats)

        for rnrStat in rnrStats:
            self.db.update_app_rnr(rnrStat.pkgname,rnrStat.ratings_average,rnrStat.ratings_total,rnrStat.reviews_total,0)

    def update_toprated(self,rnrStats):
        print "update_toprated:",len(rnrStats)
        if len(rnrStats) == 0:
            return

        self.db.init_toprated_table(rnrStats)

def _reviews_ready_callback(str_pkgname, reviews_data, my_votes=None,
                        action=None, single_review=None):
    print "\n***Enter _reviews_ready_callback..."
    print str_pkgname
    for review in reviews_data:
      print("rating: %s  user=%s" % (review.rating,
          review.reviewer_username))
      print(review.summary)
      print(review.review_text)
      print("\n")
    print "\n\n"


if __name__ == "__main__":

    #初始化打开cache
    appManager = AppManager()
    appManager.open_cache()
    print appManager.name
    #加载软件分类
    cat_list = appManager.get_category_list(True,"../data/category/")
#    print appManager.cat_list
#    print appManager.get_category_byname("office")
 #   print appManager.get_category_apps('')
    app = appManager.get_application_by_name("abe")
    ver = app.package.candidate
    print ver.record
    print ver.uri
#    print app
#    apps = appManager.get_recommend_apps()
    print app
#    print app.thumbnail
#    print app.screenshot
#    appManager.get_application_screenshots("gimp","/home/maclin/test/")
#    appManager.install_application("adanaxisgpl")
#    appManager.install_application("adonthell")
#    appManager.get_application_reviews("gimp",_reviews_ready_callback)
#    appManager.get_rating_review_stats()
#    appManager.get_toprated_stats()
    print "waiting..........\n\n"
    while True:
        print "***"
        time.sleep(2)
