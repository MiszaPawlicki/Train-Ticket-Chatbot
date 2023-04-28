import csv
import datetime
import holidays

import pandas as pd


 # ensure that all the train data is in a folder ready before runnning this file!!
def read_data():


    file = csv.reader(open("Train data/2022/WATRLMN_WEYMTH_OD_a51_2022_1_1.csv"),delimiter = ',') #start of by reading in one file
    list_file = list(file)
    previous_rid = None
    train_array = []
    first_station_deviation = None
    previous_expected_departure_row = ""
    journey_first_stop_time = ""
    journey_second_stop_time = ""

    for row in list_file[1:]:  # read all the lines in the file - apart from the first line (column names)

        destination = find_destination(list_file, row[0])
        print(destination)
        rid_no = row[0]
        year = rid_no[0:4]
        month = rid_no[4:6]
        day_of_month = rid_no[6:8]
        time = row[18]
        print(rid_no[4:6])
        print("---")

        print(rid_no)
        date = datetime.datetime.strptime(year+month+day_of_month,'%Y%m%d').date()  # convert the date to a datetime object
        day_of_week = date.strftime('%A')
        day_of_week_no = date.weekday()
        if day_of_week_no < 5:
            weekday = True
        else:
            weekday = False
        print(day_of_week)
        on_peak = check_on_peak(date, time)
        print("time ->",time)

        if row[3] != row[18]:
            if first_station_deviation == None:
                first_station_deviation = row[1]
            print("departure is not the same at ", row[1])
        # find the associated journey expected departure time

        # if the rid number is the same as the last row that means it is the same train service.
        if previous_rid == row[0]:  # this is the same train service as the previous row
            print("y")
            if journey_first_stop_time == "" and row[2]!= "":  # predicted arrival for first stop
                journey_first_stop_time = row[2]
            elif journey_second_stop_time == "" and row[2] != "":
                journey_second_stop_time = row[2]



        elif previous_rid != row[0]:
            #TODO add the current values to the data set - this will mean when the nexr train information can
            # start to be read the previous data can be added to the db/df
            associated_journey_first_stop = journey_first_stop_time
            associated_journey_second_stop = journey_second_stop_time
            hour = datetime.datetime.strptime(time, '%H:%M').time()
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
                    print(associated_journey_dev_from_dep)
            print(first_station_deviation,"day:",day_of_month,day_of_week,weekday,on_peak,hour,"associated journey:",associated_journey,
                  "associated_journey_dev_from_dep:",associated_journey_dev_from_dep,"associated_journey_first_stop:",
                  associated_journey_first_stop,"associated_journey_second_stop:",associated_journey_second_stop)
            first_station_deviation = None  # make it null again after adding the row to the df/db

            previous_expected_departure_row = row




            # find these values:
                #first station deviation from departure time - done
                # day of the week   - done
                # day of the month  - done
                # Weekday/weekend  - done
                # on or off peak - done
                # hour of the day - done
                # associated journey - Look at data and see when the journey left before
                    # if the previous journey is on the same day:
                        #Find the time difference between the expected departure of the
                        # two where the expected depature is on the station  - this can be the associated journey
                # associated journey deviation from departure
                # associated journey first stop
                # associated journey second stop




            #[row[1],row[]]
            #train_array.append()


        previous_rid = row[0]



def check_on_peak(date,time):
    """

    :param date: a datetime object representing the date of departure of train
    :param time: a string object representing the time of departure of train
    :return: returns True if it is on peak (in a busy period), if not it returns False (off peak)
    """
    if date in holidays.country_holidays("GB"):
        print("in holidays")
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


    # copy the dataframe to another dataframe to store the information but useful to be able to use in a classifier
def find_destination(file, rid_no):
    for row in file[1:]:
        if row[0] == rid_no and row[10]!='':
            return row[1]







def main():
    #print(check_on_peak(datetime.datetime(2022,1,5),"10:00"))
    read_data()


if __name__ == "__main__":
    main()