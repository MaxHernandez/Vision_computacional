#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import sys, time, random, math, filtros

"""
Referencias:
http://en.wikipedia.org/wiki/Gift_wrapping_algorithm
"""

def on_the_left(p1, p2, pt_compare):
    if (float(p2[0])-p1[0]) == 0.0 or (float(p2[1])-p1[1]) == 0.0:
        return False

    m = (float(p2[1])-p1[1]) / (float(p2[0])-p1[0])
    b = p1[1]-(m*p1[0])

    if pt_compare[0] <  int(((pt_compare[1])-b)/m):
        return True
    else:
        return False

def gift_wraping(image, points):
    draw = ImageDraw.Draw(image)
    P = list()

    point_on_hull = min(points)
    while False is not True:
        P.append(point_on_hull)
        end_point = points[0]
        i = 0
        for j in range(1, len(points)):
#            if (end_point == point_on_hull) or on_the_left(P[i], end_point, points[j]): #cosa rara
                end_point = points[j]
        i += 1
        point_on_hull = end_point
        
        if end_point == P[0]:
            break
    print P
    for i in range(1, len(P)):
        draw.line((P[i-1][0], P[i-1][1], P[i][0], P[i][1]), fill=(255,0,0))
    draw.line((P[len(P)-1][0], P[len(P)-1][1], P[0][0], P[0][1]), fill=(255,0,0))

def dfs(image, inicio, visitados, output="output.png"):
    pic = image.load()
    siguientes = list()
    points = list()
    siguientes.append(inicio)
    reference_color = pic[tuple(inicio)]
    if reference_color != (255, 255, 255):
        return

    while len(siguientes) > 0:
        actual = siguientes.pop(0)        
        visitados[tuple(actual)] = True
        points.append(tuple(actual))

        for h in range(actual[0]-1, actual[0]+2):
            for l in range(actual[1]-1, actual[1]+2):
                if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                    if not visitados[h, l]:
                        # Sepraro los if por que este de abajo podria 
                        # tornase mas complicado
                        if reference_color == pic[h,l]:
                            if not [h, l] in siguientes:
                                siguientes.append([h, l])
    gift_wraping(image, points)

def nuevo_visitados(size):
    visitados = dict()
    for i in range(size[0]):
        for j in range(size[1]):
            visitados[i,j] = False
    return visitados

def main(output="output.png"):
    image = Image.open(sys.argv[1])

    visitados = nuevo_visitados(image.size)

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if not visitados[i, j]:
                dfs(image, [i, j], visitados)
    image.save(output)

main()
