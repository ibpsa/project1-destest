# -*- coding: utf-8 -*- #######################################################
#                                                                             #
#   Hicham Johra                                                              #
#   2020-12-30                                                                #
#   Aalborg University, Denmark                                               #
#   hj@build.aau.dk                                                           #
#                                                                             #
#   Acknowledgement to co-developers:                                         #
#      - Konstantin Filonenko, SDU, Denmark                                   #
#      - Michael Mans, RWTH Aachen University, Germany                        #
#      - Ina De Jaeger, KU Leuven, Belgium                                    #
#      - Dirk Saelens, KU Leuven, Belgium                                     #
#                                                                             #
###############################################################################

"To-do list" "----------------------------------------------------------------"
###############################################################################
"""
- Add function for generation of output analysis report as PDF or Excel (Konstantin)

- Add "send data" button to send pull-request the User Test Data File to the GitHub repository if the file is valid.
Then format the data file correctly, ask for a user name, generate name file with user name + tag-name of the common exercise case
check that this file name is not already in the list of data files found in the online repository under that name-tag
if not okay, then cancel operation. If it's all correct, then generate pull-request in the right sub-folder'
"""
###############################################################################

"#############################################################################"
"##                                                                         ##"
"##               DESTEST Comparison all files & user test                  ##"
"##                                                                         ##"
"#############################################################################"

"""
Type:
    Module + Script (at the end)

Description:
    This simple module contains all needed functions to take all csv data files
    of DESTEST tests in a dedicated Github online folder and the specifically
    selected csv file of DESTEST test user test (current test) and calculates
    comparison metrics between the user test data and the reference (average profile)
    created from all the other DESTEST test files.
    If run directly, the module execute a default script that runs a comparison
    of the selected DESTEST data.

Inputs (arguments):
- None

Outputs:
- .pdf report
- DataFrames as global variables in the workspace
- Graphs in the workspace

Assumptions for proper usage:
It is assumed that all parameters files are .txt files
and that all data files are .csv files.
It is assumed that all parameters files and DESTEST data files are stored on 
the DESTEST Github online repository and that the server_infor parameters 
corresponding to that online repository are correct.

Example:
>>> None
"""

"#############################################################################"
"##                               Initialization                            ##"
"#############################################################################"

# Import libraries ############################################################

try:
    import tkinter as tk  # GUIs
    from tkinter import filedialog  # Need to specifically import it from tkinter
    from tkinter import StringVar, Label, Entry, Listbox
    from tkinter import messagebox as mbox  # Message box
    from tkinter import HORIZONTAL  # Horizontal orientation of progress bar
    from tkinter.ttk import Progressbar
    import os  # Miscellaneous operating system interfaces
    import glob  # Unix style pathname pattern expansion
    import pandas as pd  # Data manipulation and analysis
    import numpy as np  # Math functions
    import math
    import re  # Regular expression operations
    import requests  # To get information from online github folders
    import sys  # System-specific parameters and functions
    import ntpath  # Equivalent to os.path when running on windows, but will work for all paths on all platforms.
    import time
    import plotly.graph_objects as go
    from plotly.offline import plot
    import matplotlib.pyplot as plt
    import matplotlib.dates as dates
    import webbrowser
    from datetime import date, datetime, timedelta  # Date and time stamp generation

except:
    message = str("An error has occurred: Some libraries / packages could not be imported correctly.\n\nYou should install (using pip) these missing libraries / packages to run the script correctly.\n\nThe script is terminated immediately.")
    "Create a tk gui, hide it immediately, and destroy it after message clicked"
    gui = tk.Tk()
    gui.withdraw()
    mbox.showerror("Error", message)  # Popup message window
    gui.destroy()
    raise

else:
    print("\nLoading of libraries completed")


"#############################################################################"
"##                             Common CLasses                              ##"
"#############################################################################"

"Exception for Abort action from the user"
class Abort_exception(Exception):
    """The user aborted the procedure."""
    pass


"Class parameters to carry information from parameter file"
class parameters:
    pass


"CLass server_info to carry information about the online folder with all the files"
class server_info:
    pass


"#############################################################################"
"##                            Common Functions                             ##"
"#############################################################################"

###############################################################################
###                      Get full path to online file                       ###
###############################################################################

def get_full_path_to_online_file(file_name, server_info, echo=False):
    """Generates the full path of a file to the online DESTEST repository from
    server information.
    """
    try:
        full_path_file = (
            server_info.root_raw_data
            + server_info.user
            + "/"
            + server_info.repository
            + server_info.master_folder_name
            + file_name)
    except:
        if echo:
            print("\nWrong file path generation.")
        raise
    else:
        return full_path_file


###############################################################################
###                      CVRMSE from diff case - ref                        ###
###############################################################################

def Calculate_CVRMSE_from_diff_case_ref(diff_case_ref, reference_vector):
    """Calculate the Coefficient of Variation of Root Mean Squared Error (CVRMSE)
    of a case compared to a reference: CVRMSE with all data points [%]"""

    nbr_samples = len(diff_case_ref)  # Number of samples
    avrg_ref = (reference_vector.mean())  # Average value of the reference = number samples ref * mean average ref
    square_diff = diff_case_ref ** 2
    sum_squares = square_diff.sum()
    CVRMSE = ((math.sqrt(sum_squares / nbr_samples)) / avrg_ref) * 100

    return CVRMSE


###############################################################################
###                             Daily amplitude                             ###
###############################################################################

def Calculate_daily_amplitude(input_vector):
    """Caculate the amplitude (max - min) over 24 hours (daily) from midnight
    to midnight on data df with date and time stamp in 1st column"""

    vector_min = input_vector.resample("1440min", on="Date and Time").min()  # Daily min (24h resampling)
    vector_max = input_vector.resample("1440min", on="Date and Time").max()  # Daily max (24h resampling)

    "With resample .min() or .max(), the date and time stamp column does not replace the index column, so need to select data column if only 1 data column for further calculation"
    vector_min = vector_min.iloc[:, 1]
    vector_max = vector_max.iloc[:, 1]

    daily_amplitude_vector = vector_max - vector_min  # Daily resampled amplitude

    return daily_amplitude_vector


"#############################################################################"
"##                   KPIs / Comparison Metrics functions                   ##"
"#############################################################################"

###############################################################################
###                                NMBE [%]                                 ###
###############################################################################

def function_NMBE(reference_vector, test_case_vector, date_and_time_stamp_vect):
    """Calculate the Normalized Mean Bias Error (NMBE) of a case compared to
    reference [%]. NMBE with all data points"""

    "Difference point by point for test case compared to reference profile"
    diff_case_ref = test_case_vector - reference_vector  # Case - Reference

    NMBE = (diff_case_ref.sum()) * 100 / (reference_vector.sum())

    return round(NMBE, 2)


###############################################################################
###                           Hourly CVRMSE [%]                             ###
###############################################################################

def function_Hourly_CVRMSE(reference_vector, test_case_vector, date_and_time_stamp_vect):
    """Calculate the Coefficient of Variation of Root Mean Squared Error (CVRMSE)
    on Hourly running average data: Need resampling at 60 min freq"""

    "Difference point by point for test case compared to reference profile"
    diff_case_ref = test_case_vector - reference_vector  # Case - Reference

    "Resampling"
    frames = [date_and_time_stamp_vect, diff_case_ref]  # The 2 df to concat
    diff_case_ref = pd.concat(frames, axis=1, join="outer")  # date and time followed by data on the right
    "With resample .mean(), the date and time stamp column replaces the index column, so no need to select data column if only 1 data column for further calculation"
    diff_case_ref = diff_case_ref.resample("60min", on="Date and Time").mean()  # Resample as hourly mean average: the time stamp column becomes index column

    hourly_CVRMSE = Calculate_CVRMSE_from_diff_case_ref(diff_case_ref, reference_vector)

    return round(hourly_CVRMSE, 2)


###############################################################################
###                      Daily Amplitude CVRMSE [%]                         ###
###############################################################################

def function_Daily_Amplitude_CVRMSE(reference_vector, test_case_vector, date_and_time_stamp_vect):
    """CVRMSE of the daily amplitude from midnight to midnight: Need resampling
    at 1440 min"""

    "Daily amplitude test case"
    frames = [date_and_time_stamp_vect, test_case_vector]  # The 2 df to concat
    input_vector = pd.concat(frames, axis=1, join="outer")  # date and time followed by data on the right
    Daily_amplitude_case = Calculate_daily_amplitude(input_vector)  # Get daily amplitude user test data

    "Daily amplitude reference profile"
    frames = [date_and_time_stamp_vect, reference_vector]  # The 2 df to concat
    input_vector = pd.concat(frames, axis=1, join="outer")  # date and time followed by data on the right
    Daily_amplitude_reference = Calculate_daily_amplitude(input_vector)  # Get daily amplitude user test data

    "Difference daily amplitude between test case and reference"
    Diff_daily_aimplitude_case_ref = Daily_amplitude_case - Daily_amplitude_reference

    "CVRMSE"
    daily_amp_CVRMSE = Calculate_CVRMSE_from_diff_case_ref(Diff_daily_aimplitude_case_ref, Daily_amplitude_reference)  # Calculate the CVRMSE

    return round(daily_amp_CVRMSE, 2)


###############################################################################
###             R squared (coefficient of determination) [-]                ###
###############################################################################

def function_R_squared_coeff_determination(reference_vector, test_case_vector, date_and_time_stamp_vect):
    """R squared (R2) is defined here as the coefficient of determination: it 
    is the proportion of the variance in the dependant variable (model output 
    or model prediction) that is predictable from the independent variable(s) 
    (model input).
    In other words: how good a linear regression fits the data in comparison 
    to a model that is only the average of the dependant variable.
    
    ref: https://en.wikipedia.org/wiki/Coefficient_of_determination#Definitions
    """

    "y: observations / reality / measured data / reference data"
    "f: prediction / fitted data / modeled data / test data"

    y = reference_vector
    f = test_case_vector

    "e: residuals"
    e = y - f

    "e2: squares of residuals"
    e2 = e ** 2

    "SSres: sum of squares of residuals, or residual sum of squares."
    SSres = e2.sum()

    "y_mean: mean of the observed /refeence data"
    y_mean = y.mean()

    "squares of difference to the mean for the observed / reference data"
    squares_diff_to_mean = (y - y_mean) ** 2

    "SStot: total sum of squares (proportional to the variance of the data)"
    SStot = squares_diff_to_mean.sum()

    R_squared = 1 - (SSres / SStot)

    return round(R_squared, 2)


###############################################################################
###                                 RMSE [-]                                ###
###############################################################################

def function_RMSE(reference_vector, test_case_vector, date_and_time_stamp_vect):
    """Calculate the Root Mean Squared Error (RMSE) of a case 
    compared to a reference [%]: RMSLE with all data points"""

    "y: observations / reality / measured data / reference data"
    "f: prediction / fitted data / modeled data / test data"

    y = reference_vector
    f = test_case_vector

    squares_diff = (y - f) ** 2

    sum_squares_diff = squares_diff.sum()

    nbr_samples = len(test_case_vector)

    average_squares_diff = sum_squares_diff / nbr_samples

    RMSE = np.sqrt(average_squares_diff)

    return round(RMSE, 2)


###############################################################################
###                                RMSLE [-]                                ###
###############################################################################

def function_RMSLE(reference_vector, test_case_vector, date_and_time_stamp_vect):
    """Calculate the Root Mean Squared Logarithmic Error (RMSLE) of a case 
    compared to a reference [%]: RMSLE with all data points"""

    "y: observations / reality / measured data / reference data"
    "f: prediction / fitted data / modeled data / test data"

    y = reference_vector
    f = test_case_vector

    log_f = np.log(f + 1)
    log_y = np.log(y + 1)

    squares_diff_logs = (log_f - log_y) ** 2

    sum_squares_diff = squares_diff_logs.sum()

    nbr_samples = len(test_case_vector)

    average_squares_diff = sum_squares_diff / nbr_samples

    RMSLE = np.sqrt(average_squares_diff)

    return round(RMSLE, 2)


###############################################################################
###                               CVRMSE [%]                                ###
###############################################################################

def function_CVRMSE(reference_vector, test_case_vector, date_and_time_stamp_vect):
    """Calculate the Coefficient of Variation of Root Mean Squared Error (CVRMSE)
    of a case compared to a reference: CVRMSE with all data points [%]"""

    "y: observations / reality / measured data / reference data"
    "f: prediction / fitted data / modeled data / test data"

    y = reference_vector
    f = test_case_vector

    squares_diff = (y - f) ** 2

    nbr_samples = len(reference_vector)  # Number of samples

    avrg_ref = (
        reference_vector.mean()
    )  # Average value of the reference = number samples ref * mean average ref

    sum_squares = squares_diff.sum()

    CVRMSE = ((np.sqrt(sum_squares / nbr_samples)) / avrg_ref) * 100

    return round(CVRMSE, 2)


###############################################################################
###                                Minimum                                  ###
###############################################################################

def function_Minimum(reference_vector, test_case_vector, date_and_time_stamp_vect):
    result = test_case_vector.min()
    return round(result, 2)


###############################################################################
###                                Maximum                                  ###
###############################################################################

def function_Maximum(reference_vector, test_case_vector, date_and_time_stamp_vect):
    result = test_case_vector.max()
    return round(result, 2)


###############################################################################
###                                Average                                  ###
###############################################################################

def function_Average(reference_vector, test_case_vector, date_and_time_stamp_vect):
    result = test_case_vector.mean()
    return round(result, 2)


###############################################################################
###                           Standard Deviation                            ###
###############################################################################

def function_std_dev(reference_vector, test_case_vector, date_and_time_stamp_vect):
    result = np.std(test_case_vector)
    return round(result, 2)


"#############################################################################"
"##                    Module (Definition of Functions)                     ##"
"#############################################################################"

###############################################################################
###                   Welcome message with link to help                     ###
###############################################################################

def welcome_message(echo=False):
    """
    Generate a GUI to display and welcome message to shortly introduce the 
    DESTEST online comparison GUI to the user and give access to online 
    documentation (lecture note from AAU).
    """

    # Initialize GUI ##########################################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change closing wnidow handling"
    def on_closing():
        """if closing the window, raise exception to be caught by error handler 
        to destroy the gui and raise the error to top level"""
        if mbox.askokcancel("ABORT", "Do you want to abort the DESTEST comparison procedure?"):
            raise Abort_exception("The user aborted the procedure.")

    gui.protocol("WM_DELETE_WINDOW", on_closing)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Welcome")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("440x305+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    # Sub-function: get_help ##################################################

    "Define the function to be executed by the get_help_button"

    def get_help(echo=False):
        "Open the help file pdf that is on the AAU server vbn.aau.dk"
        try:
            "Open markdown file from url in default web-browser"
            webbrowser.open("https://github.com/ibpsa/project1-destest/blob/master/comparison-tool/Help_and_Guidelines_DESTEST_Comparison_Tool.md")

        except:
            mbox.showerror("Error", "The help file could not be opened.")
            if echo:
                print("The help file could not be opened.")

        else:
            if echo:
                print("The help file has been opened.")

        return

    # End Sub-function ########################################################

    # Sub-function: OK_end ####################################################

    "Close the GUI window and proceed witht the rest of the procedure"
    def start():
        gui.destroy()  # Close the GUI window, no output

    # End Sub-function ########################################################

    # Pack/grid widgets and generate GUI ######################################

    "Pack/grid the different buttons and labels on the GUI window"

    frame1 = tk.LabelFrame(gui, width=420, height=228)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Display welcome message in GUI label"
    welcome_message_text = """Welcome to the DESTEST comparison tool.
    
    The DESTEST comparison procedure consists of the following steps:
    - Selection of the case type.
    - Selection of the case characteristics.
    - Loading of the pool of DESTEST data files.
    - Selection of the user data file (optional).
    - Selection of the KPIs / Comparison Metrics.
    - Computation of the data comparison.
    - Generation of the output analysis report with figures and tables.
    
    For more information, help and guidelines, click the "HELP" button.
    To start the DESTEST comparison procedure, click the "START" button."""
    my_label = tk.Label(frame1, text=welcome_message_text)  # Grid the welcome message on the window
    my_label.pack(padx=10, pady=10)

    "Frame 2"
    frame2 = tk.LabelFrame(gui, width=420, height=42)
    frame2.pack(padx=10, pady=(0, 5))
    frame2.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Dummy labels to grid inside frame with spacings"
    label1 = tk.Label(frame2)
    label1.grid(row=0, column=2)
    label1.config(font=("Courier", 2))

    label2 = tk.Label(frame2)
    label2.grid(row=2, column=2)
    label2.config(font=("Courier", 2))

    label3 = tk.Label(frame2,text="                                                                          ")
    label3.grid(row=1, column=2)
    label3.config(font=("Courier", 2))

    label4 = tk.Label(frame2, text="                                         ")
    label4.grid(row=1, column=0)
    label4.config(font=("Courier", 2))

    label5 = tk.Label(frame2, text="                                         ")
    label5.grid(row=1, column=4)
    label5.config(font=("Courier", 2))

    "HELP button"
    help_button = tk.Button(frame2, text="HELP", command=lambda: get_help())  # Create button executing function
    help_button.grid(row=1, column=1)

    "START button"
    start_button = tk.Button(frame2, text="START", command=lambda: start())  # Create button executing function
    start_button.grid(row=1, column=3)

    "Generate a mainLoop to activate the gui"
    gui.mainloop()  # Run loop updating the window

    # Outputs of GUI ##########################################################
    "No output of GUI once closed"
    return None


###############################################################################
###                      Prompt user for case type                          ###
###############################################################################

def prompt_user_case_type(echo=False):
    """
    Generate a GUI to prompt user for selecting the type of case: building or network.
    """

    # Initialize GUI ##########################################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change closing wnidow handling"
    def on_closing():
        """if closing the window, raise exception to be caught by error handler 
        to destroy the gui and raise the error to top level"""
        if mbox.askokcancel("ABORT", "Do you want to abort the DESTEST comparison procedure?"):
            raise Abort_exception("The user aborted the procedure.")

    gui.protocol("WM_DELETE_WINDOW", on_closing)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # Changing the Tk class itself.

    "Change the window properties"
    gui.title("Select Case Type")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("420x126+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    # Sub-function: confirm_selection #########################################

    "Confirm the selected case type and return it"

    def confirm_selection():
        gui.destroy()  # Close the GUI window, the output will be returned

    # End Sub-function ########################################################

    # Pack widgets and generate GUI ###########################################

    "Pack the different buttons and labels on the GUI window"

    "Frame 1"
    frame1 = tk.LabelFrame(gui, text="Case Type for DESTEST Comparison", width=400, height=60)
    frame1.pack(padx=10, pady=5)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Dropdown selection menu for case type"
    options_case_type = [
        "Building",
        "District Heating Network"]

    selected_case_type = StringVar()
    selected_case_type.set(options_case_type[0])

    dropdown_building_type = tk.OptionMenu(frame1, selected_case_type, *options_case_type)
    dropdown_building_type.pack(padx=30, pady=(5, 10))

    "Frame 2"
    frame2 = tk.LabelFrame(gui, width=400, height=42)
    frame2.pack(padx=10, pady=5)
    frame2.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Confirm button"
    confirm_button = tk.Button(frame2, text="Confirm Selection", command=lambda: confirm_selection())  # Create button executing function
    confirm_button.pack(padx=30, pady=5)

    "Generate a mainLoop to activate the gui"
    gui.mainloop()  # Run loop updating the window

    # Outputs of GUI ##########################################################

    "Output of GUI once closed"
    case_type = selected_case_type.get()

    if echo:
        print("\nThe selected case type is: ", case_type)

    return case_type


###############################################################################
###           Prompt user for building case characteristics                 ###
###############################################################################

def prompt_user_case_characteristics_building(echo=False):
    """
    Generate a GUI to prompt user for selecting filtering parameters that will
    be used to find all files corresponding to the selected type of building 
    cases.
    """

    # Initialize GUI ##########################################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change closing wnidow handling"
    def on_closing():
        """if closing the window, raise exception to be caught by error handler 
        to destroy the gui and raise the error to top level"""
        if mbox.askokcancel("ABORT", "Do you want to abort the DESTEST comparison procedure?"):
            raise Abort_exception("The user aborted the procedure.")

    gui.protocol("WM_DELETE_WINDOW", on_closing)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Select Building Case Characteristics")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("420x210+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    # Sub-function: confirm_selection #########################################

    "Confirm the selected filtering parameters and close the GUI window and return filtering codes"

    def confirm_selection():
        gui.destroy()  # Close the GUI window, the output will be returned

    # End Sub-function ########################################################

    # Sub-function: generate filtering code ###################################

    "Extract regular expression from the selected dropdown menu variables and generate the filtering code"

    def generate_filtering_code(selected_building_type, selected_building_year, selected_occupant_type):

        "Find the building_type_code in the selected_building_type"
        pattern = ("\[(.*?)\]")  # '\' to start the definition of the regular expression; (.*?) for including anything in between
        target_string = selected_building_type
        building_type_code = re.search(pattern, target_string).group(1)  # Wanted substring is in result group(1)

        "Find the building_year_code in the selected_building_year"
        pattern = ("\[(.*?)\]")  # '\' to start the definition of the regular expression; (.*?) for including anything in between
        target_string = selected_building_year
        building_year_code = re.search(pattern, target_string).group(1)  # Wanted substring is in result group(1)

        "Find the occupant_type_code in the selected_occupant_type"
        pattern = ("\[(.*?)\]")  # '\' to start the definition of the regular expression; (.*?) for including anything in between
        target_string = selected_occupant_type
        occupant_type_code = re.search(pattern, target_string).group(1)  # Wanted substring is in result group(1)

        "Create the filtering code to find the files in Github folder"
        filtering_code = (
            building_type_code
            + "_"
            + building_year_code
            + "_"
            + occupant_type_code
            + ".csv")
        
        parameter_file_name = (
            "parameters_DESTEST_"
            + building_type_code
            + "_"
            + building_year_code
            + "_"
            + occupant_type_code
            + ".txt")

        return filtering_code, parameter_file_name

    # End Sub-function ########################################################

    # Pack widgets and generate GUI ###########################################

    "Pack the different buttons and labels on the GUI window"

    "Frame 1"
    frame1 = tk.LabelFrame(gui, text="Building Case Characteristics for DESTEST Comparison", width=400, height=140)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Dropdown selection menu for building type"
    options_building_types = [
        "Single-Family Dwelling (version 1) [SFD_1]",
        "Office Building [???]"]

    selected_building_type = StringVar()
    selected_building_type.set(options_building_types[0])

    dropdown_building_type = tk.OptionMenu(frame1, selected_building_type, *options_building_types)
    dropdown_building_type.pack(padx=30, pady=(10, 5))

    "Dropdown selection menu for building year"
    options_building_year = [
        "1980 [1980s]",
        "2000 [2000s]",
        "2010 [2010s]"]

    selected_building_year = StringVar()
    selected_building_year.set(options_building_year[0])

    dropdown_building_year = tk.OptionMenu(frame1, selected_building_year, *options_building_year)
    dropdown_building_year.pack(padx=30, pady=(0, 5))

    "Dropdown selection menu for occupant type"
    options_occupant_type = [
        "1 [1]",
        "2 [2]",
        "3 [3]",
        "4 [4]",
        "5 [5]",
        "6 [6]",
        "7 [7]",
        "8 [8]",
        "9 [9]",
        "10 [10]",
        "11 [11]",
        "12 [12]",
        "13 [13]",
        "14 [14]",
        "15 [15]",
        "16 [16]",
        "ISO [ISO]"]

    selected_occupant_type = StringVar()
    selected_occupant_type.set(options_occupant_type[16])

    dropdown_occupant_type = tk.OptionMenu(frame1, selected_occupant_type, *options_occupant_type)
    dropdown_occupant_type.pack(padx=30, pady=0)

    "Frame 2"
    frame2 = tk.LabelFrame(gui, width=400, height=42)
    frame2.pack(padx=10, pady=0)
    frame2.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Confirm button"
    confirm_button = tk.Button(frame2, text="Confirm Selections", command=lambda: confirm_selection())  # Create button executing function
    confirm_button.pack(padx=30, pady=5)

    "Generate a mainLoop to activate the gui"
    gui.mainloop()  # Run loop updating the window

    # Outputs of GUI ##########################################################

    "Output of GUI once closed"
    filtering_code, parameter_file_name = generate_filtering_code(
        selected_building_type.get(),
        selected_building_year.get(),
        selected_occupant_type.get())

    if echo:
        print(
            "\nThe selected filtering parameters are:\n",
            selected_building_type.get(),
            "\n",
            selected_building_year.get(),
            "\n",
            selected_occupant_type.get())
        print("\n The data file filtering code is:" + filtering_code)
        print("\n The parameter file name is:" + parameter_file_name)

    return filtering_code, parameter_file_name


###############################################################################
###            Prompt user for network case characteristics                 ###
###############################################################################

def prompt_user_case_characteristics_network(echo=False):
    """
    Generate a GUI to prompt user for selecting filtering parameters that will
    be used to find all files corresponding to the selected type of network 
    cases.
    """

    # Initialize GUI ##########################################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change closing wnidow handling"
    def on_closing():
        """if closing the window, raise exception to be caught by error handler 
        to destroy the gui and raise the error to top level"""
        if mbox.askokcancel("ABORT", "Do you want to abort the DESTEST comparison procedure?"):
            raise Abort_exception("The user aborted the procedure.")

    gui.protocol("WM_DELETE_WINDOW", on_closing)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Select Network Case Characteristics")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("420x130+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    # Sub-function: confirm_selection #########################################

    "Confirm the selected filtering parameters and close the GUI window and return filtering codes"

    def confirm_selection():
        gui.destroy()  # Close the GUI window, the output will be returned

    # End Sub-function ########################################################

    # Sub-function: generate filtering code ###################################

    "Extract regular expression from the selected dropdown menu variables and generate the filtering code"

    def generate_filtering_code(selected_network_type):

        "Find the building_type_code in the selected_network_type"
        pattern = ("\[(.*?)\]")  # '\' to start the definition of the regular expression; (.*?) for including anything in between
        target_string = selected_network_type
        network_type_code = re.search(pattern, target_string).group(1)  # Wanted substring is in result group(1)

        "Create the filtering code to find the files in Github folder"
        filtering_code = network_type_code + ".csv"
        parameter_file_name = "parameters_DESTEST_" + network_type_code + ".txt"

        return filtering_code, parameter_file_name

    # End Sub-function ########################################################

    # Pack widgets and generate GUI ###########################################

    "Pack the different buttons and labels on the GUI window"

    "Frame 1"
    frame1 = tk.LabelFrame(gui, text="Network Case Characteristics for DESTEST Comparison", width=400, height=60)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Dropdown selection menu for building type"
    options_network_types = [
        "Exercise 1 [Network_1]",
        "Exercise 2 [Network_2]"]

    selected_network_type = StringVar()
    selected_network_type.set(options_network_types[0])

    dropdown_building_type = tk.OptionMenu(frame1, selected_network_type, *options_network_types)
    dropdown_building_type.pack(padx=30, pady=(5, 10))

    "Frame 2"
    frame2 = tk.LabelFrame(gui, width=400, height=42)
    frame2.pack(padx=10, pady=0)
    frame2.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Confirm button"
    confirm_button = tk.Button(frame2, text="Confirm Selections", command=lambda: confirm_selection())  # Create button executing function
    confirm_button.pack(padx=30, pady=5)

    "Generate a mainLoop to activate the gui"
    gui.mainloop()  # Run loop updating the window

    # Outputs of GUI ##########################################################

    "Output of GUI once closed"
    filtering_code, parameter_file_name = generate_filtering_code(selected_network_type.get())

    if echo:
        print("\nThe selected filtering parameters are:\n", selected_network_type.get())
        print("\n The data file filtering code is:" + filtering_code)
        print("\n The parameter file name is:" + parameter_file_name)

    return filtering_code, parameter_file_name


###############################################################################
###                            Extract parameters                           ###
###############################################################################

def load_parameters(
    server_info,
    parameter_file_name,
    list_implemented_KPIs,
    list_parameters_to_find,
    echo=False):
    """Define a parameter class and populate it with the different parameters
    extracted from the parameter file"""

    # Initialize GUI ##########################################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    "Change closing wnidow handling"
    def no_closing():
        pass  # Does nothing if window is closed by user

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.
    gui.protocol("WM_DELETE_WINDOW", no_closing)

    "Change the window properties"
    gui.title("Loading")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("400x80+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    "Frame 1"
    frame1 = tk.LabelFrame(gui, width=400, height=70)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Display message as label on GUI"
    my_label = tk.Label(frame1, text="Loading DESTEST parameters: Please wait.")  # Pack the name of the file on the window
    my_label.pack()

    "Init progess bar"
    progress = Progressbar(frame1, orient=HORIZONTAL, length=200, mode="determinate")  # New horizontal progress bar in determinate (normal) mode
    progress.pack(pady=5)
    progress["value"] = 5
    gui.update_idletasks()

    # Sub-function: check validity parameter file #############################

    "Verify that the selected file has appropriate data content"

    def check_validity_parameter_file(
        file_path_and_name,
        list_implemented_KPIs,
        server_info,
        list_parameters_to_find,
        echo=False):

        "Init empty validity vector"
        validity_vect = []  # Empty vector to store all results from the validity tests
        validity_file = False  # By default the file is not valid until proven otherwise

        "Init empty full path and name file"
        full_path_and_name_file = ""

        if echo:
            print("\nStart validity test of parameter file")

        "Extract file data for inspection"
        try:
            "Create full path for parameter file"
            full_path_and_name_file = get_full_path_to_online_file(
                file_path_and_name, server_info, echo)

            "Load the file into df"
            df = pd.read_csv(full_path_and_name_file, sep="\t", header=None)
            list_parameters_name = pd.Series.tolist(df.iloc[:, 0])
            list_parameters_value = pd.Series.tolist(df.iloc[:, 1])
            if echo:
                print("\nData found in the file:")
                print(df)

        except:
            print("\nThe selected file cannot be read correctly.\nThe selected file is not valid.")
            return validity_file, full_path_and_name_file

        try:
            "First, check that right length list in parameter file df"
            test_result = len(list_parameters_to_find) == len(list_parameters_name) and len(list_parameters_to_find) == len(list_parameters_value)
            validity_vect.append(test_result)

            "Find each element of list_parameters_to_find in list_parameters_name"
            "and check that the corresponding parameter is not empty str or NaN"
            for index, parameter in enumerate(list_parameters_to_find):
                test_result = (
                    parameter in list_parameters_name
                    and list_parameters_value[index] != ""
                    and str(list_parameters_value[index]) != "nan")
                validity_vect.append(test_result)

            "Check that the list of column names has same length as number of data columns"
            index = list_parameters_name.index("list of column names:")
            list_column_names = list_parameters_value[index]  # Raw data string
            list_column_names = list_column_names.split(",")  # Split by comma and place in a list

            index = list_parameters_name.index("number of data columns:")
            nbr_data_column = list_parameters_value[index]  # Raw data string
            nbr_data_column = int(nbr_data_column)

            test_result = len(list_column_names) == nbr_data_column
            validity_vect.append(test_result)

            "Check that the list of KPIs is valid, i.e. they are all from the list of implemented KPIs"
            index = list_parameters_name.index("list of default KPIs:")
            list_KPIs = list_parameters_value[index]  # Raw data string
            list_KPIs = list_KPIs.split(",")  # Split by comma and place in a list
            test_result = all(elem in list_implemented_KPIs for elem in list_KPIs)
            validity_vect.append(test_result)

            "Check that length list KPIs is same as list KPI_weights"
            index = list_parameters_name.index("list of default KPI_weights:")
            list_KPI_weights = list_parameters_value[index]  # Raw data string
            list_KPI_weights = list_KPI_weights.split(",")  # Split by comma and place in a list
            test_result = len(list_KPI_weights) == len(list_KPIs)
            validity_vect.append(test_result)

            "Check that all elements in list KPI_weights are floats and larger than 0"
            try:
                test_result = all(
                    np.array(list(map(float, list_KPI_weights))) > 0)  # Check if all elements in converted list are greater than 0
            except:  # if the list is not only float or int, there will be an error raised
                test_result = False
                print("error test")
            finally:
                validity_vect.append(test_result)

            "Check that start date time is a datetime.datetime type"
            index = list_parameters_name.index("start date time:")
            start_date_time = list_parameters_value[index]  # Raw data string
            try:
                start_date_time = np.datetime64(start_date_time).astype(datetime)  # Try to convert into datetime format
                test_result = type(start_date_time) == datetime
            except:  # not a proper datetime input, there will be an error
                test_result = False
                print("error test")
            finally:
                validity_vect.append(test_result)

            "Check that the list typical days is not empty"
            index = list_parameters_name.index("list typical days:")
            list_typical_days = list_parameters_value[index]  # Raw data string
            list_typical_days = list_typical_days.split(",")  # Split by comma and place in a list
            test_result = len(list_typical_days) > 0
            validity_vect.append(test_result)

            "Finally, check that all validity tests are True"
            validity_file = all(validity_vect)  # AND operator on all list elements

        except:
            validity_file = False

        if echo:
            if validity_file:
                print("\nThe selected file is valid")
            else:
                print("\nThe selected file is not valid")
                print("Validity test vector: ", validity_vect)

        return validity_file, full_path_and_name_file

    # End sub-function ########################################################

    # Sub-function: get file path and name parameter file #####################

    "Find the path of the parameter file corresponding to the file code"

    def find_path_parameter_file(server_info, parameter_file_name, echo=False):

        "Get list of all the files in the target folder"
        try:
            url = server_info.url  # Get url from server info input
            r = requests.get(url)  # Get information from url
            res = r.json()  # Get json structure information

            list_txt_files_in_online_folder = []  # Init empty list

            for file in res["tree"]:  # Get all the tree (files)
                file_sub_path = file["path"]  # Get path of the file
                if (".txt" in file_sub_path):  # Check if .txt (the only valid ones for parameter files)
                    list_txt_files_in_online_folder.append(file_sub_path)

            if len(list_txt_files_in_online_folder) == 0:
                if echo:
                    print("\nNo file could be found in the online folder.\n")
                raise Exception("No file could be found in the online folder.")

            else:
                if echo:
                    print("\nList of valid txt files among which looking for parameter file:\n")
                    print(list_txt_files_in_online_folder)
        except:
            raise

        "Find the exact parameter file in the folder"
        try:
            list_parameter_files = list(filter(lambda k: parameter_file_name in k, list_txt_files_in_online_folder))

            if len(list_parameter_files) == 0:
                if echo:
                    print("\nThe parameter file could not be found in the online folder.")
                raise Exception("The parameter file could not be found in the online folder.")

            elif len(list_parameter_files) > 1:
                if echo:
                    print("\nMultiple similar parameter files found in the online folder.")
                raise Exception("Multiple similar parameter files found in the online folder.")

            else:
                file_path_and_name = list_parameter_files[0]
                if echo:
                    print("\nThe name of the parameter file is:\n", file_path_and_name)
        except:
            raise

        return file_path_and_name

    # End sub-function ########################################################

    # Main ####################################################################

    "Get parameter file from online folder"
    try:
        file_path_and_name = find_path_parameter_file(server_info, parameter_file_name, echo)
    except:
        gui.destroy()
        raise Exception("The parameter file could not be found in the online folder.")

    "Verify validity selected file"
    try:
        validity_file, full_path_and_name_file = check_validity_parameter_file(
            file_path_and_name,
            list_implemented_KPIs,
            server_info,
            list_parameters_to_find,
            echo)
        if not validity_file:
            gui.destroy()
            raise Exception("The parameter file is not valid.")

    except:
        raise
        gui.destroy()

    try:
        "Load parameters file and extract data"
        df_parameters = pd.read_csv(full_path_and_name_file, sep="\t", header=None)
        print(df_parameters)

        "Update progress bar"
        progress["value"] = 10
        gui.update_idletasks()

        "Parameters from the parameter file"
        index = df_parameters[df_parameters[0] == "number of data columns:"].first_valid_index()
        nbr_data_column = int(df_parameters.iloc[index, 1])  # Convert into integer

        "Update progress bar"
        progress["value"] = 20
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "length header data files (number of lines):"].first_valid_index()
        header_length = int(df_parameters.iloc[index, 1])  # Convert into integer

        "Update progress bar"
        progress["value"] = 30
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "first data line (line number):"].first_valid_index()
        first_line_data = int(df_parameters.iloc[index, 1])  # Convert into integer

        "Update progress bar"
        progress["value"] = 40
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "number of data rows:"].first_valid_index()
        nbr_data_rows = int(df_parameters.iloc[index, 1])  # Convert into integer

        "Update progress bar"
        progress["value"] = 50
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "list of column names:"
        ].first_valid_index()
        list_column_names = df_parameters.iloc[index, 1]  # Raw data string
        list_column_names = list_column_names.split(",")  # Split by comma and place in a list

        "Update progress bar"
        progress["value"] = 60
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "list of default KPIs:"].first_valid_index()
        list_default_KPIs = df_parameters.iloc[index, 1]  # Raw data string
        list_default_KPIs = list_default_KPIs.split(",")  # Split by comma and place in a list

        "Update progress bar"
        progress["value"] = 70
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "list of default KPI_weights:"].first_valid_index()
        list_default_KPI_weights = df_parameters.iloc[index, 1]  # Raw data string
        list_default_KPI_weights = list_default_KPI_weights.split(",")  # Split by comma and place in a list
        list_default_KPI_weights = list(map(float, list_default_KPI_weights))  # Convert list of str into list of float

        "Update progress bar"
        progress["value"] = 80
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "sampling time interval [sec]:"].first_valid_index()
        sampling_time = int(df_parameters.iloc[index, 1])  # Convert into integer

        "Update progress bar"
        progress["value"] = 90
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "start date time:"].first_valid_index()
        start_date_time = df_parameters.iloc[index, 1]  # Raw data string
        start_date_time = np.datetime64(start_date_time).astype(datetime)  # Try to convert into datetime format

        "Update progress bar"
        progress["value"] = 95
        gui.update_idletasks()

        index = df_parameters[df_parameters[0] == "list typical days:"].first_valid_index()
        list_typical_days = df_parameters.iloc[index, 1]  # Raw data string
        list_typical_days = list_typical_days.split(",")  # Split by comma and place in a list

        "Load parameters into parameters class"
        parameters.nbr_data_column = nbr_data_column
        parameters.header_length = header_length
        parameters.first_line_data = first_line_data
        parameters.nbr_data_rows = nbr_data_rows
        parameters.list_column_names = list_column_names
        parameters.list_default_KPIs = list_default_KPIs
        parameters.list_default_KPI_weights = list_default_KPI_weights
        parameters.sampling_time = (sampling_time)  # [sec] Time interval in between 2 consecutive measurement points
        parameters.start_date_time = start_date_time  # Type Datetime
        parameters.list_typical_days = (list_typical_days)  # Only date stamp without time stamp

        "Update progress bar"
        progress["value"] = 100
        gui.update_idletasks()
        time.sleep(1)  # Pause time just for visibility

        # Output of the GUI ###################################################
    except:
        raise Exception("The parameters could not be loaded correctly.")
        gui.destroy()

    else:
        full_path_file_parameter_file = full_path_and_name_file
        gui.destroy()
        return parameters, full_path_file_parameter_file


###############################################################################
###                  Check validity of online DESTEST folder                ###
###############################################################################


def check_validity_DESTEST_folder(filtering_code, parameters, server_info, echo=False):
    """
    Generate a GUI to display the progression bar while validity of DESTEST folder is tested.
    It is checked that at least 1 file is valid.
    """
    # Initialize and generate GUI #############################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Checking validity")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("400x80+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    "Frame 1"
    frame1 = tk.LabelFrame(gui, width=400, height=70)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Display message as label on GUI"
    my_label = tk.Label(frame1, text="Checking validity online DESTEST repository: Please wait.")  # Pack the name of the file on the window
    my_label.pack()

    "Init progess bar"
    progress = Progressbar(frame1, orient=HORIZONTAL, length=200, mode="determinate")  # New horizontal progress bar in determinate (normal) mode
    progress.pack(pady=5)
    progress["value"] = 0
    gui.update_idletasks()

    "Initialize local variables"
    df_valid = pd.DataFrame()
    validity_folder = False

    # Sub-function: get path and name DESTEST data files #######################

    "Find the path of the parameter file corresponding to the file code"

    def find_path_filtered_data_files(server_info, filtering_code, echo=False):

        "Get list of all the files in the target folder"
        try:
            url = server_info.url  # Get url from server info input
            r = requests.get(url)  # Get information from url
            res = r.json()  # Get json structure information

            list_files_in_online_folder = []  # Init empty list

            for file in res["tree"]:  # Get all the tree (files)
                file_sub_path = file["path"]  # Get path of the file
                if ".csv" in file_sub_path:  # Check if .csv file (the only valid ones)
                    list_files_in_online_folder.append(file_sub_path)

            if len(list_files_in_online_folder) == 0:
                if echo:
                    print("\nNo file could be found in the online folder.\n")
                raise Exception("No file could be found in the online folder.")

            else:
                if echo:
                    print("\nList of valid  files among which looking for data files:\n")
                    print(list_files_in_online_folder)
        except:
            raise

        "Find the targeted data files in the folder"
        try:
            list_filtered_data_files = list(filter(lambda k: filtering_code in k, list_files_in_online_folder))

            if len(list_filtered_data_files) == 0:  # No data files in the repository
                if echo:
                    print("\nNo data files could be found in the online repository.")

            else:
                if echo:
                    print("\nThe filtered data files are:\n", list_filtered_data_files)
        except:
            raise

        return list_filtered_data_files

    # End sub-function ########################################################

    # Sub-function: check_validity_repository #################################

    "Verify that the selected file has appropriate data content"

    def check_validity_repository(filtering_code, parameters, server_info, echo=False):

        """loop through all files in the folder, try to open them and check
        validity until finding at least 1 file valid to then allow validity.
        """

        if echo:
            print("\nStart validity test of DESTEST online repository.")

        "Init output variables"
        validity_folder = False
        list_filtered_data_files = []
        valid_file_full_path_urll = ""
        number_files = 0
        df = pd.DataFrame()

        "Get list of files of subfolders in the folder"
        try:
            "List of data files corresponding to the filtering code"
            list_filtered_data_files = find_path_filtered_data_files(
                server_info, filtering_code, echo)

            if len(list_filtered_data_files) == 0:  # No data files in the repository
                raise Exception("No data files could be found in the online repository.")  # Get out of the function

        except:
            validity_folder = False
            list_filtered_data_files = []
            return (
                validity_folder,
                df,
                list_filtered_data_files,
                number_files,
                valid_file_full_path_urll)

        else:  # If some files, then start looping validity tests
            number_files = len(list_filtered_data_files)
            if echo:
                print("\n", number_files, " filtered files have been found.")

            "Loop through filtered list of files to find at least one valid file"
            for index, f in enumerate(list_filtered_data_files):
                validity_file = False

                try:
                    "Create full path for parameter file"
                    full_path_and_name_file = get_full_path_to_online_file(f, server_info, echo)

                    df = pd.read_csv(
                        full_path_and_name_file,
                        sep=",",
                        header=None,
                        skiprows=parameters.first_line_data - 1)

                    "Rename the columns of the dataframe"
                    df.columns = parameters.list_column_names

                except:
                    if echo:
                        print(index)
                        print("File ", f, " cannot be read correctly.")
                else:
                    if echo:
                        print(index)
                        print("File: ", f, " can be read correctly.")

                    try:  # Validity test of the data in the file
                        validity_vect = []  # Empty vector to store all results from the validity tests

                        "Check if any NaN in the data file"
                        test_result = df.isnull().sum().sum() == 0
                        validity_vect.append(test_result)

                        "Check right number of data columns"
                        test_result = len(df.columns) == parameters.nbr_data_column
                        validity_vect.append(test_result)

                        "Check right number of data rows"
                        test_result = len(df) == parameters.nbr_data_rows
                        validity_vect.append(test_result)

                        "Check that sampling time is correct in all elapsed time column"
                        sub_df = pd.Series.tolist(df.iloc[:, 0])  # Get the first column containing the elapsed time
                        sub_df1 = sub_df[1:]  # From second element to the last one
                        sub_df2 = sub_df[0:-1]  # From first element to the one before the last one
                        delta_df = list(np.array(sub_df1) - np.array(sub_df2))
                        test_result = (len(set(delta_df)) == 1)  # Check that the length of the set (list of unique elements in a list) is equal to 1
                        validity_vect.append(test_result)

                        "Finally, check that all validity tests are True"
                        validity_file = all(validity_vect)  # AND operator on all list elements

                    except:
                        validity_file = False

                finally:
                    if validity_file:  # The first valid file has been found and thus stop the loop and ends the function with return
                        if echo:
                            print("File ", f, " is valid.")

                        validity_folder = True
                        valid_file_full_path_urll = full_path_and_name_file

                        progress["value"] = 100
                        gui.update_idletasks()
                        time.sleep(1)

                        return (
                            validity_folder,
                            df,
                            list_filtered_data_files,
                            number_files,
                            valid_file_full_path_urll)

                    else:  # If hte current file is not valid then loop to the next one in line
                        if echo:
                            print("File ", f, " is not valid.")

                        "Update progress bar"
                        progress["value"] = 100 * (index + 1) / number_files
                        gui.update_idletasks()

        "Reset progress bar"
        progress["value"] = 100
        gui.update_idletasks()
        time.sleep(1)

        return (
            validity_folder,
            df,
            list_filtered_data_files,
            number_files,
            valid_file_full_path_urll)  # The file return of the function if reached only if no valid file have been found in the selected folder

    # End sub-function ########################################################

    # Sub-function: Format valid  df ##########################################
    
    "Add time stamp column to the df_valid"

    def format_valid_df(df, parameters, echo=False):

        if echo:
            print("\nFormat the df of the valid data file that has been found in the online repository.\n")

        # Parameters ##########################################################

        start = parameters.start_date_time
        end = start + timedelta(seconds=(parameters.sampling_time * (parameters.nbr_data_rows - 1)))
        time_step_sec = parameters.sampling_time  # [sec]

        # Sub-Sub Function: Generate time stamp ###############################
        
        def datetime_range(start, end, delta):
            current = start
            if not isinstance(delta, timedelta):
                delta = timedelta(**delta)

            while not current > end:  # goes until the end, including the end range
                yield current
                current += delta

        # End of Sub-sub function #############################################

        output_list = []

        # this unlocks the following interface:
        for dt in datetime_range(start, end, {"seconds": time_step_sec}):  # Generate the list of time stamps
            output_list.append(dt)

        formated_list = pd.to_datetime(output_list)

        if echo:
            print(formated_list)

        "Create a new df to be added to the valid_df to add the time stamp column"
        new_df = pd.DataFrame(formated_list, columns=["Date and Time"])  # Assign name to the column header in the new df

        "Concatenate the new_df and the valid df"
        frames = [new_df, df]  # The 2 df to concat
        df_valid = pd.concat(frames, axis=1, join="outer")  # Concat columns

        if echo:
            print("\nThe formated df of the first file found in the online repository is:\n")
            print(df_valid)

        return df_valid

    # End Sub-function ########################################################

    # Main ####################################################################

    try:
        validity_folder, df, list_filtered_data_files, number_files, valid_file_full_path_urll = check_validity_repository(
            filtering_code, parameters, server_info, echo)

    except:
        gui.destroy()
        raise

    else:
        # Outputs of GUI ######################################################

        if validity_folder:
            "Make df_valid for output: add time stamp column"
            df_valid = format_valid_df(df, parameters, echo)

            message = (
                "Valid data has been found in the online DESTEST repository among the "
                + str(number_files)
                + " files.")
            if echo:
                print("\n", message)
            mbox.showinfo("Success", message)
            gui.destroy()
            return (
                validity_folder,
                df_valid,
                list_filtered_data_files,
                valid_file_full_path_urll)  # change it with the right column names according to parameters
        else:
            message = (
                "No valid data has been found in the online DESTEST repository among the "
                + str(number_files)
                + " files.")
            if echo:
                print("\n", message)
            mbox.showerror("Error", message)
            gui.destroy()
            return (
                validity_folder,
                df_valid,
                list_filtered_data_files,
                valid_file_full_path_urll)  # change it with the right column names according to parameters


###############################################################################
###                           Load DESTEST data                             ###
###############################################################################

def load_DESTEST_data(
    list_filtered_data_files,
    filtering_code,
    server_info,
    parameters,
    df_valid,
    echo=False):
    """loop through all files in the folder, try to open them and check
    validity and load them into dataframe if valid.
    """
    # Initialize and generate GUI #############################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Loading data")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("400x80+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    "Frame 1"
    frame1 = tk.LabelFrame(gui, width=400, height=70)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Display message as label on GUI"
    my_label = tk.Label(frame1, text="Loading DESTEST data: Please wait.")  # Pack the name of the file on the window
    my_label.pack()

    "Init progess bar"
    progress = Progressbar(frame1, orient=HORIZONTAL, length=200, mode="determinate")  # New horizontal progress bar in determinate (normal) mode
    progress.pack(pady=5)
    progress["value"] = 0
    gui.update_idletasks()

    # Main ####################################################################

    if echo:
        print("\nStart loading DESTEST data files.")

    "Init output df with all DESTEST data"
    df_DESTEST_data = df_valid.iloc[:, 0:2]  # Select all lines of 1st and 2nd column of a valid df: time stamp and time in sec

    if echo:
        print("\nStarting df_DESTEST_data is:\n")
        print(df_DESTEST_data)

    "Init successful loaded data index"
    successful_loaded_data_index = 0

    "Init successful loaded datasets"
    list_DESTEST_cases = []

    number_files = len(list_filtered_data_files)

    if echo:
        print(
            "\n",
            number_files,
            " data files corresponding to the case characteristics are present in the online DESTEST repository.")

    "Loop through files"
    for index, f in enumerate(list_filtered_data_files):

        validity_file = False

        if echo:
            print(index + 1)
            print(f)
            print("\n The files will be tested for validity and loaded if valid.")

        try:
            "Create full path for parameter file"
            full_path_and_name_file = get_full_path_to_online_file(f, server_info, echo)

            df = pd.read_csv(
                full_path_and_name_file,
                sep=",",
                header=None,
                skiprows=parameters.first_line_data - 1)

            "Rename the columns of the dataframe"
            df.columns = parameters.list_column_names

        except:
            if echo:
                print("File ", f, " cannot be read correctly.\nThe file is not valid.")

        else:
            if echo:
                print("File: ", f, " can be read correctly.")

            try:  # Validity test of the data in the file
                validity_vect = []  # Empty vector to store all results from the validity tests

                "Check if any NaN in the data file"
                test_result = df.isnull().sum().sum() == 0
                validity_vect.append(test_result)

                "Check right number of data columns"
                test_result = len(df.columns) == parameters.nbr_data_column
                validity_vect.append(test_result)

                "Check right number of data rows"
                test_result = len(df) == parameters.nbr_data_rows
                validity_vect.append(test_result)

                "Check that sampling time is correct in all elapsed time column"
                sub_df = pd.Series.tolist(df.iloc[:, 0])  # Get the first column containing the elapsed time
                sub_df1 = sub_df[1:]  # From second element to the last one
                sub_df2 = sub_df[0:-1]  # From first element to the one before the last one
                delta_df = list(np.array(sub_df1) - np.array(sub_df2))
                test_result = (len(set(delta_df)) == 1)  # Check that the length of the set (list of unique elements in a list) is equal to 1
                validity_vect.append(test_result)

                "Finally, check that all validity tests are True"
                validity_file = all(validity_vect)  # AND operator on all list elements

            except:
                validity_file = False

        finally:  # Check validity of the file
            if validity_file:  # The file is valid
                if echo:
                    print("File ", f, " is valid.")

                try:  # try to add the df data to DESTEST data

                    "Generate column names for new df with parameters and sufix from file name"
                    if (".csv" in f):  # In principle, redundant because only .csv can make it to the list_filtered_data_files
                        "remove filtering code and parent folders from name of the file"
                        full_string = f
                        target_prefix = "/"
                        target_sufix = "_" + filtering_code

                        list_occ = [m.start() for m in re.finditer(target_prefix, full_string)]  # Get all occurrences of the prefix

                        substring = full_string[list_occ[-1] + len(target_prefix) : full_string.rfind(target_sufix)]  # Start search from last occurrence of the prefix

                        name = substring  # The name of hte case is the substring extracted from in between prefix and sufix
                        sufix = " - " + name

                    else:
                        raise Exception("The file is corrupt and thus not valid.")

                    "Assign names to df columns"
                    df.columns = parameters.list_column_names

                    "Remove the time column from the new df that is in column 0"
                    df = df.drop([df.columns[0]], axis="columns")

                    "Add sufix to column names"
                    df = df.add_suffix(sufix)

                    "Concatenate new data from df to rest data in DESTEST data df (at the end)"
                    frames = [df_DESTEST_data, df]  # Make a list with the new df and the DESTEST df
                    df_DESTEST_data = pd.concat(frames, axis=1, join="outer")  # Concatenate new df with the all_data df

                except:  # error in loading into df
                    if echo:
                        print("Data loading failed")

                else:  # No error for loading data into DESTEST df
                    successful_loaded_data_index += 1
                    list_DESTEST_cases.append(name)

                    if echo:
                        print("Data loading completed")

            else:  # The file is not valid
                if echo:
                    print("File ", f, " is not valid.")

        "Update progress bar"
        progress["value"] = 100 * (index + 1) / number_files
        gui.update_idletasks()

    # End loop ###

    "Reset progress bar"
    progress["value"] = 100
    gui.update_idletasks()
    time.sleep(1)

    # Output ##################################################################

    "GUI loading output"
    "Check that at least 1 file has been successfully loaded"
    if (successful_loaded_data_index > 0 and successful_loaded_data_index == number_files):
        if echo:
            print("\nAll the DESTEST data has been correctly loaded:")
            print(df_DESTEST_data)

        message = (
            "All the DESTEST data has been successfully loaded from the DESTEST online repository:\n\n"
            + str(successful_loaded_data_index)
            + " files have been correctly loaded out of "
            + str(number_files)
            + " filtered files in the online DESTEST repository.")  # Give success rate of file loading
        mbox.showinfo("Success", message)

        gui.destroy()

        return df_DESTEST_data, list_DESTEST_cases

    elif (successful_loaded_data_index > 0 and successful_loaded_data_index < number_files):
        if echo:
            print("\nPart of the DESTEST data has been correctly loaded:")
            print(df_DESTEST_data)

        message = (
            "Part of the DESTEST data has been successfully loaded from the DESTEST online repository:\n\n"
            + str(successful_loaded_data_index)
            + " files have been correctly loaded out of "
            + str(number_files)
            + " filtered files in the online DESTEST repository.\n\n"
            + str(number_files - successful_loaded_data_index)
            + " files in the repository correspond to the selected "
            + str(filtering_code)
            + " case but are not valid.")  # Give success rate of file loading
        mbox.showinfo("Success", message)

        gui.destroy()

        return df_DESTEST_data, list_DESTEST_cases

    else:  # If no file has been successfully loaded, then raise an error
        if echo:
            print("\nNo DESTEST file from the online repository has been correctly loaded")

        gui.destroy()
        raise Exception("No DESTEST data has been correctly loaded")


###############################################################################
###                       Prompt user for user data file                    ###
###############################################################################

def prompt_user_for_user_data_file(
    parameters,
    server_info,
    full_path_file_parameter_file,
    filtering_code,
    valid_file_full_path_url,
    echo=False):
    """
    Generate a GUI to prompt user for a valid user test data file.
    Once a valid user test data file is found, the user can confirm selection.
    """
    
    # Initialize GUI ##########################################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change closing wnidow handling"

    def on_closing():
        """if closing the window, raise exception to be caught by error handler 
        to destroy the gui and raise the error to top level"""
        if mbox.askokcancel("ABORT", "Do you want to abort the DESTEST comparison procedure?"):
            raise Abort_exception("The user aborted the procedure.")

    gui.protocol("WM_DELETE_WINDOW", on_closing)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Select the user data file")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("420x357+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    "Initialize local variables"
    file_path_and_name = ""
    validity_file = False
    file_name_str_var = StringVar()  # String var to update the label on the gui
    file_name_str_var.set("No file selected")
    no_user_test = False

    # Sub-function: check_validity_file #######################################

    "Verify that the selected file has appropriate data content"
    def check_validity_file(file_path_and_name, parameters, echo=False):

        "Init progress bar"
        progress.pack(pady=5)
        progress["value"] = 10
        gui.update_idletasks()

        "Init empty validity vector"
        validity_vect = []  # Empty vector to store all results from the validity tests
        validity_file = False

        if echo:
            print("\nStart validity test of the user data file")

        "Extract file data for inspection"
        try:
            df = pd.read_csv(
                file_path_and_name,
                sep=",",
                header=None,
                skiprows=parameters.first_line_data - 1)

            "Update progress bar"
            progress["value"] = 20
            gui.update_idletasks()
            
        except:
            print("\nThe selected file cannot be read correctly.\nThe selected file is not valid.")
            progress.pack_forget()
            return validity_file
        
        else:  # Check validity of the file content

            if echo:
                print("\nData found in the file:")
                print(df)

            try:
                "Check if any NaN in the data file"
                test_result = df.isnull().sum().sum() == 0
                validity_vect.append(test_result)

                "Update progress bar"
                progress["value"] = 30
                gui.update_idletasks()

                "Check right number of data columns"
                test_result = len(df.columns) == parameters.nbr_data_column
                validity_vect.append(test_result)

                "Update progress bar"
                progress["value"] = 50
                gui.update_idletasks()

                "Check right number of data rows"
                test_result = len(df) == parameters.nbr_data_rows
                validity_vect.append(test_result)

                "Update progress bar"
                progress["value"] = 70
                gui.update_idletasks()

                "Check that sampling time is correct in all elapsed time column"
                sub_df = pd.Series.tolist(df.iloc[:, 0])  # Get the first column containing the elapsed time
                sub_df1 = sub_df[1:]  # From second element to the last one
                sub_df2 = sub_df[0:-1]  # From first element to the one before the last one
                delta_df = list(np.array(sub_df1) - np.array(sub_df2))
                test_result = (len(set(delta_df)) == 1)  # Check that the length of the set (list of unique elements in a list) is equal to 1
                validity_vect.append(test_result)

                "Update progress bar"
                progress["value"] = 85
                gui.update_idletasks()

                "Finally, check that all validity tests are True"
                validity_file = all(validity_vect)  # AND operator on all list elements

                "Update progress bar"
                progress["value"] = 100
                gui.update_idletasks()
                time.sleep(1)  # Pause time just for visibility

            except:
                progress.pack_forget()
                validity_file = False

        if echo:
            if validity_file:
                print("\nThe selected file is valid")
            else:
                print("\nThe selected file is not valid")
                print("Validity test vector: ", validity_vect)

        "Reset progress bar"
        progress["value"] = 0
        progress.pack_forget()
        gui.update_idletasks()

        return validity_file

    # End sub-function ########################################################

    # Sub-function: select_file ###############################################

    "Define the function to be executed by the select_file_button"

    def select_file(echo=False):

        "use nonlocal var so the function above gets the updated values of those vars"
        nonlocal file_path_and_name
        nonlocal validity_file

        try:
            "Ask to choose file and get full path"
            file_path_and_name = filedialog.askopenfilename(
                title="Select a data file",
                filetypes=(("text files", "*.txt"), ("csv files", "*.csv")))

            "Get just file name"
            head, file_name = ntpath.split(file_path_and_name)  # Split between head and tail of the full file path

            "Display name selected file"
            if file_name:
                file_name_str_var.set(file_name)  # Update the name of the file on the window
                gui.update_idletasks()

                if echo:
                    print("\nSelected file is: ", file_path_and_name)

                try:
                    "Verify validity selected file"
                    validity_file = check_validity_file(file_path_and_name, parameters, echo)

                except:
                    validity_file = False
                    
            else:
                file_name_str_var.set("No file selected")
                gui.update_idletasks()
                validity_file = False
        except:
            file_name_str_var.set("No file selected")
            gui.update_idletasks()
            validity_file = False

        "Enable confirm selection button is file is valid"
        if validity_file:
            confirm_file_button["state"] = "normal"  # Enable button
            mbox.showinfo("Success", "The selected file is valid")
        else:
            confirm_file_button["state"] = "disable"
            mbox.showerror("Error", "The selected file is not valid.")

        return

    # End Sub-function ########################################################

    # Sub-function: show data file format #####################################

    "Display relevant content of the parameter file corresponding to the selected case type"

    def show_data_file_format():
        message = (
            "Number of data columns in the file: "
            + str(parameters.nbr_data_column)
            + "\n"
            + "Length of the header data file (number of lines): "
            + str(parameters.header_length)
            + "\n"
            + "First data line (line number): "
            + str(parameters.first_line_data)
            + "\n"
            + "Number of data rows: "
            + str(parameters.nbr_data_rows)
            + "\n"
            + "List of column names: "
            + str(parameters.list_column_names)
            + "\n"
            + "Sampling time interval [sec]: "
            + str(parameters.sampling_time))
        mbox.showinfo("Valid format for the .txt or .csv data file", message)

    # End Sub-function ########################################################

    # Sub-function: download format data file #################################

    "Download the parameter file corresponding to the selected case type"

    def download_format_data_file(full_path_file_parameter_file):

        try:
            target_folder = filedialog.askdirectory(title="Select a folder to save the file")

            "Check if any folder path was selected"
            if target_folder:
                r = requests.get(full_path_file_parameter_file)  # Get content of the source file
                head, file_name = ntpath.split(full_path_file_parameter_file)  # Split between head and tail of the full file path
                new_file_path = (target_folder + "/" + file_name)  # Form the new file path with the same name as the original source file

                "Create the new file"
                with open(new_file_path, "wb") as file:  # "with" statement ensures proper acquisition and release of resources, it handles exception of the procedure, no need to file.close at the end
                    file.write(r.content)

            else:
                return

        except:
            mbox.showerror("Error", "Oups !\nSomething went wrong !")

    # End Sub-function ########################################################

    # Sub-function: download format data file #################################

    "Download the parameter file corresponding to the selected case type"

    def download_example_correct_data_file(valid_file_full_path_url):

        try:
            target_folder = filedialog.askdirectory(title="Select a folder to save the file")

            "Check if any folder path was selected"
            if target_folder:
                r = requests.get(valid_file_full_path_url)  # Get content of the source file
                head, file_name = ntpath.split(valid_file_full_path_url)  # Split between head and tail of the full file path
                new_file_path = (target_folder + "/" + file_name)  # Form the new file path with the same name as the original source file

                "Create the new file"
                with open(new_file_path, "wb") as file:  # "with" statement ensures proper acquisition and release of resources, it handles exception of the procedure, no need to file.close at the end
                    file.write(r.content)

            else:
                return

        except:
            mbox.showerror("Error", "Oups !\nSomething went wrong !")

    # End Sub-function ########################################################

    # Sub-function: confirm_selection #########################################

    "Confirm the selected file and close the GUI window and return file path"

    def confirm_selection():
        gui.destroy()  # Close the GUI window, the output will be returned

    # End Sub-function ########################################################

    # Sub-function: no_file_selection #########################################
        
    def no_file_selection():
        nonlocal no_user_test
        no_user_test = True
        gui.destroy()  # Close the GUI window, the output will be returned

    # Pack widgets and generate GUI ###########################################

    "Pack the different buttons and labels on the GUI window"

    "Frame 1"
    frame1 = tk.LabelFrame(
        gui,
        text="Select your own data file (.txt or .csv) for the DESTEST comparison",
        width=400,
        height=120)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Select file button"
    select_file_button = tk.Button(frame1, text="Select User Data File",
        command=lambda: select_file(echo))  # Create button executing function
    select_file_button.pack(pady=5)  # Pack the button that executes the command

    "Display name selected file in GUI label"
    my_label = tk.Label(frame1, textvariable=file_name_str_var)  # Pack the name of the file on the window
    my_label.pack(pady=5)

    "Frame 2"
    frame2 = tk.LabelFrame(gui, text="Get Help to Format User Test Data File", width=400, height=127)
    frame2.pack(padx=10, pady=(0, 10))
    frame2.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Data File Format button"
    show_data_file_format_button = tk.Button(
        frame2, text="Show Data File Format",
        command=lambda: show_data_file_format())  # Create button executing function
    show_data_file_format_button.pack(pady=5)

    "Download data file format button"
    download_format_data_file_button = tk.Button(
        frame2,
        text="Download Data File Format",
        command=lambda: download_format_data_file(full_path_file_parameter_file))  # Create button executing function
    download_format_data_file_button.pack(pady=5)

    "Download example correct data file button"
    download_example_correct_data_file_button = tk.Button(
        frame2,
        text="Download Example Correct Data File",
        command=lambda: download_example_correct_data_file(valid_file_full_path_url))  # Create button executing function
    download_example_correct_data_file_button.pack(pady=5)

    "Frame 3"
    frame3 = tk.LabelFrame(gui, width=400, height=88)
    frame3.pack(padx=10, pady=(0, 10))
    frame3.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Confirm selection button"
    confirm_file_button = tk.Button(
        frame3,
        text="Confirm Selection and Continue",
        command=lambda: confirm_selection())  # Create button executing function
    confirm_file_button.pack(pady=5)
    confirm_file_button["state"] = "disabled"

    "No test file button"
    no_file_button = tk.Button(
        frame3,
        text="Continue Without User Data File",
        command=lambda: no_file_selection())  # Create button executing function
    no_file_button.pack(pady=(0, 5))

    "Progess bar"
    progress = Progressbar(frame1, orient=HORIZONTAL, length=200, mode="determinate")  # New horizontal progress bar in determinate (normal) mode
    progress.pack_forget()

    "Generate a mainLoop to activate the gui"
    gui.mainloop()  # Run loop updating the window

    # Outputs of GUI ##########################################################

    "Output of GUI once closed"
    if no_user_test:
        file_path_and_name = "no file"
        return file_path_and_name, no_user_test
    elif validity_file:
        return (file_path_and_name, no_user_test)  # change it with the right column names according to parameters
    else:
        raise Exception("No valid user test data file has been selected")  # Raising an Exception to generate and error. No need return after raise


###############################################################################
###                        Load user test data file                         ###
###############################################################################

def load_user_test_data(user_test_data_file, parameters, no_user_test, echo=False):

    # Initialize and generate GUI #############################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "In the case of no user test data for DESTEST comparison"
    if no_user_test:  # No user test data
        message = "The DESTEST comparison will be conducted without user test data."
        gui.withdraw()
        mbox.showinfo("Warning", message)  # Popup message window
        gui.destroy()
        if echo:
            print("\n", message)
        df_user_test_data = pd.DataFrame()
        return df_user_test_data

    "Change the window properties"
    gui.title("Loading")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("400x80+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    "Frame 1"
    frame1 = tk.LabelFrame(gui, width=400, height=70)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Display message as label on GUI"
    my_label = tk.Label(frame1, text="Loading user test data: Please wait.")  # Pack the name of the file on the window
    my_label.pack()

    "Init progess bar"
    progress = Progressbar(frame1, orient=HORIZONTAL, length=200, mode="determinate")  # New horizontal progress bar in determinate (normal) mode
    progress.pack(pady=5)
    progress["value"] = 10
    gui.update_idletasks()

    # Main ####################################################################

    try:
        "Load data into dataframe"
        df_user_test_data = pd.read_csv(
            user_test_data_file,
            sep=",",
            header=None,
            skiprows=parameters.first_line_data - 1)

        "Update progress bar"
        progress["value"] = 50
        gui.update_idletasks()

        "Rename the columns of the dataframe"
        df_user_test_data.columns = parameters.list_column_names

        "Format Date and Time column"  # No need to convert here
        # df_user_test_data[parameters.list_column_names[0]] = pd.to_datetime(df_user_test_data[parameters.list_column_names[0]]) # Old version when datetime stamp were input in the file. Works for both - or / delimited dates followed by : delimited time

        "Update progress bar"
        progress["value"] = 100
        gui.update_idletasks()
        time.sleep(1)  # Pause time just for visibility

        # Output ##############################################################
    except:
        gui.destroy()
        raise Exception("The user test data could not be loaded correctly:")
    else:
        if echo:
            print("\nThe user test data has been correctly loaded:")
            print(df_user_test_data)

        mbox.showinfo("Success", "The user test data has been loaded")
        gui.destroy()
        return df_user_test_data


###############################################################################
###                         DESTEST KPIs selection                          ###
###############################################################################

def DESTEST_KPIs_selection(parameters, list_implemented_KPIs, echo=False):
    """
    Generate a GUI to prompt user for selecting KPIs and KPI weights for the 
    DESTEST comparison calculation.
    """

    # Initialize GUI ##########################################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change closing wnidow handling"

    def on_closing():
        """if closing the window, raise exception to be caught by error handler 
        to destroy the gui and raise the error to top level"""
        if mbox.askokcancel("ABORT", "Do you want to abort the DESTEST comparison procedure?"):
            raise Abort_exception("The user aborted the procedure.")

    gui.protocol("WM_DELETE_WINDOW", on_closing)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Select Key Performance Indicators (KPIs)")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("450x470+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    "Init GUI outputs with parameter values"
    list_KPIs = parameters.list_default_KPIs
    list_KPI_weights = parameters.list_default_KPI_weights

    # Sub-function: get_input_number ##########################################

    "Insert the input number from the user into the listbox"

    def add_new_KPI(echo=False):
        "use nonlocal var so the function above gets the updated values of those vars"
        nonlocal list_KPIs
        nonlocal list_KPI_weights

        try:
            "try to convert the KPI input string into a float to check that it is a float"
            new_KPI_weight = float(user_input_KPI_weight.get())

            "Check if the new KPI is already listed"
            already_listed = selected_new_KPI.get() in list_KPIs

            "Check validity of input number"
            if new_KPI_weight > 0:  # Check that new KPI weight is greater than 0
                if not already_listed:  # Check that the new KPI is not already listed
                    list_KPIs.append(selected_new_KPI.get())  # Add the new KPI to the end of the KPI list
                    list_KPI_weights.append(new_KPI_weight)  # Add the new KPI weight to the end of the weight list

                    "Update listbox KPIs and weights"
                    new_entry = (selected_new_KPI.get() + " weighted " + str(new_KPI_weight))
                    KPI_listbox.insert("end", new_entry)

                    if echo:
                        print(
                            "\nKPI added at the end of the list is:",
                            selected_new_KPI.get())
                        print(
                            "KPI weight added at the end of the list is:",
                            new_KPI_weight)
                        print("\nCurrent list KPIs:", list_KPIs)
                        print("Current list KPI weights:", list_KPI_weights)

                else:  # The new KPI is already listed
                    mbox.showerror(
                        "Error",
                        "This KPI is already listed in the list of selected KPIs for comparison !\nChoose another one.")
            else:  # The new KPI weight is not greater than 0
                mbox.showerror("Error", "The KPI weight must be larger than 0 !")

                "Reset value input Entry to default value"
                default_value_KPI_weight_input.set("1")
                frame2.update_idletasks()

        except ValueError:  # If the input is not a valid number
            mbox.showerror("Error", "The KPI weight is not a number !")

            "Reset value input Entry to default value"
            default_value_KPI_weight_input.set("1")
            frame2.update_idletasks()

        except:  # Something else went wrong
            mbox.showerror("Error", "This is not a valid input !")

            "Reset value input Entry to default value"
            default_value_KPI_weight_input.set("1")
            frame2.update_idletasks()

    # End Sub-function ########################################################

    # Sub-function: remove selected KPI #######################################

    'Remove the selected "anchor" KPI from the boxlist'

    def remove_selected_KPI(echo=False):

        "use nonlocal var so the function above gets the updated values of those vars"
        nonlocal list_KPIs
        nonlocal list_KPI_weights

        "Get data from the current selection"
        try:
            selected_KPI = KPI_listbox.get("anchor")
            index_selection = KPI_listbox.curselection()  # Returns a tuple
            index_selection = index_selection[0]  # Get the first element of the tuple as int
        except:
            if echo:
                print("Something wrong happened.")
        else:

            "Remove from listbox"
            try:
                KPI_listbox.delete("anchor")
            except:
                if echo:
                    print("Something wrong happened.")
            else:
                "Update list KPIs and weights"
                del list_KPIs[index_selection]
                del list_KPI_weights[index_selection]

                if echo:
                    print("\nRemoved KPI is:", selected_KPI)
                    print("At position index in the list:", index_selection)
                    print("\nCurrent list KPIs:", list_KPIs)
                    print("Current list KPI weights:", list_KPI_weights)

    # End Sub-function ########################################################

    # Sub-function: clear list KPIs

    "Clear list KPIs and list weigths and boxlist on the GUI"

    def clear_list_KPIs(echo=False):

        "use nonlocal var so the function above gets the updated values of those vars"
        nonlocal list_KPIs
        nonlocal list_KPI_weights

        try:
            "Clear the whole listbox"
            KPI_listbox.delete(0, "end")
        except:
            if echo:
                print("Something wrong happened.")
        else:
            "Replace lists with empty list"
            list_KPIs = []
            list_KPI_weights = []

            if echo:
                print("\nThe KPI list has been emptied entirely.")
                print("\nCurrent list KPIs:", list_KPIs)
                print("Current list KPI weights:", list_KPI_weights)

    # End Sub-function ########################################################

    # Sub-function: confirm_selection #########################################

    "Confirm the selected KPIs and close the GUI window and list KPIs"

    def confirm_selection(list_KPIs, echo=False):

        "Check that there is at least 1 KPI in the list of KPI and that list of KPI is same length as list weights"
        if len(list_KPIs) < 1:
            mbox.showerror(
                "Error",
                "The list of KPIs is empty.\nThere must be at least 1 KPI in the list to proceed.")
        else:
            gui.destroy()  # Close the GUI window, the output will be returned

    # End Sub-function ########################################################

    # Pack widgets and generate GUI ###########################################

    "Pack the different buttons and labels on the GUI window"

    "Frame 1"
    frame1 = tk.LabelFrame(
        gui,
        text="New KPI / Comparison Metric to Add: Choose from Dropdown Menu Below",
        width=430,
        height=70)
    frame1.pack(padx=10, pady=5)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Dropdown selection menu for KPIs"
    options_KPIs = list_implemented_KPIs

    selected_new_KPI = StringVar()
    selected_new_KPI.set(options_KPIs[0])

    dropdown_new_KPI = tk.OptionMenu(frame1, selected_new_KPI, *options_KPIs)
    dropdown_new_KPI.pack(padx=30, pady=(10, 5))

    "Frame 2"
    frame2 = tk.LabelFrame(
        gui,
        text="Grading Weight for the Above KPI / Comparison Metric to Be Added",
        width=430,
        height=60)
    frame2.pack(padx=10, pady=5)
    frame2.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Input user box for weight KPI"
    default_value_KPI_weight_input = StringVar(frame2, value="1")
    user_input_KPI_weight = tk.Entry(frame2, textvariable=default_value_KPI_weight_input, width=10)  # Init with default value
    user_input_KPI_weight.pack(pady=(10, 5))

    "Frame 3"
    frame3 = tk.LabelFrame(gui, width=430, height=115)
    frame3.pack(padx=10, pady=5)
    frame3.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Add new KPI button"
    add_new_KPI_button = tk.Button(
        frame3,
        text="Add the Above KPI / Comparison Metric to the List",
        command=lambda: add_new_KPI(echo))  # Create button executing function
    add_new_KPI_button.pack(padx=30, pady=5)

    "Remove selected KPI from the list"
    remove_KPI_button = tk.Button(
        frame3,
        text="Remove Selected KPI / Comparison Metric From the List",
        command=lambda: remove_selected_KPI(echo))  # Create button executing function
    remove_KPI_button.pack(padx=30, pady=5)

    "Clear the list of KPIs"
    clear_list_KPI_button = tk.Button(
        frame3,
        text="Clear the Entire KPI / Comparison Metric List",
        command=lambda: clear_list_KPIs(echo))  # Create button executing function
    clear_list_KPI_button.pack(padx=30, pady=5)

    "Frame 4"
    frame4 = tk.LabelFrame(
        gui,
        text="Current List of KPIs / Comparison Metrics for DESTEST Comparison",
        width=430,
        height=130)
    frame4.pack(padx=10, pady=5)
    frame4.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Create listbox to display current list of KPIs and weights"
    KPI_listbox = tk.Listbox(frame4, bg="lightgrey", width=50, height=120)
    KPI_listbox.pack(padx=10, pady=10)
    "Init listbox"
    for i, item in enumerate(list_KPIs):
        new_entry = item + " weighted " + str(list_KPI_weights[i])
        KPI_listbox.insert("end", new_entry)

    "Frame 5"
    frame5 = tk.LabelFrame(gui, width=430, height=42)
    frame5.pack(padx=10, pady=5)
    frame5.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Confirm button"
    confirm_button = tk.Button(
        frame5,
        text="Confirm Selections and Continue",
        command=lambda: confirm_selection(list_KPIs, echo))  # Create button executing function
    confirm_button.pack(padx=30, pady=5)

    "Starting information message"
    mbox.showinfo(
        "Recommendation",
        "You can change here the list of KPIs / Comparison Metrics and their respective grading weights that are used to perform the DESTEST comparison calculation.\nHowever, it is recommended to keep the default values that are already selected and proceed directly to the comparison calculation.")

    "Generate a mainLoop to activate the gui"
    gui.mainloop()  # Run loop updating the window

    # Outputs of GUI ##########################################################

    if echo:
        print("\nThe KPI selection GUI output is as follows.\nList KPIs:", list_KPIs)
        print("List KPI weights:", list_KPI_weights)

    return list_KPIs, list_KPI_weights


###############################################################################
###                     DESTEST comparison calculation                      ###
###############################################################################

def DESTEST_comparison_calculation(
    df_user_test_data,
    df_DESTEST_data,
    list_DESTEST_cases,
    parameters,
    no_user_test,
    list_KPIs,
    list_KPI_weights,
    dictionnary_KPI_functions,
    dictionnary_KPI_grade_system,
    echo=False):
    """Calculates the KPIs listed as input, Average, Minimum and Maximum
    of all measured parameters of the user test data compared to a reference
    profile built from the point-by-point average of all the loaded DESTEST data.
    Calculates the global error grade based on the KPI weights listed as input.
    """

    # Initialize and generate GUI #############################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Calculation")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("400x80+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    "Frame 1"
    frame1 = tk.LabelFrame(gui, width=400, height=70)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Display message as label on GUI"
    my_label = tk.Label(frame1, text="Performing DESTEST comparison calculation: Please wait.")  # Pack the name of the file on the window
    my_label.pack()

    "Init progess bar"
    progress = Progressbar(frame1, orient=HORIZONTAL, length=200, mode="determinate")  # New horizontal progress bar in determinate (normal) mode
    progress.pack(pady=5)
    progress["value"] = 0
    gui.update_idletasks()

    # Sub-function: Calculate reference profile ###############################

    def calculate_ref_profiles(df_DESTEST_data, parameters, echo=False):
        """Generate reference profiles (mean average) for all parameters and
        place into df """

        "Init output df"
        reference_df = df_DESTEST_data.iloc[:, 0:2]  # Select all lines of 1st and 2nd column of a valid df: time stamp and time in sec

        try:
            nbr_parameters_result = len(parameters.list_column_names) - 1
            list_parameters = parameters.list_column_names[1 : nbr_parameters_result + 1]  # get all parameters from 2nd and forward. 1st column name is elapsed time

            for p in list_parameters:
                df_all = df_DESTEST_data.loc[:, df_DESTEST_data.columns.str.contains(p + "*")]  # Select all columns that contains a parameter followed by anything in their column name
                df_mean = df_all.mean(axis=1)  # Average per row for all rows: It is a series
                df_mean = df_mean.to_frame()  # Convert from Series to DataFrame
                df_mean.columns = [p]  # Give corresponding parameter name to column df_mean

                if echo:
                    print(
                        "Data set used for reference profile of parameter "
                        + str(p)
                        + " is of size: "
                        + str(df_all.shape))
                    print(df_all)

                frames = [reference_df, df_mean]  # The 2 df to concat
                reference_df = pd.concat(frames, axis=1, join="outer")  # Add to right of reference_df

        except:
            raise
        else:
            if echo:
                print("\nThe reference DataFrame is:")
                print(reference_df)

            return reference_df

    # End Sub-function ########################################################

    # Sub-function: Calculate error grade #####################################

    def calculate_error_grade(
        df_result,
        list_DESTEST_cases,
        no_user_test,
        list_KPIs,
        list_KPI_weights,
        echo=False):
        """Calcualte the error grades and accuracy grades for all cases of the
        DESTEST and the user data and generate a df to be added to the result df

        The error grade is calculate as the weighted average of each sub-grades
        for each KPIs. Each sub-grade is calculated as linear interpolation between
        1 for the best KPI and 0 for the worst KPI. Best and Worst KPIs are determined
        based on the type of KPI (see KPI grading system dictionnary).
        The error grade is always normalized as percentages between 0-100%
        """
        if no_user_test:
            list_cases = (list_DESTEST_cases)  # Selections of columns for the error grade calculation
        else:
            list_cases = ["User Test"] + list_DESTEST_cases  # Selections of columns for the error grade calculation

        list_summary_metrics = ["Error grade [%]", "Accuracy grade [%]"]

        "Init error grade df"
        df_result_column_names = list(df_result.columns)
        df_error_grade = pd.DataFrame(columns=df_result_column_names)  # Create the column of an empty df
        new_df = pd.DataFrame(
            {
                df_result_column_names[0]: ["Summary"] * len(list_summary_metrics),
                df_result_column_names[1]: list_summary_metrics,
            })  # Make new df with repetitions of parameter and different metrics
        df_error_grade = pd.concat([df_error_grade, new_df], sort=False, ignore_index=True).fillna(0)  # Concat new df into error grade df and fill missing columns with 0

        sub_df_KPIs = df_result[df_result["KPI / Metric"].isin(list_KPIs)][list_cases + ["KPI / Metric"]]  # Select only metrics of interest (rows) and cases except reference, keep list corresponding KPIs at the end
        sub_df_KPIs.index = sub_df_KPIs["KPI / Metric"]  # Replace the index of the df by the corresponding KPI of each selected row
        sub_df_KPIs.drop("KPI / Metric", axis="columns", inplace=True)  # Drop the column with the KPIs

        sub_df_err_grades = (sub_df_KPIs.copy())  # Make a new df from the sub_df_KPIs: use .copy and not "=" otherwise only copy the pointer to the df
        sub_df_err_grades[:] = 0  # Fill it with zeros everywhere

        "Create extended list of KPI weights"
        factor = int(len(sub_df_KPIs) / len(list_KPI_weights))
        extented_list_KPI_weights = (list_KPI_weights * factor)  # Repeat n times the list of weights to fit the length of rows in the df (n = number of parameters)

        "Calculate error grade for each case and for each KPI"
        i = 0  # row index for KPI index in df
        for k, row in sub_df_KPIs.iterrows():  # Go through each row (KPI)

            grade_system = grading_system_selector(k)  # The name of the row (its index in the df) is the KPI. Use it to get select the grading system

            if grade_system == "best_zero":
                best = abs(row).min()  # The best is the closest to zero
                worst = abs(row).max()  # The worst is the furthest from zero

            elif grade_system == "best_highest":
                best = row.max()  # The best is the highest value
                worst = row.min()  # The worst is the lowest value

            elif grade_system == "best_lowest":
                best = row.min()  # The best is the lowest value
                worst = row.max()  # The worst is the highest value

            else:
                raise Exception("wrong grading system")

            for j, c in enumerate(row):  # Go through each case. "c" is current case KPI

                KPI_weight = extented_list_KPI_weights[i]

                if grade_system == "best_zero":
                    sub_df_err_grades.iloc[i, j] = KPI_weight * ((abs(c) - best) / (worst - best))  # iloc[line,column]

                elif grade_system == "best_highest":
                    sub_df_err_grades.iloc[i, j] = KPI_weight * ((best - c) / (best - worst))  # iloc[line,column]

                elif grade_system == "best_lowest":
                    sub_df_err_grades.iloc[i, j] = KPI_weight * ((c - best) / (worst - best))  # iloc[line,column]

                else:
                    raise Exception("wrong grading system")

            i = i + 1

        for i, c in enumerate(list_cases):  # Go through each case
            error_grade = (sub_df_err_grades[c].sum()) / (np.array(extented_list_KPI_weights).sum())  # Normalized Error grade
            df_error_grade.loc[(df_error_grade["KPI / Metric"] == list_summary_metrics[0]), c] = round(error_grade * 100, 2)
            df_error_grade.loc[(df_error_grade["KPI / Metric"] == list_summary_metrics[1]), c] = round(100 - error_grade * 100, 2)  # accuracy grade as reciprocal error grade

        if echo:
            print("Summary grades:")
            print(df_error_grade)

        return df_error_grade, sub_df_err_grades

    # End Sub-function ########################################################

    # Sub-function: init df result ############################################

    def init_df_result(parameters, full_list_cases, list_metrics, echo=False):
        "Init output df_result"
        "Get parameters from the parameters input"
        nbr_parameters_result = len(parameters.list_column_names) - 1
        list_parameters = parameters.list_column_names[1 : nbr_parameters_result + 1]  # get all parameters from 2nd and forward. 1st column name is elapsed time

        "Generate names of columns for the df result"
        df_result_column_names = ["Parameter"] + ["KPI / Metric"] + full_list_cases

        "Init new df for result df with those names"
        df_result = pd.DataFrame(columns=df_result_column_names)

        "Populate parameter and metric rows and init all results to 0"
        for p in list_parameters:  # Loop through measurement parameters
            new_df = pd.DataFrame(
                {
                    df_result_column_names[0]: [p] * len(list_metrics),
                    df_result_column_names[1]: list_metrics,
                })  # Make new df with repetitions of parameter and different metrics
            df_result = pd.concat([df_result, new_df], sort=False, ignore_index=True).fillna(0)  # Concat new df into result df and fill missing columns with 0

        if echo:
            print("\nInitialized df_result:\n")
            print(df_result)

        return df_result, list_parameters

    # End Sub-function ########################################################

    # Sub-function: KPI selector ##############################################

    def KPI_selector(argument, reference_vector, test_case_vector, date_and_time_stamp_vect):
        switcher = dictionnary_KPI_functions  # Create the switcher
        # Get the function from switcher dictionary
        function = switcher.get(argument, lambda: "Invalid KPI")  # The string "Invalid KPI" will be the default output
        # Execute the function
        return function(reference_vector, test_case_vector, date_and_time_stamp_vect)

    # End Sub-function ########################################################

    # Sub-function: grading system selector ###################################

    def grading_system_selector(argument):
        switcher = dictionnary_KPI_grade_system  # Create the switcher
        # Get the function from switcher dictionary
        result = switcher.get(argument, "Invalid grade system")  # The string "Invalid grade system" will be the default output
        # Execute the function
        return result

    # End Sub-function ########################################################

    # Main ####################################################################

    try:
        """General parameters"""
        basic_side_metrics = [
            "Minimum",
            "Maximum",
            "Average",
            "Standard Deviation"]  # Add classic metrics to the list of selected KPIs
        
        list_metrics = (list_KPIs + basic_side_metrics)  # Add classic metrics to the list of selected KPIs
        date_and_time_stamp_vect = df_DESTEST_data["Date and Time"]

        "Make full list of cases by adding reference and user test if any"
        if no_user_test:
            full_list_cases = ["Reference"] + list_DESTEST_cases
        else:
            full_list_cases = ["User Test"] + ["Reference"] + list_DESTEST_cases

        "Init output df_result"
        df_result, list_parameters = init_df_result(parameters, full_list_cases, list_metrics, echo)

        "Update progress bar"
        progress["value"] = 10
        gui.update_idletasks()

        "Calculate reference profile"
        reference_df = calculate_ref_profiles(df_DESTEST_data, parameters, echo)

        "Update progress bar"
        progress["value"] = 20
        gui.update_idletasks()

        """"Looping through parameters, inside which looping through cases 
        (including user test and reference) in which looping through metrics 
        (including min, max, average)"""

        for i, p in enumerate(list_parameters):  # Loop through measurement parameters

            "Select the reference profile vector for the right parameter"
            reference_vector = reference_df[p]

            if echo:
                print("\nReference vector for ", p)
                print(reference_vector)

            for j, c in enumerate(full_list_cases):  # Loop through column cases

                if c == "Reference":  # If it is the reference
                    test_case_vector = reference_vector

                elif c == "User Test":  # If it is the User Test, if any
                    test_case_vector = df_user_test_data[p]

                else:  # Other DESTEST cases
                    target = p + " - " + c
                    test_case_vector = df_DESTEST_data[target]

                if echo:
                    print("\nTest case vector for " + str(p) + " ; " + str(c))
                    print(test_case_vector)

                for k, m in enumerate(list_metrics):  # Loop through the different metrics

                    try:
                        "Switch cases to the corresponding metric to calculate"
                        result_KPI = KPI_selector(
                            m,
                            reference_vector,
                            test_case_vector,
                            date_and_time_stamp_vect)
                    except:
                        result_KPI = float("nan")
                        print("Something went wrong")
                    finally:
                        "Find the df entry from p,c,m"
                        df_result.loc[(df_result["Parameter"] == p) & (df_result["KPI / Metric"] == m),c] = result_KPI

                        if echo:
                            message = (
                                "\n"
                                + str(m)
                                + " ; "
                                + str(p)
                                + " ; "
                                + str(c)
                                + " is : "
                                + str(result_KPI))
                            print(message)

                    "Update progress bar"
                    progress["value"] = 20 + 80 * (i * len(full_list_cases) * len(list_metrics) + j * len(list_metrics) + k + 1) / (len(list_parameters) * len(full_list_cases) * len(list_metrics))
                    gui.update_idletasks()

        "Calculate summary metrics"
        df_error_grade, sub_df_err_grades = calculate_error_grade(
            df_result,
            list_DESTEST_cases,
            no_user_test,
            list_KPIs,
            list_KPI_weights,
            echo)

        "Add summary metrics"
        df_result = pd.concat([df_result, df_error_grade], sort=False, ignore_index=True)  # Concat error grade at the end of df result

    except:  # Error during intialization
        gui.destroy()
        raise Exception("The DESTEST comparison calculation has failed.")

    time.sleep(1)
    gui.destroy()
    return df_result, reference_df, sub_df_err_grades


###############################################################################
###                               DESTEST plots                             ###
###############################################################################

def DESTEST_plots(
    df_result,
    parameters,
    no_user_test,
    max_DESTEST_cases_on_graph,
    df_user_test_data,
    reference_df,
    df_DESTEST_data,
    echo=False):
    """Generates different plots fromt the DESTEST comparison results and loaded
    data from the files.
    """

    # Initialize and generate GUI #############################################

    "Create the window"
    gui = tk.Tk()  # Create a new window (widget, root, object)

    "Change exception handler of tkinter"
    def show_error(self, *args):
        nonlocal gui
        gui.destroy()
        raise  # Simply raise the exception
        return

    tk.Tk.report_callback_exception = show_error  # changing the Tk class itself.

    "Change the window properties"
    gui.title("Generate Output Report")
    screen_width = gui.winfo_screenwidth()
    screen_height = gui.winfo_screenheight()
    gui.geometry("400x80+%d+%d" % (screen_width / 2 - 275, screen_height / 2 - 125))  # Adjust window size as a function of screen resolution
    gui.lift()  # Place on top of all Python windows
    gui.attributes("-topmost", True)  # Place on top of all windows (all the time)
    gui.attributes("-topmost", False)  # Disable on top all the time
    gui.resizable(width=False, height=False)  # Disable resizing of the window

    "Frame 1"
    frame1 = tk.LabelFrame(gui, width=400, height=70)
    frame1.pack(padx=10, pady=10)
    frame1.pack_propagate(0)  # Disable resizing of the frame when widgets are packed or resized inside

    "Display message as label on GUI"
    my_label = tk.Label(frame1, text="Generating output report with figures and tables: Please wait.")  # Pack the name of the file on the window
    my_label.pack()

    "Init progess bar"
    progress = Progressbar(frame1, orient=HORIZONTAL, length=200, mode="determinate")  # New horizontal progress bar in determinate (normal) mode
    progress.pack(pady=5)
    progress["value"] = 0
    gui.update_idletasks()
    
    try:
        # Plot Parameters #####################################################
        
        "Get list parameters to plot from the parameters input"
        nbr_parameters_result = len(parameters.list_column_names) - 1
        list_parameters = parameters.list_column_names[1 : nbr_parameters_result + 1]  # get all parameters from 2nd and forward. 1st column name is elapsed time
        
        #######################################################################

        # All results table ###################################################

        "PLot the result table into an HTML doc (temp)"
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=list(df_result.columns),
                        fill_color="paleturquoise",
                        align="left",
                        ),
                    cells=dict(
                        values=[
                            df_result.iloc[:, i] for i, c in enumerate(df_result.columns)
                            ],
                        fill_color="lavender",
                        align="left",
                        ),
                    )
                ]
            )

        plot(fig, auto_open=True)  # Auto open as html in browser

        #######################################################################

        # Min Max Avrg table ##################################################

        #######################################################################

        # Comparison metrics table ############################################

        # Barplots ############################################################

        "Bar plot parameters"
        barWidth = 0.9
        capsize_para = 10

        if no_user_test:
            max_index = max_DESTEST_cases_on_graph + 2 + 1
        else:
            max_index = max_DESTEST_cases_on_graph + 2 + 2

        # Barplots Minimums ###################################################

        "Plot mimima of all parameters for all cases up to limit (one graph per parameter)"

        target = "Minimum"

        for i, p in enumerate(list_parameters):
            "Get data from entire df_result up to limit max graphs"
            df = df_result[(df_result["Parameter"] == p) & (df_result["KPI / Metric"] == target)]  # Get only data
            list_sub_df = df.iloc[0, :]  # Transform into series
            list_sub_df = list_sub_df[2 : min(len(list_sub_df), max_index)]  # Remove 2 first entries (Parameter and KPI / Metric)

            "Create bars"
            if no_user_test:
                bars2 = [list_sub_df[0]]  # Reference
                bars3 = list_sub_df[1 : len(list_sub_df)].tolist()  # All the DESTEST cases

            else:
                bars1 = [list_sub_df[0]]  # User Test
                bars2 = [list_sub_df[1]]  # Reference
                bars3 = list_sub_df[2 : len(list_sub_df)].tolist()  # All the DESTEST case

            "The X position of bars"
            if no_user_test:
                r2 = [1]  # Reference
                r3 = list(range(2, len(list_sub_df) + 1))  # All the DESTEST cases
            else:
                r1 = [1]  # User Test
                r2 = [2]  # Reference
                r3 = list(range(3, len(list_sub_df) + 1))  # All the DESTEST cases

            "Create barplot"
            if not no_user_test:
                plt.bar(r1, bars1, width=barWidth, color="red", label="User Test")

            plt.bar(r2, bars2, width=barWidth, color="grey", label="Reference")
            plt.bar(r3, bars3, width=barWidth, color="royalblue", label="DESTEST cases")

            "Adjust Y-axis to round up/down of max/min values in data"
            if no_user_test:
                y = bars2 + bars3
            else:
                y = bars1 + bars2 + bars3

            low = min(y)
            high = max(y)
            plt.ylim([math.floor(low - 0.5 * (high - low)), math.ceil(high + 0.5 * (high - low))])

            "Labels X-axis"
            if no_user_test:
                labels = ["Ref", "DESTEST cases"]
                x_labels = [1, np.array(r3).mean()]
            else:
                labels = ["User Test", "Ref", "DESTEST cases"]
                x_labels = [1, 2, np.array(r3).mean()]

            plt.xticks(x_labels, labels)

            "Title graph"
            plt.title(str(target) + " " + p)
            plt.show()

            "Update progress bar"
            progress["value"] = 40 + 10 * i / len(list_parameters)
            gui.update_idletasks()

        #######################################################################

        # Barplots Maximums ###################################################

        "Plot maxima of all parameters for all cases up to limit (one graph per parameter)"

        target = "Maximum"

        for i, p in enumerate(list_parameters):
            "Get data from entire df_result up to limit max graphs"
            df = df_result[(df_result["Parameter"] == p) & (df_result["KPI / Metric"] == target)]  # Get only data
            list_sub_df = df.iloc[0, :]  # Transform into series
            list_sub_df = list_sub_df[2 : min(len(list_sub_df), max_index)]  # Remove 2 first entries (Parameter and KPI / Metric)

            "Create bars"
            if no_user_test:
                bars2 = [list_sub_df[0]]  # Reference
                bars3 = list_sub_df[1 : len(list_sub_df)].tolist()  # All the DESTEST cases

            else:
                bars1 = [list_sub_df[0]]  # User Test
                bars2 = [list_sub_df[1]]  # Reference
                bars3 = list_sub_df[2 : len(list_sub_df)].tolist()  # All the DESTEST cases

            "The X position of bars"
            if no_user_test:
                r2 = [1]  # Reference
                r3 = list(range(2, len(list_sub_df) + 1))  # All the DESTEST cases
            else:
                r1 = [1]  # User Test
                r2 = [2]  # Reference
                r3 = list(range(3, len(list_sub_df) + 1))  # All the DESTEST cases

            "Create barplot"
            if not no_user_test:
                plt.bar(r1, bars1, width=barWidth, color="red", label="User Test")

            plt.bar(r2, bars2, width=barWidth, color="grey", label="Reference")
            plt.bar(r3, bars3, width=barWidth, color="royalblue", label="DESTEST cases")

            "Adjust Y-axis to round up/down of max/min values in data"
            if no_user_test:
                y = bars2 + bars3
            else:
                y = bars1 + bars2 + bars3

            low = min(y)
            high = max(y)
            plt.ylim([math.floor(low - 0.5 * (high - low)), math.ceil(high + 0.5 * (high - low))])

            "Labels X-axis"
            if no_user_test:
                labels = ["Ref", "DESTEST cases"]
                x_labels = [1, np.array(r3).mean()]
            else:
                labels = ["User Test", "Ref", "DESTEST cases"]
                x_labels = [1, 2, np.array(r3).mean()]

            plt.xticks(x_labels, labels)

            "Title graph"
            plt.title(str(target) + " " + p)
            plt.show()
        
            "Update progress bar"
            progress["value"] = 50 + 10 * i / len(list_parameters)
            gui.update_idletasks()

        #######################################################################

        # Barplots Averages + std dev #########################################

        "Plot averages and standard deviations of all parameters for all cases up to limit (one graph per parameter)"

        target1 = "Average"
        target2 = "Standard Deviation"

        for i, p in enumerate(list_parameters):
            "Get data from entire df_result up to limit max graphs for target1"
            df = df_result[(df_result["Parameter"] == p) & (df_result["KPI / Metric"] == target1)]  # Get only data
            list_sub_df1 = df.iloc[0, :]  # Transform into series
            list_sub_df1 = list_sub_df1[2 : min(len(list_sub_df1), max_index)]  # Remove 2 first entries (Parameter and KPI / Metric)

            "Get data from entire df_result up to limit max graphs for target2"
            df = df_result[(df_result["Parameter"] == p) & (df_result["KPI / Metric"] == target2)]  # Get only data
            list_sub_df2 = df.iloc[0, :]  # Transform into series
            list_sub_df2 = list_sub_df2[2 : min(len(list_sub_df2), max_index)]  # Remove 2 first entries (Parameter and KPI / Metric)

            "Create bars"
            if no_user_test:
                bars2_t1 = [list_sub_df1[0]]  # Reference
                bars3_t1 = list_sub_df1[1 : len(list_sub_df1)].tolist()  # All the DESTEST

                bars2_t2 = [list_sub_df2[0]]  # Reference
                bars3_t2 = list_sub_df2[1 : len(list_sub_df2)].tolist()  # All the DESTEST

            else:
                bars1_t1 = [list_sub_df1[0]]  # User Test
                bars2_t1 = [list_sub_df1[1]]  # Reference
                bars3_t1 = list_sub_df1[2 : len(list_sub_df1)].tolist()  # All the DESTEST

                bars1_t2 = [list_sub_df2[0]]  # User Test
                bars2_t2 = [list_sub_df2[1]]  # Reference
                bars3_t2 = list_sub_df2[2 : len(list_sub_df2)].tolist()  # All the DESTEST

            "The X position of bars"
            if no_user_test:
                r2 = [1]  # Reference
                r3 = list(range(2, len(list_sub_df1) + 1))  # All the DESTEST cases
            else:
                r1 = [1]  # User Test
                r2 = [2]  # Reference
                r3 = list(range(3, len(list_sub_df1) + 1))  # All the DESTEST cases

            "Create barplot"
            if not no_user_test:
                plt.bar(
                    r1,
                    bars1_t1,
                    yerr=bars1_t2,
                    align="center",
                    capsize=capsize_para,
                    ecolor="black",
                    width=barWidth,
                    color="red",
                    label="User Test")

            plt.bar(
                r2,
                bars2_t1,
                yerr=bars2_t2,
                align="center",
                capsize=capsize_para,
                ecolor="black",
                width=barWidth,
                color="grey",
                label="Reference")
        
            plt.bar(
                r3,
                bars3_t1,
                yerr=bars3_t2,
                align="center",
                capsize=capsize_para,
                ecolor="black",
                width=barWidth,
                color="royalblue",
                label="DESTEST cases")

            "Adjust Y-axis to round up/down of max/min values in data"
            if no_user_test:
                y = (
                    bars2_t1
                    + bars3_t1
                    + (np.array(bars2_t1) + np.array(bars2_t2)).tolist()
                    + (np.array(bars2_t1) - np.array(bars2_t2)).tolist()
                    + (np.array(bars3_t1) + np.array(bars3_t2)).tolist()
                    + (np.array(bars3_t1) - np.array(bars3_t2)).tolist())
            else:
                y = (
                    bars1_t1
                    + bars2_t1
                    + bars3_t1
                    + (np.array(bars1_t1) + np.array(bars1_t2)).tolist()
                    + (np.array(bars1_t1) - np.array(bars1_t2)).tolist()
                    + (np.array(bars2_t1) + np.array(bars2_t2)).tolist()
                    + (np.array(bars2_t1) - np.array(bars2_t2)).tolist()
                    + (np.array(bars3_t1) + np.array(bars3_t2)).tolist()
                    + (np.array(bars3_t1) - np.array(bars3_t2)).tolist())

            low = min(y)
            high = max(y)
            plt.ylim([math.floor(low - 0.5 * (high - low)), math.ceil(high + 0.5 * (high - low))])

            "Labels X-axis"
            if no_user_test:
                labels = ["Ref", "DESTEST cases"]
                x_labels = [1, np.array(r3).mean()]
            else:
                labels = ["User Test", "Ref", "DESTEST cases"]
                x_labels = [1, 2, np.array(r3).mean()]

            plt.xticks(x_labels, labels)

            "Title graph"
            plt.title(str(target1) + " & " + str(target2) + " " + p)
            plt.show()
        
            "Update progress bar"
            progress["value"] = 60 + 10 * i / len(list_parameters)
            gui.update_idletasks()

        # Profile graphs ######################################################

        "loop through the list of typical days"
        list_typical_days = parameters.list_typical_days
        for i, d in enumerate(list_typical_days):
            for p in list_parameters:
                "Get data from df_DESTEST_data, df_user_test_data and reference_df to limit max graphs"

                "Filter df columns that contains the current parameter of interest"
                list_boolean_targets = list(p in name for name in df_DESTEST_data.columns)  # Boolean list based on condition "p" in "name" with loop on "name"
                list_name_targets = list(df_DESTEST_data.columns[list_boolean_targets])  # Get all corresponding column names with "p" in it
                df_destest_cases = df_DESTEST_data[list_name_targets]  # Filter df columns that contains the current parameter of interest

                "limit number of DESTEST cases"
                df_destest_cases = df_destest_cases.iloc[:, 0 : min(len(df_destest_cases.columns), max_DESTEST_cases_on_graph)]

                "remove prefix from the DESDEST df column names"
                prefix = p + " - "
                list_destest_cases = list(df_destest_cases.columns.str.lstrip(prefix))  # Get again list DESTEST from the df just to be sure it's in the same order
                df_destest_cases.columns = list_destest_cases

                "get data from reference (including time vectors)"
                ref_df_time = reference_df.iloc[:, 0:2]
                ref_df_data = pd.DataFrame(reference_df[p])
                ref_df_data.columns = ["Reference"]

                "Set min and max of the time series"
                xmin = np.datetime64(d + " 00:00:00")
                xmax = xmin + np.timedelta64(1, "D")  # Add one full day

                "Find indexes of min max in timestamp series"
                x = ref_df_time["Date and Time"]  # Time vector
                xmin_index = list(x).index(xmin)
                xmax_index = list(x).index(xmax)

                x = x[xmin_index : xmax_index + 1]

                if not no_user_test:
                    y = df_user_test_data[p][xmin_index : xmax_index + 1]
                    plt.plot(x, y, label="User Test", color="red", linewidth=2)

                "Plot ref line"
                y = ref_df_data[xmin_index : xmax_index + 1]
                plt.plot(x, y, label="Reference", color="black", linewidth=2)

                "Plot other lines"
                for c in list_destest_cases:
                    y = df_destest_cases[c][xmin_index : xmax_index + 1]
                    plt.plot(x, y, label=c, linewidth=0.5)

                "Format plot"
                plt.xlabel("Date and Time")
                plt.ylabel(p)

                ax = plt.gca()  # get the current axes

                ax.set_xlim(xmin, xmax)

                ax.xaxis.set_minor_locator(dates.HourLocator(interval=4))  # every 4 hours
                ax.xaxis.set_minor_formatter(dates.DateFormatter("%H:%M"))  # hours and minutes
                ax.xaxis.set_major_locator(dates.DayLocator(interval=1))  # every day
                ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M\n%Y-%m-%d"))  # Show date only at each midnight 00:00

                plt.title(p + str(" on the ") + str(d))
                plt.legend()

                plt.show()  # Display a figure
            
            "Update progress bar"
            progress["value"] = 70 + 10 * i / len(list_parameters)
            gui.update_idletasks()

        # Time distribution graphs ############################################

        for i, p in enumerate(list_parameters):
            "Get data from df_DESTEST_data, df_user_test_data and reference_df to limit max graphs"

            "Filter df columns that contains the current parameter of interest"
            list_boolean_targets = list(p in name for name in df_DESTEST_data.columns)  # Boolean list based on condition "p" in "name" with loop on "name"
            list_name_targets = list(df_DESTEST_data.columns[list_boolean_targets])  # Get all corresponding column names with "p" in it
            df_destest_cases = df_DESTEST_data[list_name_targets]  # Filter df columns that contains the current parameter of interest

            "limit number of DESTEST cases"
            df_destest_cases = df_destest_cases.iloc[:, 0 : min(len(df_destest_cases.columns), max_DESTEST_cases_on_graph)]

            "remove prefix from the DESDEST df column names"
            prefix = p + " - "
            list_destest_cases = list(df_destest_cases.columns.str.lstrip(prefix))  # Get again list DESTEST from the df just to be sure it's in the same order
            df_destest_cases.columns = list_destest_cases

            "get data from reference (including time vectors)"
            ref_df_time = reference_df.iloc[:, 0:2]
            ref_df_data = reference_df[p]
            ref_df_data.columns = ["Reference"]

            "Time stamp series"
            x = ref_df_time["Elapsed time [sec]"]  # Time vector [Elapsed time [ec]]
            x = x / 3600  # Format into hours

            if not no_user_test:
                y = df_user_test_data[p].sort_values(ascending=False)
                plt.plot(x, y, label="User Test", color="red", linewidth=2)

            "Plot ref line"
            y = ref_df_data.sort_values(ascending=False)
            plt.plot(x, y, label="Reference", color="black", linewidth=2)

            "Plot other lines"
            for c in list_destest_cases:
                y = df_destest_cases[c].sort_values(ascending=False)
                plt.plot(x, y, label=c, linewidth=0.5)

            "Format plot"
            plt.xlabel("Hours")
            plt.ylabel(p)

            plt.title(str("Time distribution of ") + p)
            plt.legend()

            plt.show()  # Display a figure

            "Update progress bar"
            progress["value"] = 80 + 10 * i / len(list_parameters)
            gui.update_idletasks()

        # 1V1 Scattered point plot for User Test Data #########################

        if not no_user_test:
            for i, p in enumerate(list_parameters):

                "get data from reference"
                x = reference_df[p]
                ref_df_data.columns = ["Reference"]
                y = df_user_test_data[p]

                plt.scatter(x, y, color="red", alpha=0.05, s=10)  # No label
                plt.plot([], [], "o", label="User Test Data", color="red")  # Empty plot to get the correct legend marker size

                "Plot linear fit lines"
                m, b = np.polyfit(x, y, 1)  # m = slope, b = intercept
                plt.plot(
                    x,
                    m * x + b,
                    label="Linear Fitting Function (m*x+b)",
                    color="blue",
                    linewidth=2)

                "Plot y=x line"
                x = [min(list(x) + list(y)), max(list(x) + list(y))]
                y = x
                plt.plot(x, y, label="Y = X (Test = Reference) Line", color="black", linewidth=2)

                "Format plot"
                plt.xlabel("Reference: " + p)
                plt.ylabel("User Test: " + p)

                plt.title(str("User Test vs Reference Comparison: ") + p)
                plt.legend(loc="upper left")

                plt.show()  # Display a figure
            
                "Update progress bar"
                progress["value"] = 90 + 10 * i / len(list_parameters)
                gui.update_idletasks()
    
        "Update progress bar"
        progress["value"] = 100
        gui.update_idletasks()
    
    except:
        gui.destroy()
        raise
    
    else:
        gui.destroy()
        return


###############################################################################
###                         DESTEST comparison (main)                       ###
###############################################################################

def DESTEST_comparison(echo=False):

    """
    The 'DESTEST_comparison' function performs all the tasks for the comparison of the selected DESTEST data files.

    Input:
    - echo (False): if echo is true, the steps of the functions and sub-functions are printed in console.

    Output:
    - executes the different tasks to perform the comparison of the selected DESTEST data files.
    """

    # Parameters ##############################################################

    "Github server information"
    server_info.user = "ibpsa"  # Name of the Github
    server_info.repository = "project1-destest"  # name of the repository
    server_info.url = "https://api.github.com/repos/{}/{}/git/trees/master?recursive=1".format(server_info.user, server_info.repository)  # Recursive to get sub-folders as well
    server_info.root_raw_data = ("https://raw.githubusercontent.com/")  # Read data file from raw.githubusercontent.com
    server_info.master_folder_name = "/master/"

    "KPIs / Comparison Metrics implemented in the module"
    list_implemented_KPIs = [
        "NMBE [%]",
        "Hourly CVRMSE [%]",
        "Daily Amplitude CVRMSE [%]",
        "R squared (coefficient of determination) [-]",
        "RMSE [-]",
        "RMSLE [-]",
        "CVRMSE [%]"]

    "Dictionary for the corresponding list of implemented KPIs and comparison metrics"
    "Include min, max and average as well"
    dictionnary_KPI_functions = {
        "NMBE [%]": function_NMBE,
        "Hourly CVRMSE [%]": function_Hourly_CVRMSE,
        "Daily Amplitude CVRMSE [%]": function_Daily_Amplitude_CVRMSE,
        "R squared (coefficient of determination) [-]": function_R_squared_coeff_determination,
        "RMSE [-]": function_RMSE,
        "RMSLE [-]": function_RMSLE,
        "CVRMSE [%]": function_CVRMSE,
        "Minimum": function_Minimum,
        "Maximum": function_Maximum,
        "Average": function_Average,
        "Standard Deviation": function_std_dev}

    "Dictionary for the grading system (best_highest, best_lowest or best_zero) for the implemented KPIs"
    "Does not include min, max and average as well"
    dictionnary_KPI_grade_system = {
        "NMBE [%]": "best_zero",
        "Hourly CVRMSE [%]": "best_zero",
        "Daily Amplitude CVRMSE [%]": "best_zero",
        "R squared (coefficient of determination) [-]": "best_highest",
        "RMSE [-]": "best_zero",
        "RMSLE [-]": "best_zero",
        "CVRMSE [%]": "best_zero"}

    "List of parameters to be found in the parameter file"
    list_parameters_to_find = [
        "length header data files (number of lines):",
        "first data line (line number):",
        "number of data columns:",
        "number of data rows:",
        "list of column names:",
        "list of default KPIs:",
        "list of default KPI_weights:",
        "sampling time interval [sec]:",
        "start date time:",
        "list typical days:"]

    "Limit the number of DESTEST cases visible on the result graphs to improve readability of the graph"
    max_DESTEST_cases_on_graph = 10

    # Start ###################################################################

    if echo:
        print("\nStart DESTEST comparison procedure")

    # Welcome message #########################################################

    try:
        welcome_message(echo)

    except Abort_exception:  # If user closes gui window
        message = "The user aborted the procedure.\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred.\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    # Selection of case characteristics #######################################

    if echo:
        print("\nSelection of the case characteristics")

    try:
        case_type = prompt_user_case_type(echo)

    except Abort_exception:  # If user closes gui window
        message = "The user aborted the procedure.\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred: No valid case type could be selected.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    try:
        "Select file filter parameters"
        if case_type == "Building":
            filtering_code, parameter_file_name = prompt_user_case_characteristics_building(echo)

        elif case_type == "District Heating Network":
            filtering_code, parameter_file_name = prompt_user_case_characteristics_network(echo)

        else:
            Exception("Wrong case type")

    except Abort_exception:  # If user closes gui window
        message = "The user aborted the procedure.\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred: No valid parameter file could be found.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    # Loading parameter file ##################################################

    try:
        "Load parameters file into parameter object"
        parameters, full_path_file_parameter_file = load_parameters(
            server_info,
            parameter_file_name,
            list_implemented_KPIs,
            list_parameters_to_find,
            echo)
        
    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred: No valid DESTEST parameters file could be loaded correctly.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    else:
        if echo:
            print("\nThe parameters have been successfully loaded")
            print("Number of data columns:", parameters.nbr_data_column)
            print("Length header data files (number of lines):", parameters.header_length)
            print("First data line (line number):", parameters.first_line_data)
            print("Number of data rows:", parameters.nbr_data_rows)
            print("List of column names:", parameters.list_column_names)
            print("List of default KPIs for the DESTEST comparison:", parameters.list_default_KPIs)
            print("List of default KPI weights for the DESTEST comparison:", parameters.list_default_KPI_weights)
            print("The sampling time [sec]:", parameters.sampling_time)

    # Check DESTEST online repository #########################################

    if echo:
        print("\nStart finding and loading DESTEST data folder")

    try:
        "Check validity of online DESTEST folder containing all the pool of data files"
        validity_folder, df_valid, list_filtered_data_files, valid_file_full_path_url = check_validity_DESTEST_folder(
            filtering_code, parameters, server_info, echo)

    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred: No valid data could be found in the online DESTEST repository.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    else:  # If there is no error
        if validity_folder:
            if echo:
                print("\nThe online DESTEST repository is valid.")
        else:
            message = "An error has occurred: The online DESTEST repository is not valid.\n\nThe procedure is terminated immediately."
            if echo:
                print("\n", message)
            "Create a tk gui, hide it immediately, and destroy it after message clicked"
            gui = tk.Tk()
            gui.withdraw()
            mbox.showerror("Error", message)  # Popup message window
            gui.destroy()
            raise Exception("The online DESTEST repository is not valid.")

    # Load DESTEST data from online repository ################################

    global df_DESTEST_data
    global list_DESTEST_cases

    try:
        "Load entire DESTEST folder into df"
        df_DESTEST_data, list_DESTEST_cases = load_DESTEST_data(
            list_filtered_data_files,
            filtering_code,
            server_info,
            parameters,
            df_valid,
            echo)

    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred: No valid DESTEST data file could be loaded.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    else:
        if echo:
            print("DESTEST data loading completed.")

    # Load user test data file ################################################

    if echo:
        print("\nStart finding and loading user test data file")

    try:
        "Select file containing user test data file"
        user_test_data_file, no_user_test = prompt_user_for_user_data_file(
            parameters,
            server_info,
            full_path_file_parameter_file,
            filtering_code,
            valid_file_full_path_url,
            echo)

    except Abort_exception:  # If user closes gui window
        message = "The user aborted the procedure.\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred: No valid user test data file could be found.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    else:  # If there is no error
        if echo:
            if no_user_test:
                print("\nNo user test data has been selected.")
            else:
                print("\nValid user test data file has been successfully found:")
                print("\n", user_test_data_file)

    global df_user_test_data

    try:
        "Reload user test data file into df"
        df_user_test_data = load_user_test_data(user_test_data_file, parameters, no_user_test, echo)

    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred: No valid user test data file could be found.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    # Select DESTEST KPIs for comparison calculation ##########################

    if echo:
        print("\nPrompt DESTEST KPIs and KPI weights from user for DESTEST comparison")

    try:
        list_KPIs, list_KPI_weights = DESTEST_KPIs_selection(parameters, list_implemented_KPIs, echo)

    except:  # If any other error occurs (absorbs the error raise)
        message = "An error has occurred: No valid list of KPI could be determined.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    else:
        if echo:
            print("\nSelection of KPIs completed.")

    # Perform DESTEST comparison calculation ##################################

    if echo:
        print("\nStart DESTEST comparison calculation.")

    global df_result
    global reference_df
    global sub_df_err_grades

    try:
        df_result, reference_df, sub_df_err_grades = DESTEST_comparison_calculation(
            df_user_test_data,
            df_DESTEST_data,
            list_DESTEST_cases,
            parameters,
            no_user_test,
            list_KPIs,
            list_KPI_weights,
            dictionnary_KPI_functions,
            dictionnary_KPI_grade_system,
            echo)
    except:
        message = "An error has occurred: The DESTEST comparison calculation could not be carried out.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise
    else:
        if echo:
            print("\nDESTEST comparison calculation completed.")

    # Generate result graphs ##################################################

    if echo:
        print("\nPlot the DESTEST results.")

    try:
        DESTEST_plots(
            df_result,
            parameters,
            no_user_test,
            max_DESTEST_cases_on_graph,
            df_user_test_data,
            reference_df,
            df_DESTEST_data,
            echo=False)
    except:
        message = "An error has occurred: The DESTEST comparison plots could not be generated.\n\nThe procedure is terminated immediately."
        if echo:
            print("\n", message)
        "Create a tk gui, hide it immediately, and destroy it after message clicked"
        gui = tk.Tk()
        gui.withdraw()
        mbox.showerror("Error", message)  # Popup message window
        gui.destroy()
        raise  # Raise the current error to stop the execution. No need of return after raise

    # Generate result report ##################################################

    # End #####################################################################

    message = str("The DESTEST comparison has been successfully executed.")
    if echo:
        print("\n", message)
    "Create a tk gui, hide it immediately, and destroy it after message clicked"
    gui = tk.Tk()
    gui.withdraw()
    mbox.showinfo("Success", message)  # Popup message window
    gui.destroy()
    return


"#############################################################################"
"##                             (Execute) main                              ##"
"#############################################################################"

"If run directly but not imported, then run the script"
"If imported as module, then do not run the script"

if __name__ == "__main__":  # If run directly but not imported, then run the script
    DESTEST_comparison(echo=True)  # Execute the DESTEST comparison with echo mode on
