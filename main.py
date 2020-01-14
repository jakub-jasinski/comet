import os
import sys
from comet import Comet
import numpy as np
import PyXMCDA
from optparse import OptionParser
import matplotlib.pyplot as plt


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = OptionParser()

    parser.add_option("-i", "--in", dest="in_dir")
    parser.add_option("-o", "--out", dest="out_dir")

    (options, args) = parser.parse_args(argv[1:])

    in_dir = str(options.in_dir)
    in_dir = "./tests/in1"
    out_dir = str(options.out_dir)
    print(in_dir)
    # Creating a list for error messages
    errorList = []

    # If some mandatory input files are missing
    if not os.path.isfile(in_dir + "/alternatives.xml") or not os.path.isfile(
            in_dir + "/criteria.xml") or not os.path.isfile(
            in_dir + "/performanceTable.xml"):
        errorList.append("Some input files are missing")
    else:
        # We parse all the mandatory input files
        xmltree_alternatives = PyXMCDA.parseValidate(in_dir + "/alternatives.xml")
        xmltree_criteria = PyXMCDA.parseValidate(in_dir + "/criteria.xml")
        xmltree_perfTable = PyXMCDA.parseValidate(in_dir + "/performanceTable.xml")

        # We check if all madatory input files are valid
        if xmltree_alternatives is None:
            errorList.append("The alternatives file can't be validated.")
        if xmltree_criteria is None:
            errorList.append("The criteria file can't be validated.")
        if xmltree_perfTable is None:
            errorList.append("The performance table file can't be validated.")

        if not errorList:
            alternativesId = PyXMCDA.getAlternativesID(xmltree_alternatives)
            criteriaId = PyXMCDA.getCriteriaID(xmltree_criteria)
            perfTable = PyXMCDA.getPerformanceTable(xmltree_perfTable, alternativesId, criteriaId)
            thresholds = PyXMCDA.getConstantThresholds(xmltree_criteria, criteriaId)

            if not alternativesId:
                errorList.append("No alternatives found. Is your alternatives file correct ?")
            if not criteriaId:
                errorList.append("No criteria found. Is your criteria file correct ?")
            if not perfTable:
                errorList.append("No performance table found. Is your performance table file correct ?")

    if not errorList:
        table = []
        for key, value in perfTable.items():
            row = [val for val in value.values()]
            table.append(row)
        table = np.array(table)
        print(table)

        mej = np.genfromtxt('./tests/in1/mej.csv', delimiter=',')

        comet = Comet(table, 3, mej=mej)
        ranking = comet.evaluate()
        print(ranking)

        fileAltValues = open(out_dir+"/alternativesValues.xml", 'w')
        PyXMCDA.writeHeader(fileAltValues)
        fileAltValues.write("<alternativesValues>\n")
        for i, alt in enumerate(alternativesId):
            fileAltValues.write("<alternativeValue><alternativeID>" + alt + "</alternativeID><value>")
            val = ranking[i]
            fileAltValues.write("<real>" + str(val) + "</real></value></alternativeValue>\n")
        fileAltValues.write("</alternativesValues>\n")
        PyXMCDA.writeFooter(fileAltValues)
        fileAltValues.close()

        ranking = np.array(list(zip(["A" + str(x) for x in range(len(ranking))], ranking)))
        print(np.flipud(ranking[ranking[:, 1].argsort()]))

    print(errorList)
    fileMessages = open(out_dir + "/messages.xml", 'w')
    PyXMCDA.writeHeader(fileMessages)

    if not errorList:
        PyXMCDA.writeLogMessages(fileMessages, ["Execution ok"])
    else:
        PyXMCDA.writeErrorMessages(fileMessages, errorList)

    PyXMCDA.writeFooter(fileMessages)
    fileMessages.close()

if __name__ == "__main__":
    sys.exit(main(["-i ./tests/in1", "-o", "./tests/out1"]))
    #sys.exit(main())