import cv2
import matplotlib.pyplot as plt
from tiatoolbox.tools import stainnorm


def cargar(ruta):
    return cv2.cvtColor(cv2.imread(ruta), cv2.COLOR_BGR2RGB)


target_image = cargar("/storage/scratch01/groups/ce/BLCA_Spatial/candidata_3.png")  
imagen = cargar("/storage/scratch01/groups/ce/BLCA_Spatial/AL-7332_B20-04366_13_01_2116_1_14_crop.ome.tif")

# 2. Ajustar a la referencia y transformar

norm = stainnorm.get_normalizer("Reinhard")
norm.fit(target_image)
imagen_norm = norm.transform(imagen)


# 3. Guardar
cv2.imwrite("/storage/scratch01/groups/ce/BLCA_Spatial/AL-7332_B20-04366_13_01_2116_1_14_crop_norm.tif", cv2.cvtColor(imagen_norm, cv2.COLOR_RGB2BGR))