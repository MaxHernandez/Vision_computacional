#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import sys, time, random, math

def dotproduct(v1, v2):
  return float(sum((a*b) for a, b in zip(v1, v2)))

def get_angle(p1, p2, p3):
    v1 = (p2[0]-p1[0], p2[1]-p1[1])
    v2 = (p2[0]-p3[0], p2[1]-p3[1])

    producto_punto = dotproduct(v1,v2)
    producto_denominador = math.sqrt(dotproduct(v1,v1))*math.sqrt(dotproduct(v2,v2))
    angulo = 0.0
    if producto_denominador != 0:
        angulo = producto_punto / producto_denominador
        if angulo >= 1.0:
            return 0.0
        elif angulo <= -1.0:
            return math.pi
        else:
            angulo = math.degrees(math.acos(angulo))
    return angulo

def jarvis(points, image):
    point_on_hull = min(points)
    wraping_points = list()
    i = 0

    while False is not True:
        wraping_points.append(point_on_hull)
        end_point = [points[0], 0.0]
            
        for j in range(0, len(points)):
            if len(wraping_points) > 1:
                angle = get_angle(wraping_points[i-1], wraping_points[i], points[j])
            else:
                temp = (wraping_points[0][0], wraping_points[0][1]-1) 
                angle = get_angle(temp, wraping_points[i], points[j])

            if (end_point[0] == point_on_hull) or angle > end_point[1]:
                end_point[0] = points[j]
                end_point[1] = angle
        i = i+1
        point_on_hull = end_point[0]
        if end_point[0] == wraping_points[0]:
            break

    draw = ImageDraw.Draw(image)
    for i in range(1, len(wraping_points)):
        draw.line((wraping_points[i-1][0], wraping_points[i-1][1], wraping_points[i][0], wraping_points[i][1]) , fill=(255,0,0))
    draw.line((wraping_points[len(wraping_points)-1][0], wraping_points[len(wraping_points)-1][1], wraping_points[0][0], wraping_points[0][1]) , fill=(255,0,0))

def dfs(image, inicio, visitados, output="output.png"):
    pic = image.load()
    siguientes = list()
    siguientes.append(inicio)
    points = list()
    reference_color = pic[tuple(inicio)]
    if reference_color != (255,255,255):
        return

    while len(siguientes) > 0:
        actual = siguientes.pop(0)
        points.append(actual)
        visitados[tuple(actual)] = True

        for h in range(actual[0]-1, actual[0]+2):
            for l in range(actual[1]-1, actual[1]+2):
                if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                    if not visitados[h, l]:
                        if reference_color == pic[h,l]:
                            if not [h, l] in siguientes:
                                siguientes.append([h, l])
    jarvis(points, image)

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
