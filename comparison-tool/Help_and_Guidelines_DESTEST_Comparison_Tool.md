# Guidelines for the DESTEST Comparison Tool

**IBPSA Project 1 - District Energy Simulation Test Procedure (DESTEST)**

# Table of Contents

1. [Introduction](#introduction)
1. [DESTEST Comparison Tool Procedure (Step by Step)](#destest-comparison-tool-procedure-step-by-step)
    1. [Select Case Type for DESTEST Comparison](#select-case-type-for-destest-comparison)
    1. [Select Case Characteristics for DESTEST Comparison](#select-case-characteristics-for-destest-comparison)
    1. [Loading Parameters of the Selected Case](#loading-parameters-of-the-selected-case)
    1. [Checking the Validity of the Online DESTEST Repository](#checking-the-validity-of-the-online-destest-repository)
    1. [Loading DESTEST Data](#loading-destest-data)
    1. [Select User Data File](#select-user-data-file)
    1. [Select List of KPIs and Comparison Metrics](#select-list-of-kpis-and-comparison-metrics)
    1. [Computation of the DESTEST Comparison Calculation](#computation-of-the-destest-comparison-calculation)
    1. [Generation of the Output Analysis Report with Figures and Tables](#generation-of-the-output-analysis-report-with-figures-and-tables)
1. [Output Analysis Report with Figures and Tables](#output-analysis-report-with-figures-and-tables)
1. [Editing and Expanding the DESTEST Comparison Tool](#editing-and-expanding-the-destest-comparison-tool)

# Introduction

The DESTEST procedure consists in the comparison, benchmarking and thorough verification of a number of common exercises. In each common exercise, different participants are modelling and simulating a given case of buildings and/or energy grid with well-defined properties, characteristics, grid topology, weather conditions, and boundary conditions. The participants can use any suitable commercial or non-commercial simulation tools or the dedicated Modelica libraries. The simulation results of all participants are compared with each other by a dedicated Python-based time series comparison tool.

This document is a tutorial to use a dedicated Python-based tool for the comparison and analysis of the result times series from the different common exercises of the DESTEST.

[Go back :arrow_up:](#table-of-contents)

# DESTEST Comparison Tool Procedure (Step by Step)

The DESTEST Comparison Tool is a linear Graphical User Interface (GUI) that guides the user through the different steps to select a specific common exercise case and compare all results of the latter to a reference case and compare them to the user result data (optional).
The comparison consists of the calculation of the difference between the time series of the different output result parameters. This difference calculation is performed according to different Key Performance Indicators (KPIs) / Comparison Metrics and grading weights that can be specified by the user.
The User can stop the DESTEST Comparison Procedure at any time by closing the GUI window (cross icon on the upper right corner of the GUI window).

On the welcome window, the user can read a short overview of the different steps of the DESTEST comparison procedure. The user can open the help file, start the procedure or switch the echo mode on and off by pressing the dedicated buttons. If the echo mode is on, feedback messages are displayed at the different steps of the DESTEST procedure, figures and tables are displayed in the Python IDE at the end of the procedure.

![Welcome message at the start of the GUI for the DESTEST Comparison Tool Procedure](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%201.png)

*Welcome message at the start of the GUI for the DESTEST Comparison Tool Procedure.*

[Go back :arrow_up:](#table-of-contents)

## Select Case Type for DESTEST Comparison

The first step of the DESTEST comparison procedure is to select a specific common exercise case. On the first GUI window, the user can choose between common exercise cases focusing on the simulation of buildings only, or the simulation of district heating network only.

![GUI for the common exercise case type selection](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%202.png)

*GUI for the common exercise case type selection.*

In the near future, common exercise cases about district cooling network only and the simulation of district heating / cooling network coupled with models of buildings will also be available in that tool.

The user can change the common exercise case type selection by clicking the dropdown menu. To confirm the case type selection and proceed to the next step, the user must click the “Confirm Selection” button.

[Go back :arrow_up:](#table-of-contents)

## Select Case Characteristics for DESTEST Comparison

The second step of the DESTEST comparison procedure is to select the specific characteristics of the common exercise case.

![GUI for the common exercise case characteristics selection (in here, example of characteristics of the building case type)](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%203.png)

*GUI for the common exercise case characteristics selection (in here, example of characteristics of the building case type).*

For example, in the case of the building simulation common exercise cases, the user can choose the type of buildings (single-family dwellings or office buildings), the year of construction (which is related to the energy performance of the building envelope), and the type of occupants’ schedule (which is related to the scheduling of internal gains and control setpoints).

The user can change the common exercise case characteristics selection by clicking the different dropdown menus. To confirm the case characteristics selection and proceed to the next step, the user must click the “Confirm Selections” button.

After confirmation of the case characteristics, the program generates a name-tag that is then used to find the corresponding parameter and data files among all files of the online DESTEST repository.

[Go back :arrow_up:](#table-of-contents)

## Loading Parameters of the Selected Case

Once the type and characteristics of the common exercise case have been selected and confirmed, a parameter file corresponding to these type and characteristics is searched in the online DESTEST repository. If there is no parameter file corresponding to this type and characteristics in the online repository, an error is issued and the procedure is terminated. If the corresponding parameter file is found, the validity of its content is checked. If the content of the parameter file is valid (no missing data and coherent data), it is loaded.

![Loading parameters of the selected common exercise case](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%204.png)

*Loading parameters of the selected common exercise case.*

These parameters are then used to check the validity of the result data files from the different participants that have been loaded onto the online repository (verification of the number of data columns, number of data rows, length of the file header, list of data parameter names, sampling time interval, starting date and time). The parameter file also contains information for the comparison procedure such as the list of default KPIs / Comparison Metrics, the list of default KPI weights, and the list of typical days to be shown on the result figures.

[Go back :arrow_up:](#table-of-contents)

## Checking the Validity of the Online DESTEST Repository

On that step, the validity of the online DESTEST repository is verified as follows: the repository needs to contain at least one valid data file corresponding to the selected common exercise case type and characteristics.

![Checking the validity of the online DESTEST repository](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%205.png)

*Checking the validity of the online DESTEST repository.*

[Go back :arrow_up:](#table-of-contents)

## Loading DESTEST Data

On that step, all data files found in the online DESTEST repository that fit the name-tag of the common exercise case type and characteristics are checked for validity (according to the corresponding parameter file) and loaded if validated. The program indicates to the user the total number of data files that fit the name-tag of the case, and the number of valid and invalid files among those.

![Loading the pool of data from the DESTEST repository](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%206.png)

*Loading the pool of data from the DESTEST repository.*

[Go back :arrow_up:](#table-of-contents)

## Select User Data File

On that step, the user can choose to upload its own data result file. However, this is optional and the user can proceed to the next step by clicking the “Continue Without User Data File” button. If the user does so, the rest of the DESTEST procedure will be conducted without user data file, and will only compare the result data files of other participants that have been uploaded into the online DESTEST repository.

![GUI for the selection of the user data file](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%207.png)

*GUI for the selection of the user data file.*

The user can select its own data result file by clicking the “Select User Data File” button. Once the user data file is selected, its validity will be verified according to the parameter file. The program will indicate if the user data file is valid or not. If it is valid, the user can proceed to the next step with the current user data file.

The user can get information about how to format its data file to make it valid for the DESTEST procedure by clicking the buttons of the “Get Help to Format User Test Data File” section. The user can thus display information about the format of a valid data file, it can download the entire parameter file of the corresponding common exercise case, or it can download an example of a valid data file from the online DESTEST repository.

[Go back :arrow_up:](#table-of-contents)

## Select List of KPIs and Comparison Metrics

On that step, the user can select a list of KPIs / Comparison Metrics that is used to compare and calculate the difference between the different result time series of the common exercises cases with a reference result.

The user can add new KPIs from the dropdown menu into the list of selected KPIs. However, the same KPI cannot be added more than once into the list of selected KPIs. The user can also remove a selected KPI from the list of selection or clear the entire list. At least one KPI has to be in the list to proceed to the next step.

The user can also allocate a specific weight to each of the selected KPIs / Comparison Metrics. This weight corresponds to the weight of the KPI for the calculation of the summary error and accuracy grades.

It is recommended that the user does not change the default KPIs / Comparison Metrics and weights, and proceed directly to the next step of the DESTEST Comparison.

![GUI for the selection of the list of KPIs and Comparison Metrics for the DESTEST Comparison](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%208.png)

*GUI for the selection of the list of KPIs and Comparison Metrics for the DESTEST Comparison.*

[Go back :arrow_up:](#table-of-contents)

## Computation of the DESTEST Comparison Calculation

On that step, the comparison of the different sets of results (for the same common exercise case) is made as the calculation of the differences between each result time series and a reference result time series.

![Computation of the DESTEST Comparison calculation](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%209.png)

*Computation of the DESTEST Comparison calculation.*

These time series differences are calculated according to the different KPIs / Comparison Metrics selected at the previous step. For each measurement parameter of interest, the reference time series is generated as the point-by-point mean average of all valid common exercise time series loaded at the previous step.

The different sets of results might perform differently (in terms of how close they are from the reference time series) for the various KPIs / Comparison Metrics that are used to calculate a difference between two time series. The variety of comparison metrics is useful for a thorough analysis of each sets of results. However, a summary grading system is necessary to make a global assessment and ranking of the different sets of results.

In the DESTEST Comparison Tool, a summary accuracy grade is calculated as follows: for each result time series (corresponding to a specific measurement parameter of interest), each KPI / Comparison Metric is calculated. For each measurement parameter and each KPI / Comparison Metric, each set of results receives points: 100% points for the set that performs the best according to the corresponding KPI, and 0% points for the set that performs the worst. Finally, a summary accuracy grade (from 0% to 100%) is calculated for each set of results as the weighted average of all the points received for each measurement parameter and KPI.

For example, if one set of results (corresponding to a specific modeller for a specific common exercise case) has the best score for all KPIs / Comparison Metrics calculated for each measurement parameter, this set will get a summary accuracy grade of 100%.
Conversely, if one set of results has the worst score for all KPIs / Comparison Metrics calculated for each measurement parameter, this set will get a summary accuracy grade of 0%.

[Go back :arrow_up:](#table-of-contents)

## Generation of the Output Analysis Report with Figures and Tables

...

![Generation of the Output Analysis Report with Figures and Tables](https://github.com/ibpsa/project1-destest/blob/HichamJohra-patch-guidelines_and_help_comparison_tool/comparison-tool/icon/GUI%20Figure%2010.png)

*Generation of the Output Analysis Report with Figures and Tables.*

[Go back :arrow_up:](#table-of-contents)

# Output Analysis Report with Figures and Tables

*This is currently under construction*

*Explanation of what is in the output report. Take an example of output report and explain what is what in great details.*

[Go back :arrow_up:](#table-of-contents)

# Editing and Expanding the DESTEST Comparison Tool

*This is currently under construction*

*Some instructions about the structure of the Python code and how to add new cases for new common exercises and new KPIs / Comparison Metrics*

*Add new KPIs / Comparison Metrics: where to place them in the dictionary and where to place the sub-functions*

*Add new cases in the list of cases: make sure that the tag label in between squared brackets fits the nametag of the parameter and data files.*

[Go back :arrow_up:](#table-of-contents)
