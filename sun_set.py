from sun_set_city import sun_set_city
from sun_set_cv import save_sun_set
import datetime

month_list = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", \
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
city = ["Voronezh", "Lipeck",]

# в yearcity храняться списки с горадами и в нутри разделение по месяцам
yearcity = [[] for i in range(len(city))]
year_dict = {}

# переменую year можно указать любое int, но в переменую month и day должны быть ровно 1
year = 2020
month = 1
day = 1
# создается только две даты
# указывается цифрами 1-пн, 2-вт, 3-ср, 4-чт, 5-пт, 6-сб, 7-вс
day1 = 1
day2 = 3
# можно указать сколько вычитать из часов 
day1_h = 0
day2_h = 0

for month in range(1, 13):
    mon_list_1 = [[] for i in range(len(city))]
    mon_list_2 = [[] for i in range(len(city))]
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
            for i in range(len(city)):
                # функция sun_set_city возврощает список [hour = str, minute = str]
                res = sun_set_city(city[i], data)
                res[0] = str(int(res[0]) - day1_h)
                if len(str(res[1])) == 1:
                    res[1] = "0"+res[1]
                mon_list_1[i].append((day_s, ":".join(res)))
        elif data.weekday() == day2:
            for i in range(len(city)):
                # функция sun_set_city возврощает список [hour = str, minute = str]
                res = sun_set_city(city[i], data)
                res[0] = str(int(res[0]) - day2_h)
                if len(str(res[1])) == 1:
                    res[1] = "0"+res[1]
                mon_list_2[i].append((day_s, ":".join(res)))
        day += 1
    # добовление месяц в список yearcity в города
    for i in range(len(city)):
        yearcity[i].append((mon_list_1[i], mon_list_2[i]))

# сохранение дат и заходов в файл output.txt
outFile = open("output.txt", 'w', encoding='utf8')
for c in range(len(yearcity)):
    print("Город ", city[c], file=outFile)
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
for c in range(len(yearcity)):
    save_sun_set(yearcity[c], city[c])
    print("Город ", city[c])
