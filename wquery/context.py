#-*- coding:utf-8 -*-
import cPickle
import os
from collections import defaultdict

from aqt import mw
from aqt.qt import QCheckBox, QComboBox, QRadioButton
from aqt.utils import shortcut, showInfo, showText

from .lang import _
from .odds import get_model_byId, get_ord_from_fldname

VERSION = '20170416001'
CONFIG_FILENAME = '.wqcfg'


class Config(object):

    def __init__(self, window):
        self.path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), CONFIG_FILENAME)
        self.window = window
        self.data = dict()
        self.version = '0'
        self.read()

    @property
    def pmname(self):
        return self.window.pm.name

    def save_options_dialog(self, dialog):
        comboboxs, labels = dialog.findChildren(
            QComboBox), dialog.findChildren(QRadioButton)
        dict_cbs, field_cbs = comboboxs[::2], comboboxs[1::2]
        model = get_model_byId(self.window.col.models, self.last_model_id)
        maps = [{"word_checked": label.isChecked(),
                 "dict": dict_cb.currentText().strip(),
                 "dict_unique": dict_cb.itemData(dict_cb.currentIndex()) if dict_cb.itemData(dict_cb.currentIndex()) else "",
                 "dict_field": field_cb.currentText().strip(),
                 "fld_ord": get_ord_from_fldname(model, label.text()
                                                 )}
                for (dict_cb, field_cb, label) in zip(dict_cbs, field_cbs, labels)]
        # profilename: {'last':last_model_id, '..model_id..':[..maps..]}
        self.data[self.last_model_id] = maps
        self.data['%s_last' % self.pmname] = self.last_model_id
        self.data['version'] = VERSION
        with open(self.path, 'wb') as f:
            cPickle.dump(self.data, f)

    def save_fm_dialog(self, dialog):
        self.data['dirs'] = dialog.dirs
        self.data['use_filename'] = dialog.chk_use_filename.isChecked()
        self.data['export_media'] = dialog.chk_export_media.isChecked()
        with open(self.path, 'wb') as f:
            cPickle.dump(self.data, f)

    def read(self):
        try:
            with open(self.path, 'rb') as f:
                self.data = cPickle.load(f)
                try:
                    self.last_model_id = self.data['%s_last' % self.pmname]
                    self.last_model_maps = self.data[self.last_model_id]
                    self.dirs = self.data.get('dirs', [])
                    self.version = self.data.get('version', '0')
                    if VERSION != self.version:
                        # showInfo(VERSION + self.version)
                        self.last_model_maps, self.last_model_id, self.dirs = list(),  0, list()
                except Exception as e:
                    showInfo(str(e))
                    self.last_model_maps, self.last_model_id, self.dirs = list(),  0, list()
        except:
            self.last_model_maps, self.last_model_id, self.dirs = list(),  0, list()

    def get_maps(self, model_id):
        return self.data.get(model_id, list())

    def get_dirs(self):
        return self.data.get('dirs', list())

    def use_filename(self):
        return self.data.get('use_filename', True)

    def export_media(self):
        return self.data.get('export_media', False)

# action context: editor? browser?
context = defaultdict(int)
config = Config(mw)
