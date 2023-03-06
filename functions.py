#!/bin/python

def getACD_df(outlier_threshold=2.0, DQ='h', extreme=False):
    '''
    Fetches ACD data and applies criteria for training/forcing and erosive/non-erosive.
    Within training/forcing, separation at threshold for extreme model. 
    '''
    import numpy as np
    import pandas as pd
    filename='figure_data/ACD_database_updated_20200819.csv'
    df0 = pd.read_csv(filename, encoding = "ISO-8859-1")
    OldColNames = df0.columns
    NewColNames = ['ID', 'SegName', 'SegCode', 'OnsForm', 'OnsCom', 'BackForm', 'BackElev','BackElevDQ',
                   'BackMat1', 'BackMat2', 'BackCom', 'ShoForm', 'BeachForm', 'ShoMat1', 'ShoMat2', 'ShoCom',
                   'DepClos', 'Iso2m', 'Iso5m', 'Iso10m', 'Iso100m', 'OffMat', 'IceCat', 'Ice', 'IceDQ',
                   'IceCom', 'Eros', 'ErosInt', 'ErosDQ', 'DynProc', 'BulkDens', 'BulkDensDQ', 'OC', 'OCDQ',
                   'SOC', 'SOCDQ', 'Sources', 'Comments', 'CommDQ','Contact', 'Mappers', 'SeaName', 'SeaCode',
                   'SegNo', 'OldNo', 'SegCom', 'ShapeLen', 'ShapeArea','SegLen']
    df0 = df0.rename(dict(zip(OldColNames, NewColNames)), axis='columns')
    if extreme:
        xoutliers = (df0['Eros']>outlier_threshold)
    else:
        xoutliers = (df0['Eros']<=outlier_threshold)
    criteria0 = (df0['Eros']>0) & (df0['BackMat1']=='u')  & (df0['Ice']>0) # Erosive, Unlithified and Ice>0
    if DQ=='hm':
        criteria1 = ((df0['ErosDQ']=='h') | (df0['ErosDQ']=='m')) & xoutliers
    else:
        criteria1 = (df0['ErosDQ']==DQ) & xoutliers
    criteriaBool = criteria0 & criteria1 & xoutliers
    criteriaIndices  = np.arange(1314)[criteria0 & criteria1 & xoutliers]
    df_acd = df0[criteria0 & criteria1 & xoutliers]
    # 
    if DQ=='all':
        criteriaBool = (df0['BackMat1']=='u') & (df0['Eros']>0) & (df0['Ice']>0) & xoutliers
        criteriaIndices  = np.arange(1314)[criteriaBool]
        df_acd = df0[criteriaBool]

    return df_acd, criteriaIndices

def getCentroids(indices=[False,], file='figure_data/ACD_centroids.nc'):
    import xarray as xr
    import numpy as np
    ds = xr.open_dataset(file, decode_times=False)
    if len(indices)==1 and ~indices[0]:
        print('No indices were given. Returning centroids of all segments.')
        indices = np.arange(1314)
    x = ds['cxx'][indices].values
    y = ds['cyy'][indices].values
    return x, y

def segments(file='ACD_database/ACD_database'):
    '''
    Returns the shapes for the ACD coastal segments.
    USAGE:
    import acddatabase as acd
    shape_feature = acd.segments()
    '''
    from cartopy.io.shapereader import Reader
    from cartopy.feature import ShapelyFeature
    import cartopy.crs as ccrs
    shapes = ShapelyFeature(Reader(file).geometries(),ccrs.PlateCarree())
    return shapes