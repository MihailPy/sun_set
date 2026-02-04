import datetime
from astral import LocationInfo
from astral.sun import sun, sunset
import zoneinfo
print(zoneinfo.available_timezones())


def sun_set_city(city, date):
    city_ru = ["Воронеж", "Киров", "Липецк", "Брянск", "Чебоксары", "Луза", "Москва","Мценск","Н.Новгород","Рязань","Тула","Владимир","Выкса","С.Петербург","Калининград","Порхов","Волгоград","Тверь","Ярославль","Вельск","Вологда","Белгород","Бобров","Бобруйск","Владивосток","Горячий ключ","Гродно","Екатеринбург","Елец","Ессентуки","Иркутск","Казань","Краснодар","Крым","Курган","Курск","Ливны","Минеральные Воды","Минск","Мичуринск","Нижневартовск","Новосибирск","Омск","Пермь","Пятигорск","Самара","Саранск","Свободный","Сочи","СПб","Ставрополь","Стерлитамак","Таганрог","Томск","Улан-Уде","Уфа","Челябинск","Юрга","Якутск"]
    # добавление в библиотеку новых города по широте
    if city == 1:
        # Воронеж
        l = LocationInfo()
        l.name = '1'
        l.region = 'Russia'
        l.latitude = 51.67204
        l.longitude = 39.1843
        l.timezone = 'Europe/Moscow'
        l.elevation = None

    elif city == 2:
        # Киров
        l = LocationInfo()
        l.name = '2'
        l.region = 'Russia'
        l.latitude = 58.38
        l.longitude = 49.42
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 3:
        # Липецк
        l = LocationInfo()
        l.name = '3'
        l.region = 'Russia'
        l.latitude = 52.60
        l.longitude = 39.48
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 4:
        # Брянск
        l = LocationInfo()
        l.name = '4'
        l.region = 'Russia'
        l.latitude = 53.15
        l.longitude = 34.22
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 5:
        # Чебоксары
        l = LocationInfo()
        l.name = '5'
        l.region = 'Russia'
        l.latitude = 56.09
        l.longitude = 47.15
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 6:
        # Луза
        l = LocationInfo()
        l.name = '6'
        l.region = 'Russia'
        l.latitude = 60.39
        l.longitude = 47.10
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 7:
        # Москва
        l = LocationInfo()
        l.name = '7'
        l.region = 'Russia'
        l.latitude = 55.45
        l.longitude = 37.35
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 8:
        # Мценск
        l = LocationInfo()
        l.name = '8'
        l.region = 'Russia'
        l.latitude = 53.17
        l.longitude = 36.35
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 9:
        # Н.Новгород
        l = LocationInfo()
        l.name = '9'
        l.region = 'Russia'
        l.latitude = 56.20
        l.longitude = 44.0
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 10:
        # Рязань
        l = LocationInfo()
        l.name = '10'
        l.region = 'Russia'
        l.latitude = 54.37
        l.longitude = 39.37
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 11:
        # Тула
        l = LocationInfo()
        l.name = '11'
        l.region = 'Russia'
        l.latitude = 54.12
        l.longitude = 37.34
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 12:
        # Владимир
        l = LocationInfo()
        l.name = '12'
        l.region = 'Russia'
        l.latitude = 56.10
        l.longitude = 40.25
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 13:
        # Выкса
        l = LocationInfo()
        l.name = '13'
        l.region = 'Russia'
        l.latitude = 55.18
        l.longitude = 42.11
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 14:
        # С.Петербург
        l = LocationInfo()
        l.name = '14'
        l.region = 'Russia'
        l.latitude = 59.52
        l.longitude = 30.25
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 15:
        # Калининград
        l = LocationInfo()
        l.name = '15'
        l.region = 'Russia'
        l.latitude = 54.43
        l.longitude = 20.30
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 16:
        # Порхов
        l = LocationInfo()
        l.name = '16'
        l.region = 'Russia'
        l.latitude = 57.48
        l.longitude = 28.30
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 17:
        # Волгоград
        l = LocationInfo()
        l.name = '17'
        l.region = 'Russia'
        l.latitude = 48.44
        l.longitude = 44.25
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 18:
        # Тверь
        l = LocationInfo()
        l.name = '18'
        l.region = 'Russia'
        l.latitude = 56.48
        l.longitude = 35.50
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 19:
        # Ярославль
        l = LocationInfo()
        l.name = '19'
        l.region = 'Russia'
        l.latitude = 57.41
        l.longitude = 39.46
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 20:
        # Вельск
        l = LocationInfo()
        l.name = '20'
        l.region = 'Russia'
        l.latitude = 61.05
        l.longitude = 42.05
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 21:
        # Вологда
        l = LocationInfo()
        l.name = '21'
        l.region = 'Russia'
        l.latitude = 59.12
        l.longitude = 39.55
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 22:
        # Белгород
        l = LocationInfo()
        l.name = '22'
        l.region = 'Russia'
        l.latitude, l.longitude = 50.6207, 36.5802
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 23:
        # Бобров
        l = LocationInfo()
        l.name = '23'
        l.region = 'Russia'
        l.latitude, l.longitude = 51.0545, 40.0159
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 24:
        # Бобруйск
        l = LocationInfo()
        l.name = '24'
        l.region = 'Russia'
        l.latitude, l.longitude = 53.1384, 29.2214
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 25:
        # Владивосток
        l = LocationInfo()
        l.name = '25'
        l.region = 'Russia'
        l.latitude, l.longitude = 43.1056, 131.874
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 26:
        # Горячий ключ
        l = LocationInfo()
        l.name = '26'
        l.region = 'Russia'
        l.latitude, l.longitude = 44.3750, 39.0748
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 27:
        # Гродно
        l = LocationInfo()
        l.name = '27'
        l.region = 'Russia'
        l.latitude, l.longitude = 53.6884, 23.8258
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 28:
        # Екатеринбург
        l = LocationInfo()
        l.name = '28'
        l.region = 'Russia'
        l.latitude, l.longitude = 56.8519, 60.6122
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 29:
        # Елец (Афанасьево, Долгоруково)
        l = LocationInfo()
        l.name = '29'
        l.region = 'Russia'
        l.latitude, l.longitude = 52.6237, 38.5017
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 30:
        # Ессентуки
        l = LocationInfo()
        l.name = '30'
        l.region = 'Russia'
        l.latitude, l.longitude = 44.0444, 42.8606
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 31:
        # Иркутск
        l = LocationInfo()
        l.name = '31'
        l.region = 'Russia'
        l.latitude, l.longitude = 52.2978, 104.296
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 32:
        # Казань
        l = LocationInfo()
        l.name = '32'
        l.region = 'Russia'
        l.latitude, l.longitude = 55.7887, 49.1221
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 33:
        # Краснодар
        l = LocationInfo()
        l.name = '33'
        l.region = 'Russia'
        l.latitude, l.longitude = 45.0448, 38.976
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 34:
        # Крым
        l = LocationInfo()
        l.name = '34'
        l.region = 'Russia'
        l.latitude, l.longitude = 45.0368, 35.3779
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 35:
        # Курган
        l = LocationInfo()
        l.name = '35'
        l.region = 'Russia'
        l.latitude, l.longitude = 55.45, 65.3333
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 36:
        # Курск
        l = LocationInfo()
        l.name = '36'
        l.region = 'Russia'
        l.latitude, l.longitude = 51.7373, 36.1874
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 37:
        # Ливны
        l = LocationInfo()
        l.name = '37'
        l.region = 'Russia'
        l.latitude, l.longitude = 52.4253, 37.6069
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 38:
        # Минеральные Воды
        l = LocationInfo()
        l.name = '38'
        l.region = 'Russia'
        l.latitude, l.longitude = 44.2103, 43.1353
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 39:
        # Минск
        l = LocationInfo()
        l.name = '39'
        l.region = 'Russia'
        l.latitude, l.longitude = 53.9, 27.5667
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 40:
        # Мичуринск
        l = LocationInfo()
        l.name = '40'
        l.region = 'Russia'
        l.latitude, l.longitude = 52.8978, 40.4907
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 41:
        # Нижневартовск
        l = LocationInfo()
        l.name = '41'
        l.region = 'Russia'
        l.latitude, l.longitude = 60.9344, 76.5531
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 42:
        # Новосибирск
        l = LocationInfo()
        l.name = '42'
        l.region = 'Russia'
        l.latitude, l.longitude = 55.0415, 82.9346
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 43:
        # Омск
        l = LocationInfo()
        l.name = '43'
        l.region = 'Russia'
        l.latitude, l.longitude = 54.9924, 73.3686
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 44:
        # Пермь
        l = LocationInfo()
        l.name = '44'
        l.region = 'Russia'
        l.latitude, l.longitude = 58.0105, 56.2502
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 45:
        # Пятигорск
        l = LocationInfo()
        l.name = '45'
        l.region = 'Russia'
        l.latitude, l.longitude = 44.0486, 43.0594
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 46:
        # Самара
        l = LocationInfo()
        l.name = '46'
        l.region = 'Russia'
        l.latitude, l.longitude = 53.2001, 50.15
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 47:
        # Саранск
        l = LocationInfo()
        l.name = '47'
        l.region = 'Russia'
        l.latitude, l.longitude = 54.1838, 45.1749
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 48:
        # Свободный
        l = LocationInfo()
        l.name = '48'
        l.region = 'Russia'
        l.latitude, l.longitude = 51.3753, 128.141
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 49:
        # Сочи
        l = LocationInfo()
        l.name = '49'
        l.region = 'Russia'
        l.latitude, l.longitude = 43.5992, 39.7257
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 50:
        # СПб
        l = LocationInfo()
        l.name = '50'
        l.region = 'Russia'
        l.latitude, l.longitude = 59.9386, 30.3141
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 51:
        # Ставрополь
        l = LocationInfo()
        l.name = '51'
        l.region = 'Russia'
        l.latitude, l.longitude = 45.0428, 41.9734
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 52:
        # Стерлитамак
        l = LocationInfo()
        l.name = '52'
        l.region = 'Russia'
        l.latitude, l.longitude = 53.6246, 55.9501
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 53:
        # Таганрог
        l = LocationInfo()
        l.name = '53'
        l.region = 'Russia'
        l.latitude, l.longitude = 47.2362, 38.8969
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 54:
        # Томск
        l = LocationInfo()
        l.name = '54'
        l.region = 'Russia'
        l.latitude, l.longitude = 56.4977, 84.9744
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 55:
        # Улан-Уде
        l = LocationInfo()
        l.name = '55'
        l.region = 'Russia'
        l.latitude, l.longitude = 51.8272, 107.606
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 56:
        # Уфа
        l = LocationInfo()
        l.name = '56'
        l.region = 'Russia'
        l.latitude, l.longitude = 54.7431, 55.9678
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 57:
        # Челябинск
        l = LocationInfo()
        l.name = '57'
        l.region = 'Russia'
        l.latitude, l.longitude = 55.154, 61.4291
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 58:
        # Юрга
        l = LocationInfo()
        l.name = '59'
        l.region = 'Russia'
        l.latitude, l.longitude = 55.7143, 84.9214
        l.timezone = 'Europe/Moscow'
        l.elevation = None
    elif city == 59:
        # Якутск
        l = LocationInfo()
        l.name = '60'
        l.region = 'Russia'
        l.latitude, l.longitude = 62.0339, 129.733
        l.timezone = 'Europe/Moscow'
        l.elevation = None

    # print(sunset(l.observer, date, tzinfo=l.timezone).time().hour)
    # спрашиваем у Astral восколько заход
    sun_set = sunset(l.observer, date, tzinfo=l.timezone)
    # print(sun_set)
    # возврощаем список [hour = str, minute = str]
    resultSunSet = [str(sun_set.time().hour), \
        str(sun_set.time().minute)]

    return resultSunSet

