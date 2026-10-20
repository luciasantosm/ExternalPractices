import pandas as pd
import tifffile as tiff
import os

# SpaceRanger_path = "" #Create a SpaceRanger folder with all the jobs runned, the name of the job must contain the name of its original image.


def pair_parquet_image(SpaceRanger_path, images_path):
    """
    Función que empareje cada .parquet con su imagen correspondiente. Lo que hace es detectar el nombre de la imagen en el nombre del folder de SpaceRanger. 
    Cuando comprueba que son el mismo, extrae el path del .parquet y el path de la imagen y los devuelve en un diccionario.
    """
    pair_parquet_image_dic = {} #Diccionario que va a contener los pares de .parquet y .tiff en función de la muestra
    for image_name in os.listdir(images_path):
        for folder in os.listdir(SpaceRanger_path): 
            #Mira los nombres de cada uno de los resultados de SpaceRanger y comprueba si contiene el nombre de la imagen original
            if image_name in folder:
                parquet_path = os.path.join(SpaceRanger_path, folder, "outs/binned_outputs/square_002um/spatial/tissue_positions.parquet")
                image_path = os.path.join(images_path, image_name)
                pair_parquet_image_dic[image_name] = (parquet_path, image_path) 
    return pair_parquet_image_dic

def crop_tissue_tiff(parquet_path, image_path, output_path):
    """
    La función recorta la imagen original en función de las coordenadas exactas de los spots que están dentro del tejido.
    Para ello, primero lee el .parquet que contiene las coordenadas y filtra aquellos que están dentro del tejido. 
    Después, extrae las coordenadas mínimas y máximas de los spots dentro del tejido y recorta la imagen original en función de esas coordenadas.

    Inputs:
    -----------
    parquet_path: str
        Path to the .parquet file containing the spot coordinates.
    image_path: str
        Path to the original tissue image (TIFF format).
    output_path: str                
        Path where the cropped image will be saved (TIFF format).

    Outputs:
    -----------
    Saves the cropped image to the specified output path. (TIFF format)    
    """

    # Read the parquet file from SpaceRanger binned outputs
    df = pd.read_parquet(parquet_path)
    tissue_df = df[df['in_tissue']==1] #filter tissue coordinates

    #Extract x and y coordinates
    y = tissue_df["pxl_row_in_fullres"].values   
    x = tissue_df["pxl_col_in_fullres"].values

    image = tiff.imread(image_path)

    # Boundaries coordinates of the tissue 
    y0, y1 = int(y.min()), int(y.max()) 
    x0, x1 = int(x.min()), int(x.max())


    crop_image = image[y0:y1, x0:x1] #extract the tissue area from the original image

    tiff.imwrite(output_path, crop_image)

def main(SpaceRanger_path, images_path, output_path):
    """
    Main function to pair .parquet files with their corresponding tissue images and crop the images based on the coordinates from the .parquet files.

    Inputs: 
    -----------
    SpaceRanger_path: str
        Path to the SpaceRanger output directory containing the binned outputs.
    images_path: str
        Path to the directory containing the original tissue images (TIFF format).
    output_path: str
        Path where the cropped images will be saved (TIFF format).

    """

    paired_dic = pair_parquet_image(SpaceRanger_path, images_path) #Apply the function to pair the .parquet and .tiff files
    for image_name, (parquet_path, image_path) in paired_dic.items():
        # Crop the tissue image based on the coordinates from the parquet file which path is extracted from paired dictionary
        output_image_path = os.path.join(output_path, f"{image_name}_crop")
        crop_tissue_tiff(parquet_path, image_path, output_image_path)



parquet_path = "/home/luciasm/CNIO/TMA_1_2/tissue_positions_TMA_1_2.parquet"
image_path = "/home/luciasm/CNIO/TMA_1_2/AL-7332_99-6323-3_1_BOO-2657-12_2.ome.tif"
output_image_path = "/home/luciasm/CNIO/TMA_1_2/AL-7332_99-6323-3_1_BOO-2657-12_2_crop.ome.tif"  

crop_tissue_tiff(parquet_path, image_path, output_image_path)
