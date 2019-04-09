# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import urllib.request

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil
#END_HEADER


class fliu_pyfilter:
    '''
    Module Name:
    fliu_pyfilter

    Module Description:
    A KBase module: fliu_pyfilter
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "git@github.com:Fxe/kbase_python_module.git"
    GIT_COMMIT_HASH = "19e6d97c3b8dcdb7a7aad27267d3e4b4fc24a32d"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_fliu_pyfilter(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportWithModel" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String,
           parameter "fbamodel_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_fliu_pyfilter
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_fliu_pyfilter

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_fliu_pyfilter return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def sbml_importer(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportWithModel" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String,
           parameter "fbamodel_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN sbml_importer
        print(params)

#{'biomass': [], 'model_name': 'test', 
# 'sbml_url': 'http://bigg.ucsd.edu/static/models/e_coli_core.xml', 
# 'automatically_integrate': 1, 'workspace_name': 'filipeliu:narrative_1554172974237', 
# 'remove_boundary': 1}
        def valid_string_arg(key, params):
            return key in params and not params[key] == None and len(params[key].strip()) > 0

        dfu = DataFileUtil(self.callback_url)

        if valid_string_arg('sbml_url', params):
            urllib.request.urlretrieve(params['sbml_url'], '/kb/module/data/sbml.xml')
            
        elif valid_string_arg('input_staging_file_path', params):
            logging.info('pulling from staging: %s' % params['input_staging_file_path'])
            retval = dfu.download_staging_file(
                {
                    'staging_file_subdir_path': params['input_staging_file_path']
                }
            )

            logging.info('download_staging_file: %s' % retval)
        else:
            logging.info('invalid file arguments: %s' % params)

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['sbml_url']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END sbml_importer

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method sbml_importer return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def integrate_model(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportWithModel" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String,
           parameter "fbamodel_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN integrate_model
        print(params)

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END integrate_model

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method integrate_model return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def auto_propagate_genome(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportWithModel" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String,
           parameter "fbamodel_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN auto_propagate_genome

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': params['parameter_1']},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END auto_propagate_genome

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method auto_propagate_genome return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
