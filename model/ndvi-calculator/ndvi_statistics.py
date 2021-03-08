import statistics

def get_statistics(array):
    """
        Вход: массив ndvi, в ячейках которые смотреть не надо стоит -100. Для остальных ячеев вычисляется
        минимальное, максимальное, среднее и медианное значение
        Возвращает минимальное, максимальное, среднее и медианное значение ndvi"""

    data = []
    for i in range(len(array)):
        for j in range(len(array[i])):
            if array[i][j] != -100:
                data.append(array[i][j])
    return min(data), max(data), statistics.mean(data), statistics.median(data)
