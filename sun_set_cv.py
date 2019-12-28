from PIL import Image, ImageDraw, ImageFont
start_pos_x_1 = [85,885,1683]
start_pos_x_2 = [213,1008,1805]
start_pos_y = [693,1420,2140,2865]

def save_sun_set(yearcity, city):
    color = (0,0,0,0)
    image = Image.new('RGBA', (2384, 3508), color)
    font = ImageFont.truetype("cambriab.ttf", size=68)
    imgDrawer = ImageDraw.Draw(image)
    m = 0
    for y in start_pos_y:
        for x in range(3):
            day1 = yearcity[m][0]
            day2 = yearcity[m][1]
            stp = {"x":start_pos_x_1[x],"x2":start_pos_x_2[x],"y":y}
            if int(day1[0][0]) > int(day2[0][0]):
                stp["y"] += 80
            for day in day1:
                imgDrawer.text((stp["x"], stp["y"]), day[0], font=font, fill=(151, 55, 53))
                imgDrawer.text((stp["x2"], stp["y"]), day[1], font=font, fill=(28, 64, 108))
                stp["y"] += 80
            stp = {"x":start_pos_x_1[x]+330,"x2":start_pos_x_2[x]+330,"y":y}
            for day in day2:
                imgDrawer.text((stp["x"], stp["y"]), day[0], font=font, fill=(151, 55, 53))
                imgDrawer.text((stp["x2"], stp["y"]), day[1], font=font, fill=(28, 64, 108))
                stp["y"] += 80

            m += 1
        
    image.save("file/"+city+"_graf.png")