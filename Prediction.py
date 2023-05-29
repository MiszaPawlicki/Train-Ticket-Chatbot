import csv
import datetime
import holidays
import os
import glob
import time
import sqlite3

import numpy as np
from sklearn import preprocessing
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import OneHotEncoder

import pandas as pd


def read_data_2():
    trains_df = pd.DataFrame(
        columns=['first station dev', 'day of week', 'day of month', 'weekday', 'on peak', 'hour', 'associated journey',
                 'associated journey dev from dep',
                 'associated journey first stop', 'associated journey second stop', 'rid'])

    for path, subdirectory, files in os.walk("Train data"):
        for file_loc in glob.glob(path+"/*.csv"):
            file = csv.reader(open(file_loc),delimiter = ',')
            list_file = list(file)
            rid_no = list_file[1][0]
            previous_rid = list_file[1][0]
            first_station_deviation = None
            journey_first_stop_time = ""
            journey_second_stop_time = ""
            date = datetime.datetime.strptime(list_file[1][0][0:8],'%Y%m%d').date()
            day_of_week = date.weekday()
            weekday = ""
            if list_file[1][18] != "":
                time = list_file[1][18]
            elif list_file[1][10] != "":
                time = list_file[1][10]
            else:
                time = "00:00"
            hour = datetime.datetime.strptime(time, '%H:%M').time().hour
            associated_journey = "0"
            associated_journey_dev_from_dep = "0"
            associated_journey_first_stop = "00:00"
            associated_journey_second_stop ="00:00"
            predicted_dep = "00:00"
            previous_dep = "00:00"
            year = rid_no[0:4]
            month = rid_no[4:6]
            day_of_month = rid_no[6:8]
            if day_of_week < 5:
                weekday = True
            else:
                weekday = False
            on_peak = check_on_peak(date, time)




            for row in list_file[1:]:  # read all the lines in the file - apart from the first line (column names)
                if row[0] != previous_rid and previous_rid != None:  # if this is a different train, and not the first piece of data in the file
                    trains_df = pd.concat([trains_df,pd.DataFrame({'first station dev':first_station_deviation,'day of week':day_of_week,
                                                  'day of month':day_of_month,'weekday':weekday,'on peak':on_peak,'hour':hour,
                                                  'associated journey':associated_journey,'associated journey dev from dep':associated_journey_dev_from_dep,
                                                'associated journey first stop':associated_journey_first_stop,
                                                  'associated journey second stop':associated_journey_second_stop,'rid':previous_rid},index = [0])])

                    rid_no = row[0]  # retrieve the unique value that relates to the train instance
                    year = rid_no[0:4]
                    month = rid_no[4:6]
                    day_of_month = rid_no[6:8]
                    previous_dep = time
                    if row[3] == "":
                        previous_rid = row[0]
                        continue
                    previous_pred_dep = predicted_dep
                    predicted_dep = row[3]
                    if row[18]!= "":
                        time = row[18]
                    elif row[10]!= "":
                        time = row[10]
                    else:
                        previous_rid = row[0]
                        journey_first_stop_time = ""
                        journey_second_stop_time = ""
                        continue
                    date = datetime.datetime.strptime(year+month+day_of_month,'%Y%m%d').date()  # convert the date to a datetime object
                    day_of_week = date.weekday()
                    if day_of_week < 5:
                        weekday = True
                    else:
                        weekday = False

                if row[3] != row[18]:
                    if first_station_deviation == None:
                        first_station_deviation = row[1]
                # find the associated journey expected departure time

                # if the rid number is the same as the last row that means it is the same train service.
                if previous_rid == row[0]:  # this is the same train service as the previous row
                    if journey_first_stop_time == "" and row[2]!= "":  # predicted arrival for first stop
                        journey_first_stop_time = row[2]
                    elif journey_second_stop_time == "" and row[2] != "":
                        journey_second_stop_time = row[2]



                elif previous_rid != row[0]:
                    associated_journey_first_stop = journey_first_stop_time
                    associated_journey_second_stop = journey_second_stop_time
                    journey_first_stop_time = ""
                    journey_second_stop_time = ""
                    first_station_deviation = None  # make it null again after adding the row to the df/db
                    previous_expected_departure_row = row
                    if time == "":
                        previous_rid = row[0] # does not allow the incomplete data to be stored
                        continue  # do not add the value to the dataframe - Go to next iteration to stop break of loop
                    if previous_expected_departure_row == "":  # if there is no previous stop
                        associated_journey = ""
                        associated_journey_dev_from_dep = ""
                        associated_journey_first_stop = ""
                        associated_journey_second_stop = ""
                    else:
                        if date == datetime.datetime.strptime(previous_expected_departure_row[0][0:8],'%Y%m%d').date():  # if the date is the same as the previous departure
                            if previous_expected_departure_row[18] != "":
                                previous_expected = previous_expected_departure_row[18]
                            else:
                                previous_expected = previous_expected_departure_row[13]


                            associated_journey_dev_from_dep = datetime.datetime.strptime(previous_dep,'%H:%M')\
                                                          - datetime.datetime.strptime(previous_pred_dep,'%H:%M')
                            associated_journey_dev_from_dep = associated_journey_dev_from_dep.total_seconds()/60 # convert it into minutes
                            associated_journey = previous_expected_departure_row[3]

                    hour = datetime.datetime.strptime(time, '%H:%M').time().hour
                    on_peak = check_on_peak(date, time)
                previous_rid = row[0]


            #after the for loop has broken, add the final values to the table



            trains_df = pd.concat(
                [trains_df, pd.DataFrame({'first station dev': first_station_deviation, 'day of week': day_of_week,
                                          'day of month': day_of_month, 'weekday': weekday, 'on peak': on_peak, 'hour': hour,
                                          'associated journey': associated_journey,
                                          'associated journey dev from dep': associated_journey_dev_from_dep,
                                          'associated journey first stop': associated_journey_first_stop,
                                          'associated journey second stop': associated_journey_second_stop,"rid":previous_rid}, index=[0])])


    file = sqlite3.connect('prediction data/test.sqlite')
    trains_df.to_sql('Train_data', file, if_exists='replace', index=False)
    pd.read_sql('select * from Train_data', file)
    return trains_df

def find_destination(file, rid_no):
    for row in file[1:]:
        if row[0] == rid_no and row[10]!='':
            return row[1]

def check_on_peak(date,time):
    """

    :param date: a datetime object representing the date of departure of train
    :param time: a string object representing the time of departure of train
    :return: returns True if it is on peak (in a busy period), if not it returns False (off peak)
    """
    if date in holidays.country_holidays("GB"):
        return False
    else:
        if date.weekday() < 5:
            time = datetime.datetime.strptime(time,"%H:%M").time()
            if datetime.time(16,0,0)>time>datetime.time(9,30,0):
                return False
            elif datetime.time(19,0,0)<time:
                return False
            else:
                return True
        else:
            return True

def predict_using_params(first_station_dev = None, day_of_week = None, day_of_month = None, boolean_weekday = None,
                         on_peak = None, hour = None, associated_journey = None, associated_journey_dev_from_dep = None,
                associated_journey_first_stop = None,associated_journey_second_stop = None):
    # read in the data from the database
    train_data = pd.DataFrame()
    file = sqlite3.connect('prediction data/test.sqlite')
    from_file = pd.read_sql_query(" SELECT * FROM Train_data", file)
    input = pd.DataFrame()
    if first_station_dev != None:
        # convert to numerical values
        encoder = OneHotEncoder(sparse_output=False)  # This encoder will split each of the stations into
        input['first station dev'] = [first_station_dev]
        # individual columns so they can be compared.
        encoded = encoder.fit_transform(np.array(from_file['first station dev']).reshape(-1,1))
        column_names = encoder.get_feature_names_out(input_features=['first station dev'])
        train_data = pd.DataFrame(encoded, columns=column_names)
        input = pd.DataFrame(encoder.transform(input), columns=column_names)

    if day_of_week != None:
        train_data['day of week'] = from_file['day of week']
        input['day of week'] = [day_of_week]
    if day_of_month != None:
        train_data['day of month'] = from_file['day of month']
        input['day of month'] = [day_of_month]
    if boolean_weekday != None:
        train_data['weekday'] = from_file['weekday']
        input['weekday'] = [boolean_weekday]
    if on_peak != None:
        train_data['on peak'] = from_file['on peak']
        input['on peak'] = [on_peak]
    if hour != None:
        train_data['hour'] = from_file['hour']
        input['hour'] = [hour]
    if associated_journey != None:
        # TODO needs to be converted to numerical values
        train_data['associated journey'] = from_file['associated journey']
        input['associated journey'] = [associated_journey]
    if associated_journey_dev_from_dep != None:
        train_data['associated journey dev from dep'] = from_file['associated journey dev from dep']
        input['associated journey dev from dep'] = [associated_journey_dev_from_dep]
    if associated_journey_first_stop != None:
        # TODO needs to be converted into numerical values
        train_data['associated journey first stop'] = from_file['associated journey first stop']
        input['associated journey first stop'] = [associated_journey_first_stop]
    if associated_journey_second_stop != None:
        train_data['associated journey second stop'] = from_file['associated journey second stop']
        input['associated journey second stop'] = [associated_journey_second_stop]


    #encoder = OneHotEncoder(sparse_output=False)
    #encoded = encoder.fit_transform(train_data)
    #column_names = encoder.get_feature_names_out(input_features=['first station dev'])
    #encoded = pd.DataFrame(encoded, columns=column_names)

    predictor = KNeighborsClassifier(n_neighbors=1)
    y_values = np.array(from_file['rid'].values)
    predictor.fit(X=train_data,y=y_values)

    return predictor.predict(input)[0]

def time_difference(rid, start, end):
    first_time = ""
    second_time = ""
    for path, subdirectory, files in os.walk("Train data"):
        for file_loc in glob.glob(path + "/*.csv"):
            file = csv.reader(open(file_loc), delimiter=',')
            list_file = list(file)
            for row in list_file[1:]:
                if row[0] == rid:
                    if row[1] == start:

                        if row[18]!="":  # retrieve the departure time if there is one
                            first_time = row[18]
                        if row[13]!="":
                            first_time = row[13]
                        elif row[17]!="":  # The time of passing is retrieved
                            first_time = row[17]
                        elif row[10] != "":  # expected passing time otherwise is retrieved
                            first_time = row[10]

                    if row[1] == end:
                        if row[16]!="":  # retrieve the arrival time if there is one
                            second_time = row[16]
                        elif row[7]!="":  # expected time of arrival is retrieved
                            second_time = row[7]
                        elif row[17]!="":  # The time of passing is retrieved
                            second_time = row[17]
                        elif row[10] != "":  # expected passing time otherwise is retrieved
                            second_time = row[10]

    time_difference = datetime.datetime.strptime(second_time, '%H:%M') - datetime.datetime.strptime(first_time, '%H:%M')
    #print(time_difference.seconds,"is the amount of seconds between the two stops")
    return time_difference.seconds

def main():
    #print(check_on_peak(datetime.datetime(2022,1,5),"10:00"))
    #start = time.time()
    #train_data = read_data_2()


    rid = predict_using_params(first_station_dev="WDON")
    # TODO associated journeys need to be changed to a value that can be compared - maybe the time in difference?
    difference = time_difference(rid,"WDON","ESHER")
    planned_arrival = "11:52"
    planned_arrival = datetime.datetime.strptime(planned_arrival, "%H:%M")

    result = planned_arrival + datetime.timedelta(seconds = difference)
    print(result.time())



    # find the predicted time of arrival from the user and add the time difference to it.

    # What is the expected time of arrival?
    # What was the actual time of arrival?





    #train_data.to_csv('train_data.csv')

    #end = time.time()
    #duration = end - start
    #print(duration)
    #print("money shot")
    #prediction("202001028717288", "WDON","ESHER")

if __name__ == "__main__":
    main()