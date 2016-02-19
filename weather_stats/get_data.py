"""
Simple add to fetch weather information.
"""
import ConfigParser
import logging
import pkg_resources
import requests
import ruruki
import sys


LOGGER = logging.getLogger(__name__)
CONFIG = ConfigParser.SafeConfigParser()
CONFIG.read(
    pkg_resources.resource_filename(
        "weather_stats",
        "settings.cfg",
    )
)


def get_data(url, key, location):
    """
    Ftech the weather for the specified days.

    :param url: Base url where to fetch the data from.
    :type url: :class:`str`
    :param key: API key used for authentication.
    :type key: :class:`str`
    :param location: Location you want the weather for.
    :type location: :class:`str`
    :returns: Weather data received from parameter `url`.
    :rtype: :class:`dict`
    """
    payload = {
        "key": key,
        "q": location,
        "date": "today",
        "format": "json",
        "num_of_days": 7,
        "cc": "no",
    }
    request = requests.get(url, params=payload)
    return request.json()


def extract_data(weather_data, dump=None):
    """
    Extract interesting weather data.
    """
    graph = ruruki.create_graph()
    graph.add_vertex_constraint("DATE", "date")

    weather = weather_data["data"]["weather"]

    for data in weather:
        date = graph.get_or_create_vertex(
            "DATE",
            date=data["date"],
            name=data["date"],
            max_temp=int(data["maxtempC"]),
            min_temp=int(data["mintempC"]),
        )
        
        for hour in data["hourly"]:
            hour = graph.get_or_create_vertex(
                "HOUR",
                description=hour["weatherDesc"][0]["value"],
                name=hour["weatherDesc"][0]["value"],
                temp=int(hour["tempC"]),
                feelslike=int(hour["FeelsLikeC"]),
                pressure=int(hour["pressure"]),
                humidity=int(hour["humidity"]),
                weathercode=int(hour["weatherCode"]),
                windchill=int(hour["WindChillC"]),
            )
            graph.get_or_create_edge(
                hour, "HOUR", date
            )

    if dump:
        graph.dump(open(dump, "w"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    url = CONFIG.get("settings", "url")
    key = CONFIG.get("settings", "key")
    location = CONFIG.get("settings", "location")
    data = get_data(url, key, location)
    dump_file = sys.argv[1] if len(sys.argv) >= 2 else None
    extract_data(data, dump_file)
