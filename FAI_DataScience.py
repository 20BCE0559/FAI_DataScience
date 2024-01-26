import os
import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box
from matplotlib.patches import Polygon
from rasterio.mask import mask
from rasterio.enums import Resampling

# Function to read GeoTIFF file and perform resampling
def read_geotiff_with_auxiliary(file_path, target_shape):
    # Construct the paths for auxiliary files
    tfw_file = file_path.replace('.tif', '.tfw')
    aux_xml_file = file_path + '.aux.xml'
    ovr_file = file_path + '.ovr'

    # Check if the auxiliary files exist
    for file in [tfw_file, aux_xml_file, ovr_file]:
        if not os.path.exists(file):
            raise FileNotFoundError(f"File not found: {file}")

    # Read the GeoTIFF file with auxiliary files
    with rasterio.Env():
        with rasterio.open(file_path) as src:
            data = src.read(1, out_shape=target_shape, resampling=Resampling.bilinear)
            transform = src.transform

    return data, transform

import rasterio.features

# Function to create annotation map
def create_annotation_map(dtm, dsm, orthomosaic):
    # Calculate the height (vegetation) from DSM and DTM
    height = dsm - dtm

    # Define approachable and unapproachable areas based on height threshold
    approachable_threshold = 5  # Adjust as needed
    approachable_area = np.where(height > approachable_threshold, 1, 0)
    unapproachable_area = np.where(height <= approachable_threshold, 1, 0)

    # Define the Area of Interest (AOI) based on a threshold (you can adjust this threshold)
    aoi_threshold = 1
    aoi = np.where(height > aoi_threshold, 1, 0)

    # Combine approachable and unapproachable areas within AOI
    approachable_area_within_aoi = approachable_area * aoi
    unapproachable_area_within_aoi = unapproachable_area * aoi

    # Total Plant Area for the entire map
    total_plant_area = np.sum(approachable_area) + np.sum(unapproachable_area)

    # Create GeoDataFrame for the annotation
    bounds = box(*rasterio.transform.array_bounds(height.shape[0], height.shape[1], transform))
    gdf = gpd.GeoDataFrame({'geometry': [bounds]})

    # Plot the orthomosaic
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))

    # Plot the AOI on the orthomosaic
    aoi_poly = Polygon(gdf.geometry.exterior[0].coords, edgecolor='green', linewidth=2, fill=None)
    ax1.add_patch(aoi_poly)

    # Plot the approachable and unapproachable areas on the orthomosaic
    approachable_poly = Polygon(gdf.geometry.exterior[0].coords, edgecolor='blue', linewidth=2, fill=None)
    ax1.add_patch(approachable_poly)

    unapproachable_poly = Polygon(gdf.geometry.exterior[0].coords, edgecolor='red', linewidth=2, fill=None)
    ax1.add_patch(unapproachable_poly)

    # Disable the axis for the orthomosaic
    ax1.axis('off')

    # Use the mask function to apply the AOI mask to the data
    aoi_mask = rasterio.features.geometry_mask([gdf.geometry.iloc[0]], out_shape=orthomosaic.shape, transform=transform)
    masked_orthomosaic = np.ma.masked_array(orthomosaic, mask=np.logical_not(aoi_mask))

    # Plot the masked orthomosaic using imshow
    extent = rasterio.transform.array_bounds(masked_orthomosaic.shape[0], masked_orthomosaic.shape[1], transform)
    ax1.imshow(masked_orthomosaic, cmap='viridis', extent=extent, interpolation='none')

    # Create a table for the areas
    table_data = [['Area of Interest', np.sum(aoi)],
                  ['Approachable Area', np.sum(approachable_area_within_aoi)],
                  ['Unapproachable Area', np.sum(unapproachable_area_within_aoi)],
                  ['Total Plant Area', total_plant_area]]

    table = ax2.table(cellText=table_data, loc='center', cellLoc='center', colLabels=['Category', 'Area'])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)  # Adjust the table size as needed
    ax2.axis('off')  # Turn off axis for the table

    # Set titles
    ax1.set_title('Annotation Map')
    ax2.set_title('Area Summary Table')

    plt.show()

# Example usage
if __name__ == "__main__":
    # Update the paths accordingly
    dtm_path = "D:\\Processed Data (5 Ha)\\DTM\\SURINOVA_CBE_DTM.tif"
    dsm_path = "D:\\Processed Data (5 Ha)\\DSM\\SURINOVA_CBE_DSM.tif"
    orthomosaic_path = "D:\\Processed Data (5 Ha)\\Orthomosaic\\SURINOVA_CBE_ORTHO.tif"

    # Set the target shape for resampling
    target_shape = (3070, 2419)  # Adjust based on your requirements

    dtm, transform = read_geotiff_with_auxiliary(dtm_path, target_shape)
    dsm, _ = read_geotiff_with_auxiliary(dsm_path, target_shape)
    orthomosaic, _ = read_geotiff_with_auxiliary(orthomosaic_path, target_shape)

    create_annotation_map(dtm, dsm, orthomosaic)

import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box
from rasterio.mask import mask
from rasterio.enums import Resampling

# Function to read GeoTIFF file and perform resampling
def read_geotiff(file_path, target_shape):
    with rasterio.open(file_path) as src:
        data = src.read(1, out_shape=target_shape, resampling=Resampling.bilinear)
        transform = src.transform
    return data, transform

# Function to create annotation map
def create_annotation_map(dtm, dsm, orthomosaic):
    # Calculate the height (vegetation) from DSM and DTM
    height = dsm - dtm

    # Define approachable and unapproachable areas based on height threshold
    approachable_threshold = 5  # Adjust as needed
    approachable_area = np.where(height > approachable_threshold, 1, 0)
    unapproachable_area = np.where(height <= approachable_threshold, 1, 0)

    # Define the Area of Interest (AOI) based on a threshold (you can adjust this threshold)
    aoi_threshold = 1
    aoi = np.where(height > aoi_threshold, 1, 0)

    # Combine approachable and unapproachable areas within AOI
    approachable_area_within_aoi = approachable_area * aoi
    unapproachable_area_within_aoi = unapproachable_area * aoi

    # Total Plant Area for the entire map
    total_plant_area = np.sum(approachable_area) + np.sum(unapproachable_area)

    # Create GeoDataFrame for the annotation
    bounds = box(*rasterio.transform.array_bounds(height.shape[0], height.shape[1], transform))
    gdf = gpd.GeoDataFrame({'geometry': [bounds]})
    
    # Plot the orthomosaic
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))

    # Plot the AOI, approachable, and unapproachable areas on the orthomosaic
    ax1.imshow(orthomosaic, cmap='gray', extent=gdf.geometry.total_bounds, alpha=0.5)
    ax1.imshow(aoi, cmap='Greens', alpha=0.2, extent=gdf.geometry.total_bounds)
    ax1.imshow(approachable_area_within_aoi, cmap='Blues', alpha=0.5, extent=gdf.geometry.total_bounds)
    ax1.imshow(unapproachable_area_within_aoi, cmap='Reds', alpha=0.5, extent=gdf.geometry.total_bounds)

    # Create a table for the areas
    table_data = [['Area of Interest', np.sum(aoi)],
                  ['Approachable Area', np.sum(approachable_area_within_aoi)],
                  ['Unapproachable Area', np.sum(unapproachable_area_within_aoi)],
                  ['Total Plant Area', total_plant_area]]

    table = ax2.table(cellText=table_data, loc='center', cellLoc='center', colLabels=['Category', 'Area'])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)  # Adjust the table size as needed
    ax2.axis('off')  # Turn off axis for the table

    # Set titles
    ax1.set_title('Annotation Map')
    ax2.set_title('Area Summary Table')

    plt.show()

# Example usage
if __name__ == "__main__":
    dtm_path = "D:\\Processed Data (5 Ha)\\DTM\\SURINOVA_CBE_DTM.tif"
    dsm_path = "D:\\Processed Data (5 Ha)\\DSM\\SURINOVA_CBE_DSM.tif"
    orthomosaic_path = "D:\\Processed Data (5 Ha)\\Orthomosaic\\SURINOVA_CBE_ORTHO.tif"

    # Set the target shape for resampling
    target_shape = (3070, 2419)  # Adjust based on your requirements

    dtm, transform = read_geotiff(dtm_path, target_shape)
    dsm, _ = read_geotiff(dsm_path, target_shape)
    orthomosaic, _ = read_geotiff(orthomosaic_path, target_shape)

    create_annotation_map(dtm, dsm, orthomosaic)
