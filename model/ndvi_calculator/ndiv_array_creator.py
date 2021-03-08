import numpy as np

def ndvi_from_3_array(red_array, ni_array, mask_array):
    """
        Вход: 3 массива одинакового размера - красный канал, ближний инфракрасный и маска, точки которой,
        указывают, что тут надо считать ndvi.
        Возвращает массив со значениями ndvi"""
    C = []
    for i in range(len(red_array)):
        pC = []
        for j in range(len(red_array[i])):
            if mask_array[i][j] > 0:
                pC.append((ni_array[i][j] - red_array[i][j]) / (ni_array[i][j] + red_array[i][j]))
            else:
                pC.append(-100)
        C.append(pC)

    ndvi = np.array([np.array(xi) for xi in C])

    return ndvi
