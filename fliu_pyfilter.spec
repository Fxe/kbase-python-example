/*
A KBase module: fliu_pyfilter
*/

module fliu_pyfilter {
    typedef structure {
        string report_name;
        string report_ref;
        string fbamodel_id;
    } ReportWithModel;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_fliu_pyfilter(mapping<string,UnspecifiedObject> params) 
        returns (ReportWithModel output) authentication required;

    funcdef sbml_importer(mapping<string,UnspecifiedObject> params)
        returns (ReportWithModel output) authentication required;

    funcdef integrate_model(mapping<string,UnspecifiedObject> params)
        returns (ReportWithModel output) authentication required;

    funcdef auto_propagate_genome(mapping<string,UnspecifiedObject> params)
        returns (ReportWithModel output) authentication required;
};
