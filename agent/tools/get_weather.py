from random import randint


def get_weather(location: str) :
    """Get the weather in a location"""
    return {
        "location": location,
        "temperature": 72 + randint(10,25)
    }