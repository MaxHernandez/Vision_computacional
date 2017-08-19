#!/usr/bin/python   

from time import time
from sys import argv
import math
from PIL import Image, ImageOps, ImageDraw
from subprocess import call

indice_mascara = {
    "sobelx":[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
    "sobely":[[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]],
    "sobel5x":[[1, 2, 0, -2, -1], [4, 8, 0, -8, -4], [6, 12, 0, -12, -6], [4, 8, 0, -8, -4], [1, 2, 0, -2, -1]],
    "sobel5y":[[-1, -4, -6, -4, -1], [-2, -8, -12, -8, -2], [0, 0, 0, 0, 0], [2, 8, 12, 8, 2], [1, 4, 6, 4, 1]],
    "prewittx":[[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
    "prewitty":[[1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -1.0, -1.0]]
    }

def calculate_line_values(image, bias=10.0, mask = 'sobel'):
    pic = image.load()
    frequency = dict()
    line_matrix = dict()
    votos = dict()

    kernelx = indice_mascara[mask+'x']
    kernely = indice_mascara[mask+'y']
    kernel_len = len(kernelx[0])
    space = int(kernel_len/ 2)
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            
            kernel_pos = 0
            gx, gy = (0.0, 0.0)
            c = 0
            for h in range(i-space, i+space+1):
                for l in range(j-space, j+space+1):
                    if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                        pixel = pic[h, l]
                        c += 1
                        gx += (pixel[0]*kernelx[int(kernel_pos/kernel_len)][kernel_pos%kernel_len] + pixel[1]*kernelx[int(kernel_pos/kernel_len)][kernel_pos%kernel_len] + pixel[2]*kernelx[int(kernel_pos/kernel_len)][kernel_pos%kernel_len]) / 3
                        gy += (pixel[0]*kernely[int(kernel_pos/kernel_len)][kernel_pos%kernel_len] + pixel[1]*kernely[int(kernel_pos/kernel_len)][kernel_pos%kernel_len] + pixel[2]*kernely[int(kernel_pos/kernel_len)][kernel_pos%kernel_len]) / 3
                    kernel_pos += 1
            gx /= c
            gy /= c
            if (math.fabs(gx) > bias or math.fabs(gy) > bias) and (i > 3 and j > 0 and i < image.size[0] - 5 and j < image.size[1] - 5):
                angulo = math.degrees(math.atan2(gy, gx))
                ro = int( (i*math.cos(angulo)) + (j*math.sin(angulo)))
                line_matrix[i,j] = (angulo, ro)
                
                if (angulo, ro) in votos:
                    votos[(angulo, ro)] += 1 
                else:
                    votos[(angulo, ro)] = 1

    return line_matrix, frequency, votos

def nuevo_visitados(size):
    visitados = dict()
    for i in range(size[0]):
        for j in range(size[1]):
            visitados[i,j] = False
    return visitados

def dfs(image, inicio, visitados, size, angle_bias = 10, ro_bias = 5, p = None):
    siguientes = list()
    siguientes.append(inicio)
    counter = 0

    line = list(image[inicio])

    while len(siguientes) > 0:
        actual = siguientes.pop(0)
        visitados[tuple(actual)] = True
        counter += 1
#        print image[actual]

        line[0] = (line[0] + image[actual][0])/2
        line[1] = (line[1] + image[actual][1])/2

        for h in range(int(actual[0])-1, int(actual[0])+2):
            for l in range(int(actual[1])-1, int(actual[1])+2):
                if h >= 0 and l >= 0 and h < size[0] and l < size[1]:
                    if (h, l) in image and not visitados[h, l]:
                        if math.fabs(image[h, l][0]-line[0]) < angle_bias and math.fabs(image[h, l][1]-line[1]) < ro_bias: # que la linea se parezca a un promedio 
                            if not (h, l) in siguientes:
                                siguientes.append((h, l))
                        else:
                            visitados[h, l] = True
    return line, counter

def evaluate_line(angulo, ro, x):
    if math.sin(angulo) != 0:
        return (ro - (x*math.cos(angulo)) ) / math.sin(angulo)
    else:
        return 1000000

def cluster_votes(votes, threshold = 10):
    lines = votes.keys()
    lines.sort()

    fl = open("angles.dat", 'w')
    for i in lines:
        fl.write(str(i[0])+'\n')
    fl.close()
#    print votes
#    return votos

def polygon_detection(image_name, output="output.png", size=(128, 128)):
    image = Image.open(image_name)
    original_image = image.copy()
    image.thumbnail(size, Image.ANTIALIAS)

    line_matrix, frequency, votes = calculate_line_values(image, bias=60.0, mask='sobel5')

    draw = ImageDraw.Draw(image)

    votos = dict()
#    angle_bias = 15
#    ro_bias = 30

    visitados = nuevo_visitados(image.size)
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if (x, y) in line_matrix and not visitados[x, y]:
                line, counter = dfs(line_matrix, (x, y), visitados, image.size, angle_bias = 30, ro_bias = 50, p = image.load())
                #print line
                aprox = line
                votos[tuple(aprox)] = counter
#                aprox[0] = float( (int(aprox[0])/angle_bias)*angle_bias )
#                aprox[1] = float( (int(aprox[1])/ro_bias)*ro_bias )
#                if aprox in votos:
#                    votos[tuple(aprox)] += counter
#                else:
#                    votos[tuple(aprox)] = counter

                #draw.line((0, evaluate_line(line[0], line[1], 0), image.size[0], evaluate_line(line[0], line[1], image.size[0])), (255, 0, 0))
    cluster_votes(votes)
#    print votos
#    temp = votos.values()
#    temp.sort()
#    print temp
#    for line in votos.keys():
#        if votos[line] > 100:
#        draw.line((0, evaluate_line(line[0], line[1], 0), image.size[0], evaluate_line(line[0], line[1], image.size[0])), (255, 0, 0))

#    image = original_image    
    image.save(output)

def main():
    before = time()
    polygon_detection(argv[1])
    print "Tiempo de corrida:", (time() - before)

main()
