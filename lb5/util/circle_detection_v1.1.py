#!/usr/bin/python                                                                                                                                                     
from PIL import Image, ImageDraw, ImageFont
import sys, time, random, math

def get_circle_borders(image, mask_type="sobel", border_bias = 100.0):
    indice_mascara = {
        "sobelx":[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
        "sobely":[[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]],
        "prewittx":[[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
        "prewitty":[[1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -1.0, -1.0]]
        }

    pic = image.load()
    pic_copy = (image.copy()).load()
    kernelx = indice_mascara[mask_type+'x']
    kernely = indice_mascara[mask_type+'y']

    #Line detection variables 
    image_matrix = dict()
    frequency = dict()
    for i in range(image.size[0]):
        for j in range(image.size[1]):

            gx, gy = (0.0, 0.0)
            kernel_len = len(kernelx[0])
            kernel_pos = 0
            for h in range(i-1, i+2):
                for l in range(j-1, j+2):
                    if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                        pixel = pic_copy[h, l]
                        pixel = max(pixel)/len(pixel)
                        gx += pixel*kernelx[int(kernel_pos/3)][kernel_pos%3]
                        gy += pixel*kernely[int(kernel_pos/3)][kernel_pos%3]
                        kernel_pos += 1

            gradiente = math.sqrt(math.pow(gx, 2) + math.pow(gy, 2))
            if math.fabs(gradiente) > border_bias:
                image_matrix[i,j] = math.atan2(gy, gx)+math.radians(90.0)

    return image_matrix

def circle_detection(circle_border, image, group_bias = 15, jump = 12):
    diagonal = math.sqrt(math.pow(image.size[0], 2) + math.pow(image.size[y], 2))

    for r in range(10, diagonal):
        centers_matrix = dict()
        frequency = dict()
        for c in circle_border.keys():
               # circle detection
            theta = circle_border[c]
            yc = (int( y - r * math.sin(theta))/jump)*jump
            xc = (int( x - r * math.cos(theta))/jump)*jump
            center = (xc, yc)

            centers_matrix = (xc, yc)
            if not theta in frequency:
                frequency[center] = 1
            else:
                frequency[center] += 1

def random_yellow():
    return (255, random.randint(100,255), random.randint(0, 50))

def draw_lines(image, frequency, circle_matrix):
    pic = image.load()
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 18)
    draw = ImageDraw.Draw(image)
    counter = 1
    colors = dict()
#    for i in frequency.keys():
#        colors[i] = random_yellow()
#        r = 2
#        draw.ellipse((i[0]-r, i[1]-r, i[0]+r, i[1]+r), fill=(0, 255, 0))
#        draw.text((i[0]+r+3, i[1]), ('C'+str(counter)), fill=(0, 255, 0), font=font)
#        print 'C'+str(counter)
#        counter += 1

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            try:
                if circle_matrix[i, j] in frequency:
                    pic[i,j] = (255, 0, 0)#colors[circle_matrix[i, j]]
                    pic[i,j] = colors[ircle_matrix[i, j]]
            except:
                pass
    return image

def detection(image_name, output="output.png"):
    image = Image.open(image_name)
    circle_border = get_circle_borders(image)
    circle_detection(circle_border, image)

    draw_lines(image, frequency, circle_matrix)

    image.save(output)

def main():
    before = time.time()
    detection(sys.argv[1])
    print "Tiempo de corrida:", (time.time() - before)

main()
