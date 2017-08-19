#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import sys, time, random, math, filtros

def dfs(image, inicio, visitados, color, output="output.png"):
    pic = image.load()
    siguientes = list()
    siguientes.append(inicio)
    reference_color = pic[tuple(inicio)]
    number_of_pixels = 0
    sum_positions = [0,0]

    while len(siguientes) > 0:
        actual = siguientes.pop(0)
        number_of_pixels += 1
        sum_positions[0] += actual[0]
        sum_positions[1] += actual[1]

        if pic[tuple(actual)] != ( 255, 255, 255):
            pic[tuple(actual)] = tuple(color)
        
        visitados[tuple(actual)] = True

        for h in range(actual[0]-1, actual[0]+2):
            for l in range(actual[1]-1, actual[1]+2):
                if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                    if not visitados[h, l]:
                        # Sepraro los if por que este de abajo podria 
                        # tornase mas complicado
                        if reference_color == pic[h,l]:
                            if not [h, l] in siguientes:
                                siguientes.append([h, l])
    return number_of_pixels, sum_positions

def nuevo_visitados(size):
    visitados = dict()
    for i in range(size[0]):
        for j in range(size[1]):
            visitados[i,j] = False
    return visitados


def main(output="output.png"):
    image = Image.open(sys.argv[1])

    filtros.filtro_promedio(image)
    filtros.filtro_umbral(image, umbral=40)
    image.save(output)
    return

    color = (0,0,255)
    centroids = list()
    background = [0, (0,0)]
    visitados = nuevo_visitados(image.size)

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if not visitados[i, j]:
                color = [random.randint(50, 200), random.randint(0, 255), random.randint(0, 255)]
                n_pixels, centroid = dfs(image, [i, j], visitados, color)
                if n_pixels > 500:
                    centroid[0] /= n_pixels
                    centroid[1] /= n_pixels
                    centroids.append(centroid)
                if n_pixels > background[0]:
                    background[0] = n_pixels
                    background[1] = (i, j)

    visitados = nuevo_visitados(image.size)
    dfs(image, background[1], visitados, [128, 128, 128])


    font = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Arial.ttf", 18)
    draw = ImageDraw.Draw(image)
    abcedario = "ABCDEFGHIJKLMNOPQRSTUWXYZ"
    counter = 0
    for i in centroids:
        r = 5
        draw.ellipse((i[0]-r, i[1]-r, i[0]+r, i[1]+r), fill=(255, 0, 0))
        draw.text((i[0]+r+2, i[1]), abcedario[counter], font=font)
        counter += 1

    image.save(output)

main()
