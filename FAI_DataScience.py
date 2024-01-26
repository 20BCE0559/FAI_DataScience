import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box
from rasterio.mask import mask
from rasterio.enums import Resampling

def read_geotiff(file_path, target_shape):
    with rasterio.open(file_path) as src:
        data = src.read(1, out_shape=target_shape, resampling=Resampling.bilinear)
        transform = src.transform
    return data, transform

def create_annotation_map(dtm, dsm, orthomosaic):
    height = dsm - dtm
    approachable_threshold = 5  # Adjust as needed
    approachable_area = np.where(height > approachable_threshold, 1, 0)
    unapproachable_area = np.where(height <= approachable_threshold, 1, 0)

    aoi_threshold = 1
    aoi = np.where(height > aoi_threshold, 1, 0)

    approachable_area_within_aoi = approachable_area * aoi
    unapproachable_area_within_aoi = unapproachable_area * aoi

    total_plant_area = np.sum(approachable_area) + np.sum(unapproachable_area)

    bounds = box(*rasterio.transform.array_bounds(height.shape[0], height.shape[1], transform))
    gdf = gpd.GeoDataFrame({'geometry': [bounds]})
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))

    ax1.imshow(orthomosaic, cmap='gray', extent=gdf.geometry.total_bounds, alpha=0.5)
    ax1.imshow(aoi, cmap='Greens', alpha=0.2, extent=gdf.geometry.total_bounds)
    ax1.imshow(approachable_area_within_aoi, cmap='Blues', alpha=0.5, extent=gdf.geometry.total_bounds)
    ax1.imshow(unapproachable_area_within_aoi, cmap='Reds', alpha=0.5, extent=gdf.geometry.total_bounds)

    table_data = [['Area of Interest', np.sum(aoi)],
                  ['Approachable Area', np.sum(approachable_area_within_aoi)],
                  ['Unapproachable Area', np.sum(unapproachable_area_within_aoi)],
                  ['Total Plant Area', total_plant_area]]

    table = ax2.table(cellText=table_data, loc='center', cellLoc='center', colLabels=['Category', 'Area'])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)  
    ax2.axis('off')  

    ax1.set_title('Annotation Map')
    ax2.set_title('Area Summary Table')

    plt.show()

if __name__ == "__main__":
    dtm_path = "D:\\Processed Data (5 Ha)\\DTM\\SURINOVA_CBE_DTM.tif"
    dsm_path = "D:\\Processed Data (5 Ha)\\DSM\\SURINOVA_CBE_DSM.tif"
    orthomosaic_path = "D:\\Processed Data (5 Ha)\\Orthomosaic\\SURINOVA_CBE_ORTHO.tif"

    target_shape = (3070, 2419)

    dtm, transform = read_geotiff(dtm_path, target_shape)
    dsm, _ = read_geotiff(dsm_path, target_shape)
    orthomosaic, _ = read_geotiff(orthomosaic_path, target_shape)

    create_annotation_map(dtm, dsm, orthomosaic)
