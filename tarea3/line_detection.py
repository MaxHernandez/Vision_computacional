#!/usr/bin/python                                                                                                                                                     
from PIL import Image
import sys, time, random, math
from filtros import Filtros

def calculate_line_values(picx, picy, image, saltos_ro=30, saltos_angulo=12, bias=10.0):
    frequency = dict()
    line_matrix = dict()

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            (Rx, Gx, Bx) = picx[i,j]
            (Ry, Gy, By) = picy[i,j]

            gx = float(Rx+Gx+Bx)/3
            gy = float(Ry+Gy+By)/3

            if (gx < -1*bias or gx > bias) or (gy < -1*bias or gy > bias):

                angulo = 0.0
                if gx > 0.0 and gy == 0.0:
                    angulo = 0.0
                elif gx < 0.0 and gy == 0.0:
                    angulo = 180.0
                if gx == 0.0 and gy > 0.0:
                    angulo = 90.0
                elif gx == 0.0 and gy < 0.0:
                    angulo = 270.0
                else:
                    angulo = (int(math.degrees( math.atan(gy/gx) )  )/saltos_angulo)*saltos_angulo

                ro = (int( (i*math.cos(angulo)) + (j*math.sin(angulo))) /saltos_ro)*saltos_ro
                line_matrix[i,j] = (angulo, ro)

                if not (angulo, ro) in frequency:
                    frequency[(angulo, ro)] = 1
                else:
                    frequency[(angulo, ro)] += 1
            else:
                line_matrix[i, j] = None

    return line_matrix, frequency

def draw_lines(image, frequency, line_matrix):
    pic = image.load()
    pixeles_verticales = 0
    pixeles_horizontales = 0
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if line_matrix[i, j] in frequency:
                if line_matrix[i, j][0] == 0.0 or line_matrix[i, j][0] == 180.0:
                    pixeles_horizontales += 1
                    pic[i,j] = (255, 0, 0)
                if line_matrix[i, j][0] == 90.0 or line_matrix[i, j][0] == 270.0:
                    pixeles_verticales += 1
                    pic[i,j] = (0, 0, 255)

    print "Numero de pixeles Horizontales:", pixeles_horizontales
    print "Numero de pixeles verticales:", pixeles_verticales
    return image

def line_detection(image_name, output="output.png"):
    f = Filtros()
    imagex = f.aplicar_mascara(image_name, ["prewittx"], [1.0/18.0], cmd="i")
    imagey  = f.aplicar_mascara(image_name, ["prewitty"], [1.0/18.0], cmd="i")

    image = Image.open(image_name)
    line_matrix, frequency = calculate_line_values(imagex, imagey,  image, saltos_ro=5, saltos_angulo=5, bias=10.0)

    f = list()
    for i in frequency.keys():
        if frequency[i] < 5:
            frequency.pop(i)
        else:
            f.append(frequency[i])
    f.sort()

    draw_lines(image, frequency, line_matrix)
    image.save(output)

def main():
    line_detection(sys.argv[1])

main()
