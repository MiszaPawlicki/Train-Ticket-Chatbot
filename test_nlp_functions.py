import pytest
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

# infer_time

# infer_date

# infer_time_and_date

# yes_or_no

# check_questions

# full_details_response

# process_request

# generate_response

# predict_intent

