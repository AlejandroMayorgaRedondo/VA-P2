import numpy as np
import cv2 as cv


def processImage(route):
    img = cv.imread(route)
    grayimg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    return grayimg

#-------------------------------------------------------------------------------


def traceLimit(inImage, ratio, isExterLent):
    x = 0
    y = 10
    lines = []
    cont = 0
    while x < len(inImage[0]):
        while y < len(inImage)-3:

            if (inImage[y, x] == 255 and cont == 0):
                if (isExterLent):
                    aux = y
                    cont += 1
                    val = [x,y]
                    y += 20
                    continue
                else:
                    y += 20

                cont += 1

            if (inImage[y, x] == 255 and cont == 1):
                if (not isExterLent):
                    aux = y
                    cont += 1
                    val = [x,y]
                    y += 20
                    continue
                else:
                    y += 20

                cont += 1

            if (inImage[y, x] == 255 and cont == 2):
                val.append(y-aux)
                lines.append(val)
                val = 0
                cont = 0
                y = 20
                break

            y += 1

        y = 20
        x += ratio

    return lines



#-------------------------------------------------------------------------------



def printValues(values1, values2):
    val1 = []
    val2 = []

    for x in values1:
        val1.append(x[2])
    for y in values2:
        val2.append(y[2])

    print("Forma de las listas: [[valor x, valor y, distancia hasta cornea]]\n"
          "Valores obtenidos para la medición lente externa-cornea:\n")
    for h in values1:
        print(h)
    print("\nMedia para lente externa-cornea:",round(np.mean(val1),2))
    print("Mediana para lente externa-cornea:", np.median(val1))
    print("Desviación típica entre mediciones:", round(np.std(val1),2))
    print("\n\n#-------------------------------------------------------------")
    print("\n\nValores obtenidos para la medición lente interna-cornea:\n")
    for h in values2:
        print(h)
    print("\nMedia para lente interna-cornea:",round(np.mean(val2),2))
    print("Mediana para lente interna-cornea:", np.median(val2))
    print("Desviación típica entre mediciones:", round(np.std(val2),2))


#-------------------------------------------------------------------------------

def paintLines(colorImage, list, isExterLent):                   #Lista de la forma: [valor x, valor y, distancia de la linea]
    medianValues = []

    for h in list:
        medianValues.append(h[2])
    median = np.median(medianValues)

    for x in list:


        if (x[2]<median*0.9):
                if (isExterLent):
                    outImage[x[1]:x[1]+x[2],x[0]] = (255,0,0)
                else:
                    outImage[x[1]:x[1]+x[2],x[0]] = (200,0,0)

        elif (x[2]>median*1.1):
            if (isExterLent):
                outImage[x[1]:x[1]+x[2],x[0]] = (0,0,255)
            else:
                outImage[x[1]:x[1]+x[2],x[0]] = (0,0,200)

        else:
            if (isExterLent):
                outImage[x[1]:x[1]+x[2],x[0]] = (0,255,0)
            else:
                outImage[x[1]:x[1]+x[2],x[0]] = (0,200,0)

    return colorImage



#-------------------------------------------------------------------------------


route = r"/home/alex/Escritorio/VA-P2/Imagenes/im8.jpeg"
inImage = processImage(route)



#Parte 1: Limpieza de imagen

kernel = np.array([[1]*50]*50)


outImage = cv.GaussianBlur(inImage, (7,7), cv.BORDER_DEFAULT)
outImage = cv.medianBlur(outImage, 9)
outImage = cv.morphologyEx(outImage, cv.MORPH_CLOSE, kernel)
outImage = cv.Canny(outImage,60, 130, 3)




#Parte 2: Obtención de datos

lines1 = traceLimit(outImage, 10, True)
lines2 = traceLimit(outImage, 5, False)
printValues(lines1,lines2)



#Parte 3: Visualización gráfica

outImage =  cv.cvtColor(outImage, cv.COLOR_GRAY2BGR)
outImage = paintLines(outImage, lines1, True)
outImage = paintLines(outImage, lines2, False)




cv.imshow("Salida", outImage)
cv.waitKey(0)


#Cosas que faltan:

    #Encontrar los mejores parámetros para las funciones de procesado: Los de ahora
    #no están mal, pero en algunos casos borran la parte inferior de la córnea -> ¿Importante?
