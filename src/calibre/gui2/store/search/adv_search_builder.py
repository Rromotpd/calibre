# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__ = 'GPL 3'
__copyright__ = '2011, John Schember <john@nachtimwald.com>'
__docformat__ = 'restructuredtext en'

import re

from PyQt4.Qt import (QDialog, QDialogButtonBox)

from calibre.gui2.store.search.adv_search_builder_ui import Ui_Dialog
from calibre.library.caches import CONTAINS_MATCH, EQUALS_MATCH

class AdvSearchBuilderDialog(QDialog, Ui_Dialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.buttonBox.accepted.connect(self.advanced_search_button_pushed)
        self.tab_2_button_box.accepted.connect(self.accept)
        self.tab_2_button_box.rejected.connect(self.reject)
        self.clear_button.clicked.connect(self.clear_button_pushed)
        self.adv_search_used = False
        self.mc = ''
        
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.currentChanged[int].connect(self.tab_changed)
        self.tab_changed(0)
        
    def tab_changed(self, idx):
        if idx == 1:
            self.tab_2_button_box.button(QDialogButtonBox.Ok).setDefault(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

    def advanced_search_button_pushed(self):
        self.adv_search_used = True
        self.accept()

    def clear_button_pushed(self):
        self.title_box.setText('')
        self.author_box.setText('')
        self.price_box.setText('')
        self.format_box.setText('')
        self.drm_combo.setCurrentIndex(0)
        self.download_combo.setCurrentIndex(0)
        self.affiliate_combo.setCurrentIndex(0)

    def tokens(self, raw):
        phrases = re.findall(r'\s*".*?"\s*', raw)
        for f in phrases:
            raw = raw.replace(f, ' ')
        phrases = [t.strip('" ') for t in phrases]
        return ['"' + self.mc + t + '"' for t in phrases + [r.strip() for r in raw.split()]]

    def search_string(self):
        if self.adv_search_used:
            return self.adv_search_string()
        else:
            return self.box_search_string()

    def adv_search_string(self):
        mk = self.matchkind.currentIndex()
        if mk == CONTAINS_MATCH:
            self.mc = ''
        elif mk == EQUALS_MATCH:
            self.mc = '='
        else:
            self.mc = '~'
        all, any, phrase, none = map(lambda x: unicode(x.text()),
                (self.all, self.any, self.phrase, self.none))
        all, any, none = map(self.tokens, (all, any, none))
        phrase = phrase.strip()
        all = ' and '.join(all)
        any = ' or '.join(any)
        none = ' and not '.join(none)
        ans = ''
        if phrase:
            ans += '"%s"'%phrase
        if all:
            ans += (' and ' if ans else '') + all
        if none:
            ans += (' and not ' if ans else 'not ') + none
        if any:
            ans += (' or ' if ans else '') + any
        return ans

    def token(self):
        txt = unicode(self.text.text()).strip()
        if txt:
            if self.negate.isChecked():
                txt = '!'+txt
            tok = self.FIELDS[unicode(self.field.currentText())]+txt
            if re.search(r'\s', tok):
                tok = '"%s"'%tok
            return tok

    def box_search_string(self):
        mk = self.matchkind.currentIndex()
        if mk == CONTAINS_MATCH:
            self.mc = ''
        elif mk == EQUALS_MATCH:
            self.mc = '='
        else:
            self.mc = '~'

        ans = []
        self.box_last_values = {}
        title = unicode(self.title_box.text()).strip()
        if title:
            ans.append('title:"' + self.mc + title + '"')
        author = unicode(self.author_box.text()).strip()
        if author:
            ans.append('author:"' + self.mc + author + '"')
        price = unicode(self.price_box.text()).strip()
        if price:
            ans.append('price:"' + self.mc + price + '"')
        format = unicode(self.format_box.text()).strip()
        if format:
            ans.append('format:"' + self.mc + format + '"')
        drm = unicode(self.drm_combo.currentText()).strip()
        if drm:
            ans.append('drm:' + drm)
        download = unicode(self.download_combo.currentText()).strip()
        if download:
            ans.append('download:' + download)
        affiliate = unicode(self.affiliate_combo.currentText()).strip()
        if affiliate:
            ans.append('affiliate:' + affiliate)  
        if ans:
            return ' and '.join(ans)
        return ''
