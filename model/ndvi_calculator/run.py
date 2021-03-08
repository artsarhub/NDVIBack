import ndvi_main


if __name__ == "__main__":
    # Координаты около Ростова
    polygon_wkt = "POLYGON((39.2376 47.3518,39.2514 47.2470,39.2156 47.2302,39.2349 47.04439,39.3214 47.0442," \
                  "39.3145 46.9483,39.4831 46.9851,39.5356 47.0640,39.74921 47.0819,39.7705 47.0078,40.0286 46.9727," \
                  "39.9461 47.3648,39.2376 47.3518))"

    # Весенний Ростов
    result_file, min, max, mean, median = ndvi_main.ndvi("./HDF/MOD09A1.A2020145.h20v04.006.2020154052223.hdf",
                                                         polygon_wkt)
    print(result_file, min, max, mean, median)


    # Осенний Ростов
    result_file, min, max, mean, median = ndvi_main.ndvi("./HDF/MOD09A1.A2020249.h20v04.006.2020262020549.hdf",
                                                         polygon_wkt)
    print(result_file, min, max, mean, median)


