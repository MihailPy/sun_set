

from sun_set_city import sun_set_city
from sun_set_cv import save_sun_set
import datetime

month_list = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
# city = ["Voronezh", "Lipeck", "Kirov", "Moscow"]
# city = ["Vladimir", "Viska", "Tyla","Razan","Voronezh", "Lipeck", "Kirov", "Bransk", "Cheboksari", "Luza", "Moscow","Mcensk", "NN", ]
city_ru = ["Воронеж", "Киров", "Липецк", "Брянск", "Чебоксары", "Луза", "Москва","Мценск","Н.Новгород","Рязань","Тула","Владимир",
"Выкса","С.Петербург","Калининград","Порхов","Волгоград","Тверь","Ярославль","Вельск","Вологда","Белгород","Бобров","Бобруйск",
"Владивосток","Горячий ключ","Гродно","Екатеринбург","Елец","Ессентуки","Иркутск","Казань","Краснодар","Крым","Курган","Курск",
"Ливны","Минеральные Воды","Минск","Мичуринск","Нижневартовск","Новосибирск","Омск","Пермь","Пятигорск","Самара","Саранск",
"Свободный","Сочи","СПб","Ставрополь","Стерлитамак","Таганрог","Томск","Улан-Уде","Уфа","Челябинск","Юрга","Якутск"]
# в yearcity храняться списки с горадами и в нутри разделение по месяцам
yearcity = [[] for i in range(len(city_ru))]
year_dict = {}

# переменую year можно указать любое int, но в переменую month и day должны быть ровно 1
year = 2023
month = 1
day = 1
# создается только две даты
# указывается цифрами 7-пн, 1-вт, 2-ср, 3-чт, 4-пт, 5-сб, 6-вс
day1 = 4
day2 = 5
# можно указать сколько вычитать из часов 
day1_h = 1
day2_h = 0

for month in range(1, 13):
    mon_list_1 = [[] for i in range(len(city_ru))]
    mon_list_2 = [[] for i in range(len(city_ru))]
    while True:
        # проверка есть ли дата токой нет то меняем день на 1
        try:
            data = datetime.date(year, month, day)
        except:
            day = 1
            break
        # month_s и day_s стоковоые month-месяц и day-день 
        month_s = str(month)
        day_s = str(day)
        if len(month_s) == 1:
            month_s = "0"+month_s
        if len(day_s) == 1:
            day_s = "0"+day_s
        # спрашиваем заход только на указаные в переменны \
        # day1 и day2 дни недели заход солнца
        if data.weekday() == day1:
            for i in range(len(city_ru)):
                # функция sun_set_city возврощает список [hour = str, minute = str]
                res = sun_set_city(i+1, data)
                res[0] = str(int(res[0]) - day1_h)
                if len(str(res[1])) == 1:
                    res[1] = "0"+res[1]
                mon_list_1[i].append((day_s, ":".join(res[0:2])))
        elif data.weekday() == day2:
            for i in range(len(city_ru)):
                # функция sun_set_city возврощает список [hour = str, minute = str]
                res = sun_set_city(i+1, data)
                res[0] = str(int(res[0]) - day2_h)
                if len(str(res[1])) == 1:
                    res[1] = "0"+res[1]
                mon_list_2[i].append((day_s, ":".join(res[0:2])))
        day += 1
    # добовление месяц в список yearcity в города
    for i in range(len(city_ru)):
        yearcity[i].append((mon_list_1[i], mon_list_2[i]))

# сохранение дат и заходов в файл output.txt
outFile = open("output.txt", 'w', encoding='utf8')
for c in range(len(yearcity)):
    print(year, file=outFile)
    print("Город ", city_ru[c], file=outFile)
    mu = 0
    for m in yearcity[c]:
        pt = []
        sb = []
        for d in m[0]:
            pt.append("  ".join(d))
        for d in m[1]:
            sb.append("  ".join(d))
        print(month_list[mu], file=outFile)
        mu += 1
        print("   ".join(pt), file=outFile)
        print("   ".join(sb), file=outFile)
        print("  ", file=outFile)
    print("  ", file=outFile)
outFile.close()

# сохранение дат с заходом в изображении
for c in range(len(city_ru)):
# for c in range(0,1):
    data = datetime.date(year, month, day)
    save_sun_set(yearcity[c], c+1, city_ru[c])
    print("Город ", city_ru[c], c+1)

