from PIL import Image, ImageDraw, ImageFont
start_pos_x_1 = [92,860,1623]
start_pos_x_2 = [213,978,1745]
start_pos_y = [805,1500,2195,2890]

def save_sun_set(yearcity, city, name_ru):
    print(name_ru)
    color = (0,0,0,0)
    img = Image.open("graf.jpg", "r")
    img_w, img_h = img.size
    image = Image.new('RGBA', (2384, 3508), color)
    bg_w, bg_h = image.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    image.paste(img, offset)
    font = ImageFont.truetype("cambriab.ttf", size=67)
    font_city = ImageFont.truetype("cambriab.ttf", size=140)
    imgDrawer = ImageDraw.Draw(image)
    imgDrawer.text((90, 200), name_ru, font=font_city, fill=(0,0,0))
    imgDrawer.text((90, 340), "2023", font=font_city, fill=(0,0,0))
    m = 0
    for y in start_pos_y:
        for x in range(3):
            day1 = yearcity[m][0]
            day2 = yearcity[m][1]
            stp = {"x":start_pos_x_1[x],"x2":start_pos_x_2[x],"y":y}
            if int(day1[0][0]) > int(day2[0][0]):
                stp["y"] += 75
            for day in day1:
                imgDrawer.text((stp["x"], stp["y"]), day[0], font=font, fill=(151, 55, 53))
                imgDrawer.text((stp["x2"], stp["y"]), day[1], font=font, fill=(28, 64, 108))
                stp["y"] += 75
            stp = {"x":start_pos_x_1[x]+330,"x2":start_pos_x_2[x]+330,"y":y}
            for day in day2:
                imgDrawer.text((stp["x"], stp["y"]), day[0], font=font, fill=(151, 55, 53))
                imgDrawer.text((stp["x2"], stp["y"]), day[1], font=font, fill=(28, 64, 108))
                stp["y"] += 75

            m += 1
        
    image.save("file/"+str(city)+"_"+name_ru+"_graf.png")