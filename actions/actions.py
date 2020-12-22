# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"


#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
#from rasa_sdk.executor import CollectingDispatcher
import json
import requests

class ZomatoLocationAndCuisine:
    def _init(self):
        self.api_key = "eb2174b4576dca6630d573916db78db2"
        self.base_url = "https://developers.zomato.com/api/v2.1/"

    def get_LocationId(self, location):

        queryString = {"query": location}

        headers = {'Accept' : 'application/json', 'user-key':'self.api_key'}

        res = requests.get(self.base_url + "locations", params=queryString, headers=headers)

        data = json.loads(res)

        if len(data['location_suggestions']) == 0:
            raise Exception('invalid_location')

        location_id = data['city_id']
        entity_type = data['entity_type']
        return location_id, entity_type

    def get_cuisineId(self, location_id):

        headers = {'Accept': 'application/json', 'user-key': self.api_key}

        queryString = {"query": location_id}

        res = requests.get(self.base_url + "cuisines", params=queryString, headers=headers)

        cuisines = json.loads(res)

        if len(cuisines['cuisine_id']) == 0:
            raise Exception("Invalid Cuisine, Try another cuisine")

        cuisine_id = cuisines['cuisine_id']
        return cuisine_id

    def get_restaurants(self,location,cuisine):

        location_id, entity_type = self.get_LocationId(location)
        cuisine_id = self.get_cuisineId(location_id)

        queryString = {
            "entity_type": entity_type,
            "entity_id": location_id,
            "cuisines": cuisine_id,
            "count": 5
        }

        headers = {'Accept': 'application/json', 'user-key': self.api_key}
        res = requests.get(self.base_url + "search", params=queryString, headers=headers)

        restaurant_payload = json.loads(res)
        restaurants = restaurant_payload["restautants"]
        restaurant_names = []
        for i in restaurants:
            restaurant_names.append(i['names'])

        return restaurant_names

class ActionShowRestaurants(Action):

    def name(self):
        return "action_show_restaurants"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:

        location = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')

        zo = ZomatoLocationAndCuisine()
        list_of_all_restaurants = zo.get_restaurants(str(location), str(cuisine))

        if len(list_of_all_restaurants) ==0 :
            dispatcher.utter_message("Sorry no such restaurant of " + cuisine + " available at " + location + ". Try looking for some other cuisine.")

        else:
            list_of_all_restaurants_json = json.dumps(list_of_all_restaurants)
            dispatcher.utter_message(json_message=list_of_all_restaurants_json)

        return []