/*
A KBase module: fliu_pyfilter
*/

module fliu_pyfilter {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_fliu_pyfilter(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
