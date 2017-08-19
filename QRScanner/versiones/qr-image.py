#!/usr/bin/python
from PIL import Image, ImageDraw
from sys import argv
from time import time
from math import ceil, fabs

def get_charstable(pattern):
    charstable = dict()
    length = len(pattern)

    for i in range(length-1):
            charstable[pattern[i]] = length -i -1
    return charstable

def boyer_moore(string, pattern):
    charstable = get_charstable(pattern)

    length_pattern = len(pattern)
    length_string = len(string)

    if length_pattern > length_string:
        return
        yield
        
    i = length_pattern - 1# for the string
    j = length_pattern - 1# for the pattern
    shift = 0
    counter = 0

    while i < length_string:# - length_pattern:
        if string[i] == pattern[j]:
            if shift == length_pattern-1:
                yield i
                counter += 1
                i += length_pattern
                j = length_pattern - 1
                shift = 0
            shift += 1
            i -= 1
            j -= 1

        else:
            if string[i] in charstable:
                i += charstable[string[i]]
            else:
                i += length_pattern
            j = length_pattern - 1
            shift = 0
    return
    yield

class QR:

    def binarize(self, image, threshold = 128):
        new = Image.new('1', image.size)

        nimat = new.load()
        imat = image.load()
        for x in range(image.size[0]):
            for y in range(image.size[1]):
                pixel = imat[x, y]
                if type(pixel) == tuple:
                    pixel = sum(pixel)/len(pixel)
                if pixel > threshold:
                    nimat[x, y] = 255
                else:
                    nimat[x, y] = 0
        return new

    def find_patterns(self, image, threshold = (0.5)*5, color_pat = 'BWBWB', pat = (1, 1, 3, 1, 1)): #(color, proporcion)):
        imat = image.load()
        bandera = False

        for x in range(image.size[0]):
            line = ''
            cpixel = list()
            ranges = [0]
            color_counter = 1
            color = imat[x, 0]

            for y in range(1, image.size[1]):
                pixel = imat[x, y]
                if pixel == color:
                    color_counter += 1
                else:
                    if color == 255: line += 'W'
                    else: line += 'B'
                    ranges.append(y)
                    cpixel.append(color_counter)
                    color = pixel
                    color_counter = 1

            if color == 255: line += 'W'
            else: line += 'B'
            ranges.append(y)
            cpixel.append(color_counter)

            for r in boyer_moore(line, color_pat):
                for vector in [[cpixel[j] for j in range(r, r+5)]] :
                    unidad = float(vector[-1])
                    for indice in range(1, len(vector)):

                        vector[indice] = vector[indice]/unidad
                        if fabs(pat[indice]-vector[indice]) > threshold[indice]:
                            break
                        if indice == len(vector)-1:
                            for ycord in range(ranges[r], ranges[r+5]):
                                yield x, ycord
                                bandera = True
                                
        # Revision vertical
        for y in range(image.size[1]):
            line = ''
            cpixel = list()
            ranges = [0]
            color_counter = 1
            color = imat[0, y]

            for x in range(1, image.size[0]):
                pixel = imat[x, y]
                if pixel == color:
                    color_counter += 1
                else:
                    if color == 255: line += 'W'
                    else: line += 'B'
                    ranges.append(x)
                    cpixel.append(color_counter)
                    color = pixel
                    color_counter = 1

            if color == 255: line += 'W'
            else: line += 'B'
            ranges.append(x)
            cpixel.append(color_counter)

            for r in boyer_moore(line, color_pat):
                for vector in [[cpixel[j] for j in range(r, r+5)]]:
                    unidad = float(vector[-1])

                    for indice in range(1, len(vector)):
                        vector[indice] = vector[indice]/unidad

                        if fabs(pat[indice]-vector[indice]) > threshold[indice]:
                            break
                        if indice == len(vector)-1:
                            for xcord in range(ranges[r], ranges[r+5]):
                                yield xcord, y
                                bandera = True
        
        # Revision de diagonal
        
        for inicio in [(x, 0) for x in range(image.size[0]-len(pat))]+[(0, y) for y in range(1, image.size[1]-len(pat))]:
            x, y = inicio
            line = ''
            cpixel = list()
            ranges = [(x, y)]#No se que hacer con esto o.0
            color_counter = 1
            color = imat[x, y]
            x, y = (x+1, y+1)

            while x < image.size[0] and y < image.size[1]:
                pixel = imat[x, y]
                if pixel == color:
                    color_counter += 1
                else:
                    if color == 255: line += 'W'
                    else: line += 'B'
                    ranges.append((x, y))
                    cpixel.append(color_counter)
                    color = pixel
                    color_counter = 1
                x, y = (x+1, y+1)

            for r in boyer_moore(line, color_pat):
                for vector in [[cpixel[j] for j in range(r, r+5)]]:
                    unidad = float(vector[-1])
                    
#                    if inicio != (13, 0):
#                        break
#                    print line
#                    print vector

                    for indice in range(1, len(vector)):
                        vector[indice] = vector[indice]/unidad
                        
                        if fabs(pat[indice]-vector[indice]) > threshold[indice]:
                            break

                        if indice == len(vector)-1:
                            x, y = ranges[r]
                            for xcord, ycord in [(x+i, y+i)for i in range(ranges[r+len(pat)][0]-ranges[r][0])]:
                                yield xcord, ycord
                                bandera = True

        if bandera:
            return
        else:
            return
            yield

    def scan(self, image_path, output='output.png', size=(128, 128)):
        image = Image.open(image_path)
        image.thumbnail(size, Image.ANTIALIAS)
        image = self.binarize(image)
        image.save('binary_'+output)
        size = image.size
        
        values = [(x, y) for x, y in self.find_patterns(image, threshold = (0.5, 0.5, 1.5, 0.5, 0.5) )]
        
        frequency = dict()
        for i in values:
            if i in frequency:
                frequency[i] += 1
            else:
                frequency[i] = 1
                    
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
#        for i in values:
#            if True:
        for i in frequency.keys():
            if frequency[i] > 2:
                x = int(image.size[0]*(float(i[0])/size[0]))
                y = int(image.size[1]*(float(i[1])/size[1]))
                r = 1
                draw.ellipse((x-r, y-r, x+r, y+r), fill=(0, 255, 0))

#        draw.line((x, 0, x, image.size[1]), fill=(255, 0, 0)) # Linea en x
#        draw.line((0, y, image.size[0], y), fill=(255, 0, 0)) # Linea en y
#        y = 39
#        y = 49
#        x, y = (13, 1)
#        x = int(image.size[0]*(float(x)/size[0]))
#        y = int(image.size[1]*(float(y)/size[1]))
#        draw.line((x, y, x+500, y+500), fill=(255, 0, 0)) # Linea en x
#        draw.line((0, y, image.size[0], y), fill=(255, 0, 0)) # Linea en y

        image.save(output)
        

def main():
    before = time()
    qr = QR()
    qr.scan(argv[1])
    print "Tiempo de corrida:", (time() - before)

main()
