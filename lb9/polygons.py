#!/usr/bin/python   

from time import time
from sys import argv
from  math import fabs, sqrt, pow, sin, cos, degrees, atan2
from random import randint
from PIL import Image, ImageOps, ImageDraw, ImageFont
from subprocess import call
from ImageFilter import MedianFilter

indice_mascara = {
    "sobelx":[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
    "sobely":[[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]],
    "sobel5x":[[1, 2, 0, -2, -1], [4, 8, 0, -8, -4], [6, 12, 0, -12, -6], [4, 8, 0, -8, -4], [1, 2, 0, -2, -1]],
    "sobel5y":[[-1, -4, -6, -4, -1], [-2, -8, -12, -8, -2], [0, 0, 0, 0, 0], [2, 8, 12, 8, 2], [1, 4, 6, 4, 1]],
    "prewittx":[[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
    "prewitty":[[1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -1.0, -1.0]]
    }

def mult_kernel(kernel, c):
    for x in range(len(kernel)):
        for y in range(len(kernel[0])):
            kernel[x][y] *= c
    return kernel

def border(image, bias = 10.0, mask = 'sobel', conts=1.0):
    output = image.copy()
    output = ImageOps.grayscale(output)
    
    matO = output.load()
    mat = image.load()

    kernelx = mult_kernel(indice_mascara[mask+'x'], conts)
    kernely = mult_kernel(indice_mascara[mask+'y'], conts)
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
                        pixel = mat[h, l]
                        c += 1
                        gx += (pixel[0]*kernelx[int(kernel_pos/kernel_len)][kernel_pos%kernel_len] + pixel[1]*kernelx[int(kernel_pos/kernel_len)][kernel_pos%kernel_len] + pixel[2]*kernelx[int(kernel_pos/kernel_len)][kernel_pos%kernel_len]) / 3
                        gy += (pixel[0]*kernely[int(kernel_pos/kernel_len)][kernel_pos%kernel_len] + pixel[1]*kernely[int(kernel_pos/kernel_len)][kernel_pos%kernel_len] + pixel[2]*kernely[int(kernel_pos/kernel_len)][kernel_pos%kernel_len]) / 3
                    kernel_pos += 1
            gx /= c
            gy /= c

            matO[i, j] = int(sqrt(pow(gx, 2)+pow(gy, 2)))
    return output

def normalize(image, maxv):
    mat = image.load()
    ratio = 255.0/maxv

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            mat[x, y] = int(mat[x, y]*ratio)
    return image

def difference(izq, der):
    output = izq.copy()
    matO = output.load()
    matI = izq.load()
    matD = der.load()
    maxv = 0
    for x in range(output.size[0]):
        for y in range(output.size[1]):
            cord = (x, y)
            matO[cord] = fabs(matI[cord]-matD[cord])
            if matO[cord] > maxv:
                maxv = matO[cord]
    return normalize(output, maxv)

def threshold(image, threshold = 128):
    mat = image.load()

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            value = mat[x, y]
            if value > threshold:
                mat[x, y] = 255
            else:
                mat[x, y] = 0
    return image

def nuevo_visitados(size):
    visitados = dict()
    for i in range(size[0]):
        for j in range(size[1]):
            visitados[i,j] = False
    return visitados

def dfs_promedio(mat, inicio, size):
    siguientes = list()
    siguientes.append(inicio)

    points = list()

    while len(siguientes) > 0:
        actual = siguientes.pop(0)
        mat[tuple(actual)] = 0
        points.append(actual)

        for h in range(int(actual[0])-1, int(actual[0])+2):
            for l in range(int(actual[1])-1, int(actual[1])+2):
                if h >= 0 and l >= 0 and h < size[0] and l < size[1]:
                    if mat[h, l] == 255: # que la linea se parezca a un promedio 
                        if not (h, l) in siguientes:
                            siguientes.append((h, l))
    return points

def promediar_esquinas(image):
    corners = list()
    mat = image.load()

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if mat[x, y] == 255:
                points = dfs_promedio(mat, (x, y), image.size)
                promedio = [0.0, 0.0]

                for p in points:
                    promedio[0] += p[0]
                    promedio[1] += p[1]
                    
                promedio = (int(promedio[0]/len(points)), int(promedio[1]/len(points)))
                corners.append(promedio)
    for cord in corners:
        mat[cord] = 255
    return corners

def random_color():
    return (randint(1,255), randint(1, 255), randint(1, 255))

def dfs_polygons(mat, inicio, size, corners):
    siguientes = [inicio]
    flag = True

    points = list()
    while len(siguientes) > 0:
        actual = siguientes.pop(0)
        mat[tuple(actual)] = 0
        
        if actual in corners:
            points.append(tuple(actual))
            if flag and inicio != actual:
                siguientes = list()
                flag = False

        for h in range(int(actual[0])-1, int(actual[0])+2):
            for l in range(int(actual[1])-1, int(actual[1])+2):
                if h >= 0 and l >= 0 and h < size[0] and l < size[1]:
                    if mat[h, l] == 255: # que la linea se parezca a un promedio 
                        if not (h, l) in siguientes:
                            siguientes.append((h, l))
    return points

def join_corners(image, corners):
    polygons = list()
    mat = image.copy().load()

    for x, y in corners:
        if mat[x, y] == 255:
            points = dfs_polygons(mat, (x, y), image.size, corners)
            polygons.append(points)

    return polygons

def verify_line(mat, cornerA, cornerB):
    if cornerA[0] < cornerB[0]:
        x0, y0 = cornerA
        x1, y1 = cornerB
    else:
        x0, y0 = cornerB
        x1, y1 = cornerA

    if x0 != x1:            
        deltax = x1 - x0
        deltay = y1 - y0
        error = 0.0

        delta_error = fabs(float(deltay) / deltax)
        y = y0
        for x in xrange(x0, x1, 1):
            if mat[x, y] != 255:
                return False

            error += delta_error
            while error >= 0.5:
                y += deltay/fabs(deltay)
                error -= 1.0
    else:
        x = x0
        for y in xrange(y0, y1):
            if mat[x, y] != 255:
                return False            

    return True

def verify_polygons(image, polygons):
    mat = image.load()
    
    verified_polygons = list()
    
    for i in range(len(polygons)):
        for j in range(1, len(polygons[i])):
            if not verify_line(mat, polygons[i][j-1], polygons[i][j]):
                break
        if j == len(polygons[i])-1 and verify_line(mat, polygons[i][0], polygons[i][-1]):
            verified_polygons.append(polygons[i])
    return verified_polygons

def polygon_detection(image_name, output="output.png", size=(128, 128)):
    image = Image.open(image_name)
    corner_image = image.copy()
    corner_image.thumbnail(size, Image.ANTIALIAS)

    border_image = border(corner_image, conts = 2.0)
    border_image = threshold(border_image, 10)

    corner_image = ImageOps.grayscale(corner_image)
    median_image = corner_image.copy().filter(MedianFilter(size=3))
    corner_image = difference(corner_image, median_image)
    del median_image
    corner_image = threshold(corner_image, 50)
    corners = promediar_esquinas(corner_image)
    polygons = join_corners(border_image, corners)
    
    razon = (float(image.size[0])/corner_image.size[0], float(image.size[1])/corner_image.size[1])

    order = image.copy()
    draw = ImageDraw.Draw(order)
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 18)
    for i in range(len(polygons)):
        for j in range(len(polygons[i])):
            x = polygons[i][j][0]*razon[0]
            y = polygons[i][j][1]*razon[1]
            draw.text((x, y), str(j+1), fill=(255, 0, 0), font=font)

    polygons =  verify_polygons(border_image, polygons)

    draw = ImageDraw.Draw(image)
    for i in range(len(polygons)):
        for j in range(1, len(polygons[i])):
            x0 = polygons[i][j-1][0]*razon[0]
            y0 = polygons[i][j-1][1]*razon[1]
            x1 = polygons[i][j][0]*razon[0]
            y1 = polygons[i][j][1]*razon[1]
            draw.line((x0, y0, x1, y1), fill=(255, 0, 0))
        x0 = polygons[i][0][0]*razon[0]
        y0 = polygons[i][0][1]*razon[1]
        x1 = polygons[i][-1][0]*razon[0]
        y1 = polygons[i][-1][1]*razon[1]
        draw.line((x0, y0, x1, y1), fill=(255, 0, 0) )

        prom = [0.0, 0.0]
        for j in range(len(polygons[i])):
            prom[0] += polygons[i][j][0]
            prom[1] += polygons[i][j][1]
        prom = (prom[0]*razon[0] / len(polygons[i]), prom[1]*razon[1] / len(polygons[i]))
        draw.ellipse((prom[0]-5, prom[1]-5, prom[0]+5, prom[1]+5), fill=(0, 255, 0))
        draw.text((prom[0]+10, prom[1]), 'Poligono'+str(i+1), fill=(0, 128, 128), font=font)
        print 'Poligono'+str(i+1), 'encontrado, tiene', str(len(polygons[i])),'lados.'

    border_image.save('border_'+output)
    corner_image.save('corner_'+output)
    order.save('order_'+output)
    image.save(output)

def main():
    before = time()
    polygon_detection(argv[1])
    print "Tiempo de corrida:", (time() - before)

main()
