# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import urllib.request
import json
import uuid

from fliu_pyfilter.wut import mkdir_p
from fliu_pyfilter.escher_curation import EscherModel, EscherMap
from fliu_pyfilter.bios_utils import read_json, write_json
import shutil
import escher
import cobra
import cobrakbase

from kbase_python import fetch_models_from_url
from kbase_python import convert_sbml_to_kbase

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
    GIT_COMMIT_HASH = "7f8e76300be366d07e826e98440f4cab88330a29"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        
        self.dfu = DataFileUtil(self.callback_url)
        self.report = KBaseReport(self.callback_url)
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
        ws = params['workspace_name']
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
        ws = params['workspace_name']
#{'biomass': [], 'model_name': 'test', 
# 'sbml_url': 'http://bigg.ucsd.edu/static/models/e_coli_core.xml', 
# 'automatically_integrate': 1, 'workspace_name': 'filipeliu:narrative_1554172974237', 
# 'remove_boundary': 1}

        def valid_string_arg(key, params):
            return key in params and not params[key] == None and len(params[key].strip()) > 0

        dfu = DataFileUtil(self.callback_url)

#        if valid_string_arg('sbml_url', params):
#            urllib.request.urlretrieve(params['sbml_url'], '/kb/module/data/sbml.xml')
#
#        elif valid_string_arg('input_staging_file_path', params):
#            logging.info('pulling from staging: %s' % params['input_staging_file_path'])
#            retval = dfu.download_staging_file(
#                {
#                    'staging_file_subdir_path': params['input_staging_file_path']
#                }
#            )
#
#            logging.info('download_staging_file: %s' % retval)
#        else:
#            logging.info('invalid file arguments: %s' % params)

        model_id = params['model_name']
        sbml_url = params['sbml_url']
        biomass_ids = params['biomass']
        
        config = {
            'jar_path' : '/kb/module/data/bin',
            'out_path' : '/kb/module/data/json',
            'download_path' : '/kb/module/data/download',
        }
        
        fbamodel_files = fetch_models_from_url(sbml_url, model_id, biomass_ids, config)

        print('model', fbamodel_files)

        fbamodel_objects = []
        for model in fbamodel_files:
            with open(model, 'r') as f:
                fbamodel = json.loads(f.read())
                fbamodel_objects.append(fbamodel)

        objects_created = []

        kbase = cobrakbase.KBaseAPI(ctx['token'], config=self.config)

        for fbamodel in fbamodel_objects:
            kbase.save_object(fbamodel['id'], fbamodel, 'FBA', ws)
            1

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created' : objects_created,
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

    def sbml_to_kbase(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportWithModel" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String,
           parameter "fbamodel_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN sbml_to_kbase
        
        kbase = cobrakbase.KBaseAPI(ctx['token'], config=self.config)
        
        config = {
            'jar_path' : '/kb/module/data/bin',
            'out_path' : '/kb/module/data/json',
            'download_path' : '/kb/module/data/download',
        }
        
        model_objects = convert_sbml_to_kbase(params['filename'], 
                                              params['model_id'], 
                                              params['auto_integrate'], 
                                              params['remove_boundary'],
                                              params['biomass_ids'],
                                              config)
        
        output = model_objects[0]
        
        #END sbml_to_kbase

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method sbml_to_kbase return value ' +
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

    def escher_fbamodel(self, ctx, params):
        """
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportWithModel" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String,
           parameter "fbamodel_id" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN escher_fbamodel
        ws = params['workspace_name']
        kbase = cobrakbase.KBaseAPI(ctx['token'], dev=True)
        kmodel = kbase.get_object(params['model_id'], ws)
        fbamodel = cobrakbase.core.model.KBaseFBAModel(kmodel)
        flux_data = None
        if 'fba_id' in params:
            kfba = kbase.get_object(params['fba_id'], ws)
            fba = cobrakbase.core.model.KBaseFBASolution(kfba)
            flux_data = {}
            for rxn_var in fba.data['FBAReactionVariables']:
                flux = rxn_var['value']
                rxn_id = rxn_var['modelreaction_ref'].split('/')[-1]
                flux_data[rxn_id] = flux
            for rxn_var in fba.data['FBABiomassVariables']:
                flux = rxn_var['value']
                rxn_id = rxn_var['biomass_ref'].split('/')[-1]
                flux_data[rxn_id + '_biomass'] = flux
            for rxn_var in fba.data['FBACompoundVariables']:
                flux = rxn_var['value']
                cpd_id = rxn_var['modelcompound_ref'].split('/')[-1]
                flux_data['EX_' + cpd_id] = -1 * flux
        #kmedia = kbase.get_object('Carbon-D-Glucose', ws)
        
        def fetch_metabolites_and_reactions(fbamodel, compartment_match = 'c0', compartment_match2 = 'c'):
            rxn_map_to_model = {}
            compartment_match2 = 'c'

            for modelreaction in fbamodel.reactions:
                reaction_ref = modelreaction.data['reaction_ref'].split('/')[-1]
                seed_id, compartment = reaction_ref.split('_')
                if compartment == compartment_match2:
                    rxn_map_to_model[seed_id] = modelreaction.id
                #print(modelreaction.id, seed_id, compartment)

            compartment_match = 'c0'
            cpd_map_to_model = {}
            for metabolite in fbamodel.metabolites:
                seed_id = metabolite.data['compound_ref'].split('/')[-1]
                compartment = metabolite.data['modelcompartment_ref'].split('/')[-1]
                if compartment == compartment_match:
                    cpd_map_to_model[seed_id] = metabolite.id

            return cpd_map_to_model, rxn_map_to_model

        def build_escher_map(escher_map, model_json):
            map_json_str = json.dumps(escher_map.escher_map)
            builder = escher.Builder(map_json=map_json_str, model_json=model_json, reaction_data=flux_data)
            builder.set_highlight_missing(True)
            builder.set_enable_tooltips(True)
            builder.set_show_gene_reaction_rules(True)
            builder.set_and_method_in_gene_reaction_rule(True)
            return builder
        
        cpd_map_to_model, rxn_map_to_model = fetch_metabolites_and_reactions(fbamodel)
        print('cpd_map_to_model', len(cpd_map_to_model), 'rxn_map_to_model', len(rxn_map_to_model))
        
        ESCHER_HOME = '/kb/module/data/escher'
        escher_model_data = read_json(ESCHER_HOME + '/models/' + 'BIOS' + '/' + 'bios7.json')
        escher_model = EscherModel(escher_model_data)
        cpd_remap, rxn_remap = escher_model.map_escher_model_data(cpd_map_to_model, rxn_map_to_model)
        
        map_list = [{'organism': 'BIOS', 'map_name': 'bios7.proteins'},
 {'organism': 'BIOS', 'map_name': 'bios7.Quinones'},
 {'organism': 'BIOS', 'map_name': 'bios7.fa'},
 {'organism': 'BIOS', 'map_name': 'bios7.AA'},
 {'organism': 'BIOS', 'map_name': 'bios7.LipidIV'},
 {'organism': 'BIOS', 'map_name': 'bios7.thf'},
 {'organism': 'BIOS', 'map_name': 'bios7.Central'},
 {'organism': 'BIOS', 'map_name': 'bios7.mycolate'},
 {'organism': 'BIOS', 'map_name': 'bios7.Riboflavin'},
 {'organism': 'BIOS', 'map_name': 'bios7.sugars'},
 {'organism': 'BIOS', 'map_name': 'bios7.f430'},
 {'organism': 'BIOS', 'map_name': 'bios7.Thiamine'},
 {'organism': 'BIOS', 'map_name': 'bios7.Nucleotides'},
 {'organism': 'BIOS', 'map_name': 'bios7.peptidoglycan'}]
        
        media_const = {}
        cobra_model = cobrakbase.convert_kmodel(kmodel, media_const)
        model_json = cobra.io.to_json(cobra_model)
        
        catalog = {}
        
        for o in map_list:
            map_id = o['map_name']
            escher_map_data = read_json(ESCHER_HOME + '/maps/' + 'BIOS' + '/' + map_id + '.json')
            escher_map = EscherMap(escher_map_data)
            escher_map.swap_ids(cpd_remap, rxn_remap)
            builder = build_escher_map(escher_map, model_json)
            builder.save_html('/kb/module/data/report/maps/' + map_id, overwrite=True)
            catalog[map_id]= {
                "reactions" : 10,
                "model_flux" : 20,
                "model_reactions" : 30,
                "model_genes" : 40,
                "src" : "maps/" + map_id + ".html"
            }
        
        write_json(catalog, '/kb/module/data/report/catalog.json')
        
        print(params)
        
        output_directory = os.path.join(self.shared_folder, str(uuid.uuid4()))
        mkdir_p(output_directory)
        
        print('output_directory', output_directory, os.listdir(output_directory))
        shutil.copytree('/kb/module/data/report', output_directory + '/report')
        
        print(output_directory)
        
        shock_id = self.dfu.file_to_shock({
            'file_path': output_directory + '/report',
            'pack': 'zip'
        })['shock_id']
        
        html_report = []
        html_report.append({
            'shock_id': shock_id,
            'name': 'index.html',
            'label': 'viewer',
            'description': 'description'
        })
        
        report = KBaseReport(self.callback_url)
        
        report_params = {
            'message': 'message_in_app ' + output_directory,
            'warnings': ['warnings_in_app'],
            'workspace_name': ws,
            'objects_created': [],
            'html_links': html_report,
            'direct_html_link_index': 0,
            'html_window_height': 600,
        }
        
        print(report_params)
        report_info = report.create_extended_report(report_params)
        
        output = {
            'report_name': report_info['name'], 
            'report_ref': report_info['ref']
        }
        
        #END escher_fbamodel

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method escher_fbamodel return value ' +
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
