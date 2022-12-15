from PIL import Image
import numpy as np
import math
import cv2 as cv
import matplotlib.pyplot as plt


def processImage(route):
    img = Image.open(route)
    img_gray = img.convert('L')
    arr = np.array(img_gray)/255

    return arr


#-------------------------------------------------------------------------------

def dilate (inImage, SE, center):
    outImage = np.copy(inImage)

    if (center == []):
        center = [math.floor(len(SE)/2), math.floor(len(SE[0])/2)]

    for x in range(0, len(inImage) - len(SE/2)):
        for y in range(0, len(inImage[0]) - len(SE[0]/2)):
            if (inImage[x+center[0]][y+center[1]] == 1.):

                for h in range(0, len(SE)):
                    for l in range(0, len(SE[0])):
                        if (SE[h][l] == 1.):
                            outImage [x+h][y+l] = 1.

    return outImage

#--------------------------------------------------------------------------------

def erode (inImage, SE, center):
    outImage = np.zeros((len(inImage),len(inImage[0])))
    out = False
    if (center == []):
        center = [math.floor(len(SE)/2), math.floor(len(SE[0])/2)]

    for x in range(0, len(inImage) - len(SE/2)):
        for y in range(0, len(inImage[0]) - len(SE[0]/2)):

            out = False
            rangeImage = inImage[x:x+len(SE),y:y+len(SE[0])]
            outImage[center[0]+x][center[1]+y] = 1.

            for j in range(0,len(rangeImage)):
                if (out):
                    break
                for l in range(0,len(rangeImage[0])):

                    if (int(SE[j][l]) != int(rangeImage[j][l])):
                        outImage[center[0]+x][center[1]+y] = 0.
                        out = True
                        break

    return outImage



#---------------------------------------------------------------------------------


def opening(inImage, SE, center):
    tmpImage = erode(inImage,SE,center)
    outImage = dilate(tmpImage,SE,center)
    return outImage


#--------------------------------------------------------------------------------



def closing(inImage, SE, center):
    tmpImage = dilate(inImage,SE,center)
    outImage = erode(tmpImage,SE,center)
    return outImage


#---------------------------------------------------------------------------------


def medianfilter(inImage, filterSize, finish):
        outImage = np.copy(inImage)
        centerKernel = math.floor(filterSize/2+1)

        for h in range(centerKernel,len(inImage)-centerKernel):
            if (h==finish and finish!=0):
                break
            for l in range(centerKernel,len(inImage[0])-centerKernel):

                image_matr = inImage[h:h+filterSize, l:l+filterSize]
                flatten_matr = image_matr.flatten()
                outImage[h + centerKernel, l + centerKernel] = np.median(flatten_matr)

        return outImage


#-------------------------------------------------------------------------------

def umbralize(inImage, umbr):
    outImage = np.copy(inImage)

    for x in range(0, len(inImage)):
        for y in range(0, len(inImage[0])):

            if ((inImage[x][y])>umbr):
                outImage[x][y] = 1.

            else:
                outImage[x][y] = 0.

    return outImage

#-------------------------------------------------------------------------------

def traceLimit(inImage, limitTracing, ratio):
    cont = limitTracing
    x = 0
    y = 30
    check = [1.,1.,1.]
    lines = []

    while x < len(inImage[0]):
        while y < len(inImage)-3:

            if (np.all(inImage[y:y+3, x] == check) and cont == 0):
                cont += 1
                y += 50
                continue

            if (np.all(np.array(inImage[y:y+3, x])) and cont == 1):
                aux = y
                cont += 1
                val = [x,y]
                y += 50
                continue

            elif (np.any(np.array(inImage[y:y+3, x])) and cont == 2):
                val.append(y-aux)
                lines.append(val)
                val = 0
                cont = limitTracing
                y = 30
                break

            if (y == len(inImage)-4):
                cont = 0
                y = 30
                break

            y += 1
        x += ratio

    return lines


#-------------------------------------------------------------------------------

def paintLines(colorImage, list):                   #Lista de la forma: [valor x, valor y, distancia de la linea]
    medianValues = []

    for h in list:
        medianValues.append(h[2])
    median = np.median(medianValues)

    for x in list:

        if (x[2]<median*0.9):
            for y in range(0,x[2]):
                colorImage.putpixel((x[0],x[1]+y),(0,0,255,0))

        elif (x[2]>median*1.1):
            for y in range(0,x[2]):
                colorImage.putpixel((x[0],x[1]+y),(255,0,0,0))

        else:
            for y in range(0,x[2]):
                colorImage.putpixel((x[0],x[1]+y),(0,255,0,0))

    return colorImage


#-------------------------------------------------------------------------------



def printValues(values1, values2):
    val1 = []
    val2 = []
    #print("Valores obtenidos para la medición lente extern-cornea", np.sort(values1))
    for x in values1:
        val1.append(x[2])
    for y in values2:
        val2.append(y[2])
    #print(val2)
    print("Media para lente externa-cornea:",round(np.mean(val1),2))
    print("Mediana para lente externa-cornea:", np.median(val1))
    print("Desviación típica entre mediciones:", round(np.std(val1),2))
    #print("Valores obtenidos para la medición lente interna-cornea", np.sort(values2))
    print("Media para lente interna-cornea:",round(np.mean(val2),2))
    print("Mediana para lente interna-cornea:", np.median(val2))
    print("Desviación típica entre mediciones:", round(np.std(val2),2))

#------------------------------------------------------------------------------


def supresion(tmpImage2):

    suprImage = processImage()
    mag = np.copy(tmpImage2[1])
    dir = np.copy(tmpImage2[0])
    [ant, pos] = [0., 0.]

    for x in range(0, len(tmpImage2[0])-5):
        for y in range(0, len(tmpImage2[0][0])-5):

            if (0.39 < dir[x][y] < 1.17):
                [ant, pos] = [ mag[x-1][y-1], mag[x+1][y+1]]

            elif (-0.39 < dir[x][y] < 0.39):
                [ant, pos] = [mag[x][y+1], mag[x][y-1]]

            elif (-1.17 < dir[x][y] < -0.39):
                [ant, pos] = [mag[x+1][y-1], mag[x-1][y+1]]

            else:
                [ant, pos] = [mag[x+1][y], mag[x-1][y]]

            if ((mag[x][y]>=pos) and (mag[x][y]>=ant)):
                suprImage[x][y] = mag[x][y]
            else:
                suprImage[x][y] = 0.

    return suprImage

#------------------------------------------------------------------------------


def checkHisteresis(suprImage, tl, x, y, direccion):
    puntos = []
    if (-0.39 < direccion[x][y] < 0.39):

        if(suprImage[x+1][y] > tl):
            puntos += [(x+1,y)]
        if(suprImage[x-1][y] > tl):
            puntos += [(x-1,y)]

    if (0.39 < direccion[x][y] < 1.17):

        if(suprImage[x+1][y-1] > tl):
            puntos += [(x+1,y-1)]
        if(suprImage[x-1][y+1] > tl):
            puntos += [(x-1,y+1)]

    elif (-1.17 < direccion[x][y] < -0.39):
        if(suprImage[x-1][y-1] > tl):
            puntos += [(x-1,y-1)]
        if(suprImage[x+1][y+1] > tl):
            puntos += [(x+1,y+1)]

    else:

        if(suprImage[x][y-1] > tl):
            puntos += [(x,y-1)]
        elif(suprImage[x,y+1] > tl):
            puntos += [(x,y+1)]

    return puntos

#------------------------------------------------------------------------------

def histeresis(suprImage,orient,tl,th):
    outImage = np.zeros((len(suprImage), len(suprImage[0])))
    puntos = []

    for x in range(1, len(suprImage)-1):
        for y in range(1, len(suprImage[0])-1):
            if (suprImage[x][y]>th):
                outImage[x][y] = 1.
                puntos = checkHisteresis(suprImage, tl, x, y, orient)
                for l in puntos:
                    outImage[l[0]][l[1]] = 1.
                puntos = []

    return outImage

#------------------------------------------------------------------------------


def edgeCanny(inImage, sigma, tlow, thigh):
    outImage = processImage()
    tmpImage = np.copy(outImage)
    tmpImage2 = np.copy(outImage)
    tmpImage3 = np.copy(outImage)

    tmpImage = gradientImage(gaussianFilter(inImage, sigma), "Sobel")
    tmpImage2 = magAndOrient(tmpImage[0], tmpImage[1])
    tmpImage3 = supresion(tmpImage2)
    outImage = histeresis(tmpImage3, tmpImage2[0], tlow, thigh)

    return outImage
#-------------------------------------------------------------------------------

img = "im12.jpeg"
route = r"/home/alex/Escritorio/VA-P2/Imagenes/"
name = route + img

inImage = processImage(name)
#plt.hist(inImage)
#plt.show()



#kernel = [[4/10,2/10,4/10]]
#outImage = filterImage(inImage, kernel)
#outImage = adjustIntensity(inImage, [], [0.,0.8])
outImage = umbralize(inImage, 0.45)
#outImage = adjustIntensity(outImage, [], [0.,1.])
outImage = medianfilter(outImage, 5, 0)
outImage = medianfilter(outImage, 7, 200)
#outImage = medianfilter(outImage, 5, 500)
#plt.hist(outImage)
#plt.show()


#SE1 = np.array([[1,1,1,1]])

SE3 = np.array([[1,1,1,1]])


#outImage = erode(np.copy(outImage), SE1, [])





#tmpImage = Image.fromarray((outImage*255).astype(np.uint8)).convert("RGB")
#tmpImage.show()

outImage = opening(np.copy(outImage), SE3, [])


lines1 = traceLimit(outImage, 0, 50)
lines2 = traceLimit(outImage, 1, 70)
outImage = Image.fromarray((outImage*255).astype(np.uint8)).convert("RGB")
outImage = paintLines(outImage, lines1)
outImage = paintLines(outImage, lines2)



printValues(lines1,lines2)



outImage.show()
outImage.save("Salida.png")
