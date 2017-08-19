#!/usr/bin/python
from PIL import Image
import sys, time, random, math

def escala_grises(image):
    pic = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):

            (R, G, B) = pic[i,j]
            # Grayscale
            intensity = int((R+G+B)/3)
            R = G = B = intensity
            pic[i,j] = (R, G, B)
    return pic

def filtro_umbral(image, umbral=128):
    pic = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):

            colors = list(pic[i,j])
            for h in range(len(colors)):
                if colors[h] < umbral:
                    colors[h] = 0
                else:
                    colors[h] = 255
            pic[i,j] = tuple(colors)
    return pic

def filtro_media(image):
    pic = image.load()
    pic_copy = (image.copy()).load()

    for i in range(image.size[0]):
        for j in range(image.size[1]):

            temp = []
            for h in range(i-1, i+2):
                for l in range(j-1, j+2):
                    if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                        temp.append(pic_copy[i, j][0])

            temp.sort()
            R = G = B = int(temp[int(len(temp)/2)])
            pic[i,j] = (R, G, B)
    return pic

def diferencia_media_grises(image):
    image2 = image.copy()
    escala_grises(image)
    filtro_media(image2)
    pic = image.load()
    pic2 = image2.load()

    # grises - media
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            (R, G, B) = pic[i,j]
            (R2, G2, B2) = pic2[i,j]
            R = R2 - R 
            G = G2 - G
            B = B2 - B
            pic[i,j] = (R, G, B)

def generar_sal_y_pimienta(image):
    pic = image.load()
    pic_copy = (image.copy()).load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            (R, G, B) = pic[i,j]
            pic[i,j] = (R, G, B)
    
efecto = {
    "grayscale":escala_grises,
    "umbral":filtro_umbral,
    "media":filtro_media,
    "diferencia":diferencia_media_grises,
    "generarsl":generar_sal_y_pimienta
    }

def aplicar_efecto(nImagen, nOutput, aplicar_efectos=[]):
    image = Image.open(nImagen)
    const = 16.0
    for i in aplicar_efectos:
        pic = efecto[i](image)
    image.save(nOutput)

indice_mascara = {
    "gaussian":[[1.0, 2.0, 1.0], [2.0, 4.0, 2.0], [1.0, 2.0, 1.0]],
    "sobelx":[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
    "sobely":[[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]]
    }

def matrix_copy(matrix):
    new = list()
    for i in matrix:
        temp = list()
        for j in i:
            temp.append(j)
        new.append(temp)
    return new

def convolucion(kernel, image):
    pic = image.load()
    pic_copy = (image.copy()).load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):

            sumatory = [0.0, 0.0, 0.0] # RGB
            kernel_len = len(kernel[0])
            kernel_pos = 0
            
            for h in range(i-1, i+2):
                for l in range(j-1, j+2):
                    if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                        pixel = pic_copy[h, l]
                        sumatory[0] += pixel[0]*kernel[int(kernel_pos/3)][kernel_pos%3]
                        sumatory[1] += pixel[1]*kernel[int(kernel_pos/3)][kernel_pos%3]
                        sumatory[2] += pixel[2]*kernel[int(kernel_pos/3)][kernel_pos%3]
                        kernel_pos += 1

            pic[i, j] = (int(sumatory[0]), int(sumatory[1]), int(sumatory[2]))
            
def multiplicar_mascara(kernel, const):
    for i in range(len(kernel)):
        for j in range(len(kernel[0])):
            kernel[i][j] *= const
    return kernel

def aplicar_mascara(nImagen, mascara=[], const=[], nOutput="output.jpg", image=None, cmd=""):
    if image == None:
        image = Image.open(nImagen)
    for i in range(len(mascara)):
        kernel = matrix_copy(indice_mascara[mascara[i]])
        kernel = multiplicar_mascara(kernel, const[i])
        convolucion(kernel, image)

    if cmd == "i":
        return image
    else:
        image.save(nOutput)

def gradient(gradientx, gradienty):
    gx = gradientx.load()
    gy = gradienty.load()

    max_values = [0,0,0]

    for i in range(gradientx.size[0]):
        for j in range(gradientx.size[1]):
            (Rx, Gx, Bx) = gx[i,j]
            (Ry, Gy, By) = gy[i,j]

            Rx = int(math.sqrt(Rx+Ry))
            if Rx > max_values[0]:
                max_values[0] = Rx

            Gx = int(math.sqrt(Gx+Gy))
            if Gx > max_values[1]:
                max_values[1] = Gx

            Bx = int(math.sqrt(Bx+By))
            if Bx > max_values[2]:
                max_values[2] = Bx

            gx[i,j] = (Rx, Gx, Bx)
    return gradientx, max_values

def normalizar(image, max_values):
    pic = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            (R, G, B) = pic[i,j]
            R = G = B = int( ( ((float(R)/max_values[0])*255 ) + ((float(G)/max_values[1])*255) + ((float(B)/max_values[2])*255) )/3 )
            pic[i,j] = (R, G, B)

def border_detection(picture, output="output.png"):
    imagex = aplicar_mascara(picture, ["sobelx"], [1.0/1.0], cmd="i")
    imagey  = aplicar_mascara(picture, ["sobely"], [1.0/1.0], cmd="i")
    border, max_values = gradient(imagex, imagey)
    del imagey

    pseudo_promedio = normalizar(border, max_values)
    filtro_umbral(border, umbral=int(sys.argv[2]))
    
    border.save(output)    

def main():
    border_detection(sys.argv[1])
    #aplicar_efecto(sys.argv[1], "output.jpg", ["generarsl", "media"])
    
main()
