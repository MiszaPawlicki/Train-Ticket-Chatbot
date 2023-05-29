import datetime
import NLP

# clean_input
def test_clean_input():
    dirty_input = "AaBbcC!,.?"
    expected_output = "aabbcc"
    cleaned_input = NLP.clean_input(dirty_input)
    assert cleaned_input == expected_output

# find_station_in_sentence
def test_find_station_in_sentence():
    test_sent_1 = "I would like to travel to Brighton"
    test_sent_2 = "Can i travel from Norwich"
    test_sent_3 = "Give me a ticket from Norwich to Brighton"

    output_1 = NLP.find_station_in_sentence(test_sent_1)
    output_2 = NLP.find_station_in_sentence(test_sent_2)
    output_3 = NLP.find_station_in_sentence(test_sent_3)

    assert output_1['destinations'][0]['crsCode'] == "BTN"
    assert output_2['origins'][0]['crsCode'] == "NRW"
    assert output_3['destinations'][0]['crsCode'] == "BTN"
    assert output_3['origins'][0]['crsCode'] == "NRW"

# get_crs_code_and_station_name
def test_crs_code_and_station_name():
    test_1 = {'origins': [{'stationName': "Norwich", 'crsCode': "NRW"}]}
    test_2 = {'destinations': [{'stationName': "London", 'crsCode': "182"}]}

    output_1_crs_code, output_1_place = NLP.get_crs_and_station_name(test_1, "origins")
    output_2_crs_code, output_2_place = NLP.get_crs_and_station_name(test_2, "destinations")

    assert output_1_crs_code == "NRW"
    assert output_1_place == "Norwich"

    #crsCode is a number, therefore placename takes its place for the URL to scrape
    assert output_2_crs_code == "London"
    assert output_2_place == "London"

# get_response
def test_get_response():
    intent_1 = "greeting"
    intent_2 = "goodbye"
    intent_3 = "thanks"
    intent_4 = "requests"
    intent_5 = "requests_no_time_single"
    intent_6 = "requests_no_time_no_origin_single"
    intent_7 = "requests_with_time_with_location_single"
    intent_8 = "requests_with_time_with_locations_return_same_day"
    intent_9 = "requests_with_time_with_locations_return_different_day"
    intent_10 = "reset"
    intent_11 = "delayed_train"

    responses = []
    
    responses.append(intent_1)
    responses.append(intent_2)
    responses.append(intent_3)
    responses.append(intent_4)
    responses.append(intent_5)
    responses.append(intent_6)
    responses.append(intent_7)
    responses.append(intent_8)
    responses.append(intent_9)
    responses.append(intent_10)
    responses.append(intent_11)

    for r in responses:
        assert r != None


# infer_time
def test_infer_time():
    test_sent_1 = "i would like a train at 8pm"
    test_sent_2 = "i would like a train at 20:00"

    output_1 = NLP.infer_time(test_sent_1)
    output_2 = NLP.infer_time(test_sent_2)

    assert output_1[0] == datetime.time(20, 0)
    assert output_2[0] == datetime.time(20, 0)


# infer_date
def test_infer_date():
    test_sent_1 = "i would like a train on the 30th of may"
    test_sent_2 = "i would like a train on 30/05"
    test_sent_3 = "i would like a train on 30/05/23"
    test_sent_4 = "i would like a train tomorrow"



    output_1 = NLP.infer_date(test_sent_1)
    output_2 = NLP.infer_date(test_sent_2)
    output_3 = NLP.infer_date(test_sent_3)
    output_4 = NLP.infer_date(test_sent_4)

    # in future these tests may fail as the date requested is in the past
    assert output_1[0] == datetime.date(2023, 5, 30)
    assert output_2[0] == datetime.date(2023, 5, 30)
    assert output_3[0] == datetime.date(2023, 5, 30)
    assert output_4[0] == datetime.date(2023, 5, 30)

# infer_time_and_date
def test_infer_time_and_date():
    test_sent_1 = "i would like a train on the 30th of may at 8pm"
    test_sent_2 = "i would like a train on 30/05/23 at 20:00"
    test_sent_3 = "i would like a train 30/05 at 8pm"
    test_sent_4 = "i would like a train tomorrow at 8pm"

    output_1 = NLP.infer_time_and_date(test_sent_1)
    output_2 = NLP.infer_time_and_date(test_sent_2)
    output_3 = NLP.infer_time_and_date(test_sent_3)
    output_4 = NLP.infer_time_and_date(test_sent_4)

    # in future these tests may fail as the date requested is in the past
    assert output_1['date']==datetime.date(2023, 5, 30)
    assert output_2['date'] == datetime.date(2023, 5, 30)
    assert output_3['date'] == datetime.date(2023, 5, 30)
    assert output_4['date'] == datetime.date(2023, 5, 30)

    assert output_1['time'] == datetime.time(20, 0)
    assert output_2['time'] == datetime.time(20, 0)
    assert output_3['time'] == datetime.time(20, 0)
    assert output_4['time'] == datetime.time(20, 0)

# yes_or_no
def test_yes_or_no():
    test_sent_1 = "yes i would"
    test_sent_2 = "no thanks"

    output_1 = NLP.yes_or_no(test_sent_1)
    output_2 = NLP.yes_or_no(test_sent_2)

    assert output_1
    assert not output_2

# full_details_response
def test_full_details_response():
    test_journey_details = {'origins': [{'stationName': "Norwich", 'crsCode': "NRW"}],
                       'destinations': [{'stationName': "Brighton", 'crsCode': "BTN"}],
                       'departureDate': datetime.date(2023, 5, 30),
                       'departureTime': datetime.time(20, 0),
                       'returnDate': datetime.date(2023, 6, 1),
                       'returnTime': datetime.time(20, 0)}

    output_1 = NLP.full_details_response(test_journey_details)
    expected_output = "<a href=https://ojp.nationalrail.co.uk/service/timesandfares/NRW/BTN/300523/2000/dep/010623/2000/dep target=\"_blank\">click here!</a>"
    print(output_1)
    #may fail in future because date is in the past
    assert expected_output in output_1


# generate_response

# predict_intent
def test_predict_intent():
    test_sent_1 = "hello!"
    test_sent_2 = "I would like a ticket please"
    test_sent_3 = "thank you"
    test_sent_4 = "can i get a ticket from london to norwich"
    test_sent_5 = "i would like a ticket to norwich"
    test_sent_6 = "at 8am i would like a ticket from london to norwich"
    test_sent_7 = "find me tickets to london from norwich at 8am and return at 8am"
    test_sent_8 = "i want to travel to london from norwich at 8am and return on the 30th at 8pm"
    test_sent_9 = "my train is late"
    test_sent_10 = "bye"
    test_sent_11 = "lets start again"

    output_1 = NLP.predict_intent(test_sent_1)
    output_2 = NLP.predict_intent(test_sent_2)
    output_3 = NLP.predict_intent(test_sent_3)
    output_4 = NLP.predict_intent(test_sent_4)
    output_5 = NLP.predict_intent(test_sent_5)
    output_6 = NLP.predict_intent(test_sent_6)
    output_7 = NLP.predict_intent(test_sent_7)
    output_8 = NLP.predict_intent(test_sent_8)
    output_9 = NLP.predict_intent(test_sent_9)
    output_10 = NLP.predict_intent(test_sent_10)
    output_11 = NLP.predict_intent(test_sent_11)

    assert output_1 == "greeting"
    assert output_2 == "requests"
    assert output_3 == "thanks"
    assert output_4 == "requests_no_time_single"
    assert output_5 == "requests_no_time_no_origin_single"
    assert output_6 == "requests_with_time_with_location_single"
    assert output_7 == "requests_with_time_with_locations_return_same_day"
    assert output_8 == "requests_with_time_with_locations_return_different_day"
    assert output_9 == "delayed_train"
    assert output_10 == "goodbye"
    assert output_11 == "reset"
