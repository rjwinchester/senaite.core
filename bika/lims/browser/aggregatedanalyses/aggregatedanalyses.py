# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.permissions import *
from bika.lims.browser.aggregatedanalyses.aggregatedanalyses_filter_bar\
    import AggregatedanalysesBikaListingFilterBar
import json
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING


class AggregatedAnalysesView(AnalysesView):
    """
    View the displays a list of analyses with results pending, regardless of
    the Analysis Requests or Worksheets to which they belong. Thus, analyses
    of received samples, but without results or with verification pending.
    This view is similar to other "manage_results" views (the user can submit
    results, etc.). The view's main purpose is to provide a fast overview of
    analyses with results pending, as well as results introduction, without
    the need of browsing through Analysis Requests and/or Worksheets.
    Eventhough, the recommended process for the introduction of results is
    by using worksheets instead.
    This view makes use of CATALOG_ANALYSIS_LISTING for items retrieval and
    minimises the use of Analysis objects.
    """

    def __init__(self, context, request, **kwargs):
        super(AggregatedAnalysesView, self).__init__(context, request)
        self.title = _("Analyses pending")
        self.show_select_all_checkbox = False
        self.show_categories = False
        self.pagesize = 50
        # Get temp objects that are too time consuming to obtain every time
        self.bika_catalog = getToolByName(context, 'bika_catalog')
        # Check if the filter bar functionality is activated or not
        self.filter_bar_enabled =\
            self.context.bika_setup.getDisplayAdvancedFilterBarForAnalyses()

        # each editable item needs it's own allow_edit
        # which is a list of field names.
        self.allow_edit = True

        self.columns['AnalysisRequest'] = {
            'title': _('Analysis Request'),
            'attr': 'getAnalysisRequestTitle',
            'replace_url': 'getAnalysisRequestURL',
            'sortable': False
            }
        self.columns['Worksheet'] = {
            'title': _('Worksheet'),
            'sortable': False
            }
        self.review_states = [
            {'id': 'default',
             'title':  _('Results pending'),
             'transitions': [{'id': 'sample'},
                             {'id': 'submit'},
                             {'id': 'cancel'},
                             # {'id': 'assign'}
                             ],
             'contentFilter': {'review_state': [
                'sample_received', 'assigned', 'attachment_due']},
             'columns': ['AnalysisRequest',
                         'Worksheet',
                         'Service',
                         'Result',
                         'Uncertainty',
                         'Partition',
                         'Method',
                         'Instrument',
                         'Analyst',
                         'state_title',
                         ]
             },
            {'id': 'to_be_verified',
             'title':  _('To be verified'),
             'transitions': [{'id': 'verify'},
                             {'id': 'cancel'}
                             ],
             'contentFilter': {'review_state': [
                 'to_be_verified']},
             'columns': ['AnalysisRequest',
                         'Worksheet',
                         'Service',
                         'Result',
                         'Uncertainty',
                         'Partition',
                         'Method',
                         'Instrument',
                         'Analyst',
                         'state_title',
                         ]
             },
        ]

    def getPOSTAction(self):
        return 'aggregatedanalyses_workflow_action'

    def isItemAllowed(self, obj):
        """
        Checks if the passed in Analysis must be displayed in the list. If the
        'filtering by department' option is enabled in Bika Setup, this
        function checks if the Analysis Service associated to the Analysis
        is assigned to any of the currently selected departments (information
        stored in a cookie). In addition, the function checks if the Analysis
        matches with the filtering criterias set in the advanced filter bar.
        If no criteria in the advanced filter bar has been set and the option
        'filtering by department' is disblaed, returns True.

        :param obj: A single Analysis brain
        :type obj: CatalogBrain
        :returns: True if the item can be added to the list. Otherwise, False
        :rtype: bool
        """
        # The isItemAllowed function from the base class AnalysesView already
        # takes into account filtering by department
        allowed = super(AnalysesView, self).isItemAllowed(obj)
        if not allowed:
            return False

        if self.filter_bar_enabled:
            # Advanced filter bar is enabled. Check if the Analysis matches
            # with the filtering criterias.
            return self.filter_bar_check_item(obj)

        # By default, display the analysis
        return True

    def folderitem(self, obj, item, index):
        """
        In this case obj should be a brain
        """
        item = super(AnalysesView, self).folderitem(obj, item, index)
        if not item:
            return None

        # Worksheet
        item['Worksheet'] = ''
        wss = self.bika_catalog(getAnalysesUIDs={
                    "query": obj.UID,
                    "operator": "or"
                })
        if wss and len(wss) == 1:
            # TODO-performance: don't get the whole object
            ws = wss[0].getObject()
            item['Worksheet'] = ws.Title()
            anchor = '<a href="%s">%s</a>' % (ws.absolute_url(), ws.Title())
            item['replace']['Worksheet'] = anchor

        return item

    def getFilterBar(self):
        """
        This function creates an instance of BikaListingFilterBar if the
        class has not created one yet.
        :returns: a BikaListingFilterBar instance
        :rtype: bika.lims.browser.BikaListingFilterBar
        """
        if not self._advfilterbar:
            self._advfilterbar = AggregatedanalysesBikaListingFilterBar(
                                    context=self.context, request=self.request)
        return self._advfilterbar
