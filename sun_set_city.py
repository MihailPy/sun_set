import datetime
from astral import Astral, Location

def sun_set_city(city, date):
    # добавление в библиотеку новых города по широте
    if city == "Voronezh":
        l = Location()
        l.name = 'Voronezh'
        l.region = 'Russia'
        l.latitude = 51.69
        l.longitude = 39.05
        l.timezone = 'Europe/Moscow'
        l.elevation = 50
        l.sun()
    elif city == "Lipeck":
        l = Location()
        l.name = 'Lipeck'
        l.region = 'Russia'
        l.latitude = 52.60
        l.longitude = 39.48
        l.timezone = 'Europe/Moscow'
        l.elevation = 0
        l.sun()
    
    # спрашиваем у Astral восколько заход
    sun = l.sun(date=date, local=True)
    # возврощаем список [hour = str, minute = str]
    resultSunSet = [str(sun['sunset'].time().hour), \
        str(sun['sunset'].time().minute)]

    return resultSunSet
