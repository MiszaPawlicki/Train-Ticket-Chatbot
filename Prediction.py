import csv
import datetime
import holidays
import os
import glob
import time

import pandas as pd


 # ensure that all the train data is in a folder ready before runnning this file!!
def read_data():
    trains_df = pd.DataFrame(
        columns=['first station dev', 'day of week', 'day of month', 'weekday', 'on peak', 'hour', 'associated journey',
                 'associated journey dev from dep',
                 'associcated journey first stop', 'associated journey second stop', 'rid'])

    for path, subdirectory, files in os.walk("Train data"):
        for file_loc in glob.glob(path+"/*.csv"):
            print(file_loc)
            file = csv.reader(open(file_loc),delimiter = ',')
            list_file = list(file)
            previous_rid = None
            first_station_deviation = None
            previous_expected_departure_row = ""
            journey_first_stop_time = ""
            journey_second_stop_time = ""
            on_peak = None

            for row in list_file[1:]:  # read all the lines in the file - apart from the first line (column names)
                if row[0] != previous_rid and previous_rid != None:  # if this is a different train, and not the first piece of data in the file
                    #trains_array.append([first_station_deviation,day_of_week,day_of_month,weekday,on_peak,hour,
                    #                              associated_journey,associated_journey_dev_from_dep,
                    #                            associated_journey_first_stop,associated_journey_second_stop,previous_rid])



                    print(row[0]," does not equal ",previous_rid)
                    trains_df = pd.concat([trains_df,pd.DataFrame({'first station dev':first_station_deviation,'day of week':day_of_week,
                                                  'day of month':day_of_month,'weekday':weekday,'on peak':on_peak,'hour':hour,
                                                  'associated journey':associated_journey,'associated journey dev from dep':associated_journey_dev_from_dep,
                                                'associcated journey first stop':associated_journey_first_stop,
                                                  'associated journey second stop':associated_journey_second_stop,'rid':previous_rid},index = [0])])


                destination = find_destination(list_file, row[0])
                rid_no = row[0]
                year = rid_no[0:4]
                month = rid_no[4:6]
                day_of_month = rid_no[6:8]
                if row[18]!= "":
                    time = row[18]
                else:
                    row[10]

                time = row[18]
                date = datetime.datetime.strptime(year+month+day_of_month,'%Y%m%d').date()  # convert the date to a datetime object
                day_of_week = date.strftime('%A')
                day_of_week_no = date.weekday()
                if day_of_week_no < 5:
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
                    #TODO add the current values to the data set - this will mean when the nexr train information can
                    # start to be read the previous data can be added to the db/df
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
                            associated_journey_dev_from_dep = datetime.datetime.strptime(previous_expected_departure_row[18],'%H:%M')\
                                                          - datetime.datetime.strptime(previous_expected_departure_row[3],'%H:%M')
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
                                          'associcated journey first stop': associated_journey_first_stop,
                                          'associated journey second stop': associated_journey_second_stop,"rid":previous_rid}, index=[0])])


    return trains_df


def read_data_2():
    trains_df = pd.DataFrame(
        columns=['first station dev', 'day of week', 'day of month', 'weekday', 'on peak', 'hour', 'associated journey',
                 'associated journey dev from dep',
                 'associcated journey first stop', 'associated journey second stop', 'rid'])

    for path, subdirectory, files in os.walk("Train data"):
        for file_loc in glob.glob(path+"/*.csv"):
            print(file_loc)
            file = csv.reader(open(file_loc),delimiter = ',')
            list_file = list(file)
            previous_rid = list_file[1][0]
            first_station_deviation = None
            journey_first_stop_time = ""
            journey_second_stop_time = ""
            on_peak = None
            day_of_month = None
            time = "00:00"
            date = datetime.datetime.strptime(list_file[1][0][0:8],'%Y%m%d').date()
            day_of_week=""
            weekday = ""
            hour = ""
            associated_journey = ""
            associated_journey_dev_from_dep = ""
            associated_journey_first_stop = ""
            associated_journey_second_stop  =""
            predicted_dep = "00:00"
            previous_dep = "00:00"



            for row in list_file[1:]:  # read all the lines in the file - apart from the first line (column names)
                if row[0] != previous_rid and previous_rid != None:  # if this is a different train, and not the first piece of data in the file
                    trains_df = pd.concat([trains_df,pd.DataFrame({'first station dev':first_station_deviation,'day of week':day_of_week,
                                                  'day of month':day_of_month,'weekday':weekday,'on peak':on_peak,'hour':hour,
                                                  'associated journey':associated_journey,'associated journey dev from dep':associated_journey_dev_from_dep,
                                                'associcated journey first stop':associated_journey_first_stop,
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
                        continue
                    date = datetime.datetime.strptime(year+month+day_of_month,'%Y%m%d').date()  # convert the date to a datetime object
                    day_of_week = date.strftime('%A')
                    day_of_week_no = date.weekday()
                    if day_of_week_no < 5:
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
                                print(previous_expected_departure_row)
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
                                          'associcated journey first stop': associated_journey_first_stop,
                                          'associated journey second stop': associated_journey_second_stop,"rid":previous_rid}, index=[0])])


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

def predict_using_params(first_station_dev, day_of_week, day_of_month, boolean_weekday, on_peak, hour,
                         associated_journey, associated_journey_dev_from_dep, associated_journey_first_stop,
                         associated_journey_second_stop):
    # read in the data from the database
    # 

def main():
    #print(check_on_peak(datetime.datetime(2022,1,5),"10:00"))
    #start = time.time()
    train_data = read_data_2()
    #train_data.to_csv('train_data.csv')

    #end = time.time()
    #duration = end - start
    #print(duration)
    #print("money shot")
    #find_times("202001028717288", "WDON","ESHER")

def find_times(rid,start,end):
    first_time = ""
    second_time = ""
    for path, subdirectory, files in os.walk("Train data"):
        for file_loc in glob.glob(path + "/*.csv"):
            print(file_loc)
            file = csv.reader(open(file_loc), delimiter=',')
            list_file = list(file)
            for row in list_file[1:]:
                if row[0] == rid:
                    if row[1] == start:
                        print(row)
                        if row[18]!="":  # retrieve the departure time if there is one
                            first_time = row[18]
                        if row[13]!="":
                            first_time = row[13]
                        elif row[17]!="":  # The time of passing is retrieved
                            first_time = row[17]
                        elif row[10] != "":  # expected passing time otherwise is retrieved
                            first_time = row[10]
                        print(first_time)
                    if row[1] == end:
                        if row[16]!="":  # retrieve the arrival time if there is one
                            second_time = row[16]
                        elif row[7]!="":  # expected time of arrival is retrieved
                            second_time = row[7]
                        elif row[17]!="":  # The time of passing is retrieved
                            second_time = row[17]
                        elif row[10] != "":  # expected passing time otherwise is retrieved
                            second_time = row[10]
                        print(second_time)
    time_difference = datetime.datetime.strptime(second_time, '%H:%M') - datetime.datetime.strptime(first_time, '%H:%M')
    print(time_difference.seconds,"is the amount of seconds between the two stops")



if __name__ == "__main__":
    main()