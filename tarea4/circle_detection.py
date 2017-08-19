#!/usr/bin/python                                                                                                                                                     
from PIL import Image, ImageDraw, ImageFont
import sys, time, random, math
from filtros import Filtros

def calculate_circle_center(picx, picy, image, salto = 10, bias=10.0):
    frequency = dict()
    circle_matrix = dict()

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            (Rx, Gx, Bx) = picx[i,j]
            (Ry, Gy, By) = picy[i,j]

            gx = float(Rx+Gx+Bx)/3
            gy = float(Ry+Gy+By)/3

            gradiente = math.sqrt(math.pow(gx, 2) + math.pow(gy, 2))
            if gradiente < -1*bias or gradiente > bias:
                cos_theta = (gx/gradiente)
                sin_theta = (gy/gradiente)
                theta = math.atan2(gy, gx)
                r = 60

#                print cos_theta, sin_theta
#                centro = (int(i - r * cos_theta), int(j - r * sin_theta))
                centro = (int( i - r * math.cos(theta+math.radians(90.0))), int( j - r * math.sin(theta+math.radians(90.0))))
                centro = ((centro[0]/salto)*salto, (centro[1]/salto)*salto)
                circle_matrix[i,j] = centro

                if not centro in frequency:
                    frequency[centro] = 1
                else:
                    frequency[centro] += 1
            else:
                circle_matrix[i, j] = None
    return circle_matrix, frequency

def random_yellow():
    return (255, random.randint(100,255), random.randint(0, 50))

def draw_lines(image, frequency, circle_matrix):
    pic = image.load()
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 18)
    draw = ImageDraw.Draw(image)
    counter = 1
    colors = dict()
    for i in frequency.keys():
        colors[i] = random_yellow()
        r = 2
        draw.ellipse((i[0]-r, i[1]-r, i[0]+r, i[1]+r), fill=(0, 255, 0))
        draw.text((i[0]+r+3, i[1]), ('C'+str(counter)), fill=(0, 255, 0), font=font)
        print 'C'+str(counter)
        counter += 1

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if circle_matrix[i, j] in frequency:
                try:
#                    pic[circle_matrix[i,j]] = (255, 0, 0)
                    pic[i,j] = colors[circle_matrix[i, j]]
                except:
                    pass
    return image

def circle_detection(image_name, output="output.png"):
    f = Filtros()
    imagex = f.aplicar_mascara(image_name, ["sobelx"], [1.0/10.0], cmd="i")
    imagey  = f.aplicar_mascara(image_name, ["sobely"], [1.0/10.0], cmd="i")

#    imagex = f.aplicar_mascara(image_name, ["prewittx"], [1.0/10.0], cmd="i")
#    imagey  = f.aplicar_mascara(image_name, ["prewitty"], [1.0/10.0], cmd="i")

    image = Image.open(image_name)
    salto = 30
    circle_matrix, frequency = calculate_circle_center(imagex, imagey,  image, salto = salto, bias=10.0)

    for i in frequency.keys():
        if frequency[i] < salto*8:
            frequency.pop(i)
        else:
            print frequency[i], i

    draw_lines(image, frequency, circle_matrix)
    image.save(output)

def main():
    circle_detection(sys.argv[1])

main()
