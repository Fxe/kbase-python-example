import os
import subprocess
import json
import urllib.request
import urllib.parse
import requests
from os import listdir

DEFAULT_JAR_PATH = '.'
DEFAULT_JSON_OUT_PATH = '.'

def get_filename(url):
    a = urllib.parse.urlparse(url)
    return os.path.basename(a.path)

def valid_url(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok

def fetch_models_from_url(sbml_url, model_id, biomass_ids = None, config = {'download_path' : '/kb/module/data'}):
    if not valid_url(sbml_url):
        raise Exception('invalid url %s' % sbml_url)

    #detect ID from url
    filename = get_filename(sbml_url)
    
    fbamodels = []
    #download url
    import_file = config['download_path'] + '/' + filename
    urllib.request.urlretrieve(sbml_url, import_file)
    
    if model_id == None:
        model_id = filename[:filename.rfind('.')]
        
    fbamodels = convert_sbml_to_kbase(import_file, model_id, config = config)
    
    return fbamodels

def convert_sbml_to_kbase(filename, model_id, 
                          auto_integrate = True, 
                          remove_boundary = True, 
                          biomass_ids = [],
                          config = {}):
    return SbmlReader(auto_integrate, remove_boundary, config).read(filename, model_id, biomass_ids)

class SbmlReader:

    def __init__(self, auto_integrate = True, remove_boundary = True, config = {}):
        self.jre = config['jre'] if 'jre' in config else 'java'
        self.jar = config['jar'] if 'jar' in config else 'sbml-to-kbase.jar'
        self.working_dir = config['jar_path'] if 'jar_path' in config else DEFAULT_JAR_PATH
        self.output_dir  = config['out_path'] if 'out_path' in config else DEFAULT_JSON_OUT_PATH
        self.auto_integrate = auto_integrate
        self.remove_boundary = remove_boundary
        

    def read(self, filename, model_id = None, biomass_ids = []):
        importer_subprocess = [
            self.jre,
            '-Dlogback.configurationFile=file:./logback.xml',
            "-jar", self.jar,
            '--curation', '/Users/fliu/workspace/java/kbase-SBMLTools/data/cpd_curation.tsv',
            '--data', '/Users/fliu/workspace/java/kbase-SBMLTools/data/export',
            '--modelseed', '/Users/fliu/workspace/java/kbase-SBMLTools/data/modelseed',
            '-O', self.output_dir,
        ]
        if not biomass_ids == None and not len(biomass_ids) == 0:
            importer_subprocess.append('--biomass')
            importer_subprocess.append(';'.join(biomass_ids))
        if not model_id == None and not len(model_id.strip()) == 0:
            importer_subprocess.append('--name')
            importer_subprocess.append(model_id.strip())
        if self.auto_integrate:
            importer_subprocess.append('--integrate')
        if self.remove_boundary:
            importer_subprocess.append('--removeb')
            
        importer_subprocess.append(filename)

        process = subprocess.Popen(importer_subprocess, cwd=self.working_dir, stdout=subprocess.PIPE)
        out, err = process.communicate()
        
        #check json at path
        json_files = []
        for f in listdir(self.output_dir):
            if f.endswith('.json'):
                json_files.append(f)
                
        #read to objects
        imported_models = []
        for json_file in json_files:
            with open(self.output_dir + '/' + json_file, 'r') as f:
                o = json.loads(f.read())
                imported_models.append(o)
        
        return imported_models