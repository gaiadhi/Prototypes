#Requiremenmts: BlockReport df, admin2 geos supported by Holos, GD_Holos_RenderMP.json.  For Team 9, Spring 2025, these can be found at 
#https://teams.microsoft.com/v2/?tenantId=5cdc5b43-d7be-4caa-8173-729e3b0a62d9
import pandas as pd
import sys
from shapely.geometry import Point, shape, Polygon
import geopandas as gpd
from datetime import datetime
import time
import json

#convert to geo df and display a map
def create_map(avg_df, point_df, avg_col, max_col, min, max):
    if 'geometry' in avg_df.columns:
        geo_pol_df = gpd.GeoDataFrame(avg_df, crs=4326)
        mp = geo_pol_df.explore(column=avg_col,
                                cmap='RdYlGn',
                                vmin=min,
                                vmax=max,
                                marker_kwds=dict(radius=5, fill=True),
                                tooltip_kwds=dict(labels=True),
                                scheme='naturalbreaks',
                                legend=True,
                                k=10,
                                tooltip=True,
                                legend_kwds=dict(colorbar=False),
                                style_kwds=dict(color="black", weight=2, fillOpacity=0.4))
        geo_pnt_df = gpd.GeoDataFrame(point_df, crs=4326)
        # With overlay:
        ap = geo_pnt_df.explore(m=mp,
                                # Do thus for cases where the district map is not available: ap = geo_pnt_df.explore(
                                column='Yield (kg/ha)',
                                # column = max_col,
                                cmap='RdYlGn',
                                # color='dt_name',
                                marker_kwds=dict(radius=5, fill=True),
                                tooltip=True,
                                tooltip_kwds=dict(labels=True),
                                style_kwds=dict(color="black", weight=1, fillOpacity=0.9))
        # style_kwds = dict(stroke=False, fillOpacity=0.9))
    else:
        geo_pnt_df = gpd.GeoDataFrame(point_df, crs=4326)
        # With overlay:
        ap = geo_pnt_df.explore(column='Yield (kg/ha)',
                                # column = max_col,
                                cmap='RdYlGn',
                                # color='dt_name',
                                marker_kwds=dict(radius=5, fill=True),
                                tooltip=True,
                                tooltip_kwds=dict(labels=True),
                                style_kwds=dict(color="black", weight=1, fillOpacity=0.9))
        # style_kwds = dict(stroke=False, fillOpacity=0.9))


    return ap

def create_app_specific_point_max (app, df, block_json): #need to fill in geometry col
    point_df = pd.DataFrame()
    col_name = ''
    if app == 'district-max-water-yield':
        #Cols needed ['Center Lat', 'Center Long', 'Yield (kg/ha)', 'Yield Day', 'Planting Date', 'Water Used (mm)', 'Yield/App Irrigation Prod(kg/ha/mm)', 'Cultivar', 'geometry']]
        col_name = 'Max Water Yield Index'
        point_df = df.groupby('Sub Block ID').agg(Yield_Index=('Yield/App Irrigation Prod(kg/ha/mm)', 'max'))
    elif app == 'district-max-nitrogen-yield':
        #Cols needed ['Center Lat', 'Center Long', 'Yield (kg/ha)', 'Yield Day', 'Planting Date', 'Nitrogen Used (kg/ha)', 'Yield/App Nitrogen Prod(kg/kg)', 'Cultivar', 'geometry']]
        col_name = 'Nirogen Yield Index'
        point_df = df.groupby('Sub Block ID').agg(Yield_Index=('Yield/App Nitrogen Prod(kg/kg)', 'max'))

    point_df.reset_index(inplace=True)
    for index, row in point_df.iterrows():
        if app == 'district-max-water-yield':
            point_rows = df[(df['Sub Block ID']==row['Sub Block ID']) & (df['Yield/App Irrigation Prod(kg/ha/mm)']==row['Yield_Index']) ]
        elif app == 'district-max-nitrogen-yield':
            point_rows = df[(df['Sub Block ID'] == row['Sub Block ID']) & (
                        df['Yield/App Nitrogen Prod(kg/kg)'] == row['Yield_Index'])]
        point_rows.reset_index(inplace=True)
        point_df.at[index, 'Block'] = point_rows.loc[0]['ADM3 Block Name']
        point_df.at[index, 'Cultivar'] = point_rows.loc[0]['Cultivar']
        #point_df.at[index, 'Center Lat'] = point_rows.loc[0]['Center Lat']
        #point_df.at[index, 'Center Long'] = point_rows.loc[0]['Center Long']
        point_df.at[index, 'Yield (kg/ha)'] = point_rows.loc[0]['Unadjusted Yield (kg/ha))']
        point_df.at[index, 'Planting Day'] = (datetime.strptime(
            str(datetime.now().year*1000 + point_rows.loc[0]['Planting Date'].astype(int)%1000), '%Y%j').date()).strftime('%d/%m/%Y')
        # TODO: Harvest Start Date should be in %d/%m/%Y format, but wrap around needs to be fixed; so leaving out Y for now; and fidging the +1 to avoid 365th day
        #point_df.at[index, 'Harvest Start Day'] = (datetime.strptime(
        #    str(datetime.now().year*1000 + (point_rows.loc[0]['Yield Day'].astype(int)+point_rows.loc[0]['Planting Date'].astype(int)%1000)%365+1), '%Y%j').date()).strftime('%d/%m')

        point_df.at[index, 'Start Harvest After'] = point_rows.loc[0]['Yield Day']
        point_df.at[index, 'Treatment Key'] = point_rows.loc[0]['Treatment Name']

        if app == 'district-max-water-yield':
            point_df.at[index, 'Water Used (mm)'] = point_rows.loc[0]['Water Used (mm)']
        elif app == 'district-max-nitrogen-yield':
            point_df.at[index, 'Nitrogen Used (kg/ha)'] = point_rows.loc[0]['Nitrogen Used (kg/ha)']

        #Reading from GD_Holos_RenderMP.json
        for block in block_json['features']:
            if block['properties']['id'] == row['Sub Block ID']:
                poly = Polygon(block['geometry']['coordinates'][0])
                #print(f'bbox {poly}, area {poly.area}')
                point_df.at[index, 'geometry'] = poly
                break

    point_df.drop(columns = {'Sub Block ID'}, inplace=True)
    point_df.rename(columns={'Yield_Index': col_name}, inplace=True)
    return point_df, col_name

#TODO: Worker method to create subsets as needed by methods like create_app_specific_block_avg().
def get_region_index_subset(df, region_col, region, index_col, index_val):
    subset_df = df[(df[region_col]==region) & (df[index_col] == index_val)]
    if subset_df.empty:
        subset_df = df[(df[region_col]==region) & (df[index_col]-index_val).abs().argsort()[:3]]

#Avg needs more work to get subset of rows that are around the avg.  This is being put on hold until there is a need,
# we will go with create_app_specific_block_max() until then
def create_app_specific_block_avg (app, df, tnm):  #replaces avg_dist()
    app_df = pd.DataFrame()
    col_name = ''
    vmin = 0.0
    vmax = 0.0
    if app == 'district-max-water-yield':
        vmin =  df['Yield/App Irrigation Prod(kg/ha/mm)'].min()
        vmax =  df['Yield/App Irrigation Prod(kg/ha/mm)'].max()
        col_name = 'Max Water Yield Index'
        app_df = df.groupby('ADM2 District Name').agg(Yield_Index = ('Yield/App Irrigation Prod(kg/ha/mm)', 'median'))
        app_df.reset_index(inplace=True)
        #df.iloc[(df['Yield/App Irrigation Prod(kg/ha/mm)']-row['Yield_Index']).abs().argsort()[:3]]
        for index, row in app_df.iterrows():
            app_df.at[index,'Avg Yield (kg/ha)'] = df[(df['ADM2 District Name']==row['ADM2 District Name']) & (
                    df['Yield/App Irrigation Prod(kg/ha/mm)'] == row['Yield_Index'])]['Unadjusted Yield (kg/ha))'].mean()
            app_df.at[index, 'Water Used (mm)'] = df[(df['ADM2 District Name'] == row['ADM2 District Name']) & (
                        df['Yield/App Irrigation Prod(kg/ha/mm)'] == row['Yield_Index'])]['Water Used (mm)'].mean()
            #Set Geometry
            if isinstance(tnm, pd.DataFrame):
                for i in range(len(tnm)):
                    if ((app_df['ADM2 District Name'][index]) == (tnm['dtname'][i])):
                        app_df.at[index,'geometry'] = tnm['geometry'][i]
                        break
            else:
                features = tnm['features']
                for i in range(len(features)):
                    if ((app_df['ADM2 District Name'][index]) == (features[i]['properties']['shapeName'])):
                        app_df.at[index,'geometry'] = shape(features[i]['geometry'])
                        break
    elif app == 'district-max-nitrogen-yield':
        col_name = 'Nitrogen Yield Index'
        vmin = df['Yield/App Nitrogen Prod(kg/kg)'].min()
        vmax = df['Yield/App Nitrogen Prod(kg/kg)'].max()
        app_df = df.groupby('ADM2 District Name').agg(Yield_Index = ('Yield/App Nitrogen Prod(kg/kg)', 'median'))
        app_df.reset_index(inplace=True)
        for index, row in app_df.iterrows():
            app_df.at[index,'Avg Yield (kg/ha)'] = df[(df['ADM2 District Name']==row['ADM2 District Name']) & (df['Yield/App Nitrogen Prod(kg/kg)'] == row['Yield_Index'])]['Unadjusted Yield (kg/ha))'].mean()
            app_df.at[index, 'Nitrogen Used (kg/ha)'] = df[(df['ADM2 District Name'] == row['ADM2 District Name']) & (
                        df['Yield/App Nitrogen Prod(kg/kg)'] == row['Yield_Index'])]['Nitrogen Used (kg/ha)'].mean()
            #Set Geometry
            if isinstance(tnm, pd.DataFrame):
                for i in range(len(tnm)):
                    if ((app_df['ADM2 District Name'][index]) == (tnm['dtname'][i])):
                        app_df.at[index,'geometry'] = tnm['geometry'][i]
                        break
            else:
                features = tnm['features']
                for i in range(len(features)):
                    if ((app_df['ADM2 District Name'][index]) == (features[i]['properties']['shapeName'])):
                        app_df.at[index,'geometry'] = shape(features[i]['geometry'])
                        break

    app_df.rename(columns = {'Yield_Index':col_name}, inplace=True)

    return app_df, col_name, vmin, vmax

def create_app_specific_block_max (app, df, tnm):  #replaces avg_dist()
    app_df = pd.DataFrame()
    col_name = ''
    vmin = 0.0
    vmax = 0.0
    if app == 'district-max-water-yield':
        col_name = 'Max Water Yield Index'
        vmin = df['Yield/App Irrigation Prod(kg/ha/mm)'].min()
        vmax = df['Yield/App Irrigation Prod(kg/ha/mm)'].max()
        app_df = df.groupby('ADM2 District Name').agg(Yield_Index = ('Yield/App Irrigation Prod(kg/ha/mm)', 'max'))
        app_df.reset_index(inplace=True)
        #df.iloc[(df['Yield/App Irrigation Prod(kg/ha/mm)']-row['Yield_Index']).abs().argsort()[:3]]
        for index, row in app_df.iterrows():
            app_df.at[index,'Avg Yield (kg/ha)'] = df[(df['ADM2 District Name']==row['ADM2 District Name']) & (
                    df['Yield/App Irrigation Prod(kg/ha/mm)'] == row['Yield_Index'])]['Unadjusted Yield (kg/ha))'].mean()
            app_df.at[index, 'Water Used (mm)'] = df[(df['ADM2 District Name'] == row['ADM2 District Name']) & (
                        df['Yield/App Irrigation Prod(kg/ha/mm)'] == row['Yield_Index'])]['Water Used (mm)'].mean()
            #Set Geometry
            if isinstance(tnm, pd.DataFrame):
                for i in range(len(tnm)):
                    if ((app_df['ADM2 District Name'][index]) == (tnm['dtname'][i])):
                        app_df.at[index,'geometry'] = tnm['geometry'][i]
                        break
            else:
                features = tnm['features']
                for i in range(len(features)):
                    if ((app_df['ADM2 District Name'][index]) == (features[i]['properties']['shapeName'])):
                        app_df.at[index,'geometry'] = shape(features[i]['geometry'])
                        break
    elif app == 'district-max-nitrogen-yield':
        col_name = 'Nitrogen Yield Index'
        vmin = df['Yield/App Nitrogen Prod(kg/kg)'].min()
        vmax = df['Yield/App Nitrogen Prod(kg/kg)'].max()
        app_df = df.groupby('ADM2 District Name').agg(Yield_Index = ('Yield/App Nitrogen Prod(kg/kg)', 'max'))
        app_df.reset_index(inplace=True)
        for index, row in app_df.iterrows():
            app_df.at[index,'Avg Yield (kg/ha)'] = df[(df['ADM2 District Name']==row['ADM2 District Name']) & (
                    df['Yield/App Nitrogen Prod(kg/kg)'] == row['Yield_Index'])]['Unadjusted Yield (kg/ha))'].mean()
            app_df.at[index, 'Nitrogen Used (kg/ha)'] = df[(df['ADM2 District Name'] == row['ADM2 District Name']) & (
                        df['Yield/App Nitrogen Prod(kg/kg)'] == row['Yield_Index'])]['Nitrogen Used (kg/ha)'].mean()
            #Set Geometry
            if isinstance(tnm, pd.DataFrame):
                for i in range(len(tnm)):
                    if ((app_df['ADM2 District Name'][index]) == (tnm['dtname'][i])):
                        app_df.at[index,'geometry'] = tnm['geometry'][i]
                        break
            else:
                features = tnm['features']
                for i in range(len(features)):
                    if ((app_df['ADM2 District Name'][index]) == (features[i]['properties']['shapeName'])):
                        app_df.at[index,'geometry'] = shape(features[i]['geometry'])
                        break

    app_df.rename(columns = {'Yield_Index':col_name}, inplace=True)

    return app_df, col_name, vmin, vmax
#def app_specific_district_level_holos_choropleth (df_fname, app, shapefile, block_json_fname):
def app_specific_district_level_holos_choropleth(app, block_df, block_json, tnm):

    #block_df = pd.read_pickle('TN_Sorghum_BlockReport_df.pkl')

    app_specific_avg_block_df, avg_col, vmin, vmax = create_app_specific_block_max (app, block_df, tnm) #add in app specific data and geometry at district level
    #geometrty in point df is the POINT of center long. lat
    app_specific_max_point_df, max_col = create_app_specific_point_max(app, block_df, block_json)
    #app_specific_avg_block_df.to_excel('app_specific_avg_block_df.xlsx')
    #app_specific_max_point_df.to_excel('app_specific_max_point_df.xlsx')

    mpnew = create_map(app_specific_avg_block_df, app_specific_max_point_df, avg_col, max_col, vmin, vmax) # NEEDED FOR INTEGRATING

    return mpnew

if __name__ == "__main__":
    start = time.time()
    df_name = sys.argv[1]

    #Read data
    block_df = pd.read_pickle(df_name)
    # if shapefile:
    #     # tnm = gpd.read_file('./Shap/tn_shp_gh/TAMIL NADU_DISTRICTS.shp')
    #     tnm = gpd.read_file('TAMIL_NADU_DISTRICTS.shp')
    # else:
    #     with open('/Users/karthik/Downloads/geoBoundaries-IND-ADM2.json') as f:
    #         tnm = json.load(f)
    #For India
    #with open('/Users/karthik/Downloads/geoBoundaries-IND-ADM2.json') as f:
    # For US:
    #with open('/Users/karthik/Downloads/geoBoundariesCGAZ_ADM2.json') as f:
    #    tnm = json.load(f)
    # For Holos supported
    with open('/Users/karthik/Downloads/geoBoundaries_HolosSupported_ADM2.json') as f:
        tnm = json.load(f)

    with open(sys.argv[2]) as f:
        block_json = json.load(f)

    app = 'district-max-water-yield'
    mpnew = app_specific_district_level_holos_choropleth (app, block_df, block_json, tnm)
    outfp = f"holos_{app}_{df_name}_map.html"
    mpnew.save(outfp)
    print (f'Completed in {time.time() - start} secs')

    app = 'district-max-nitrogen-yield'
    mpnew = app_specific_district_level_holos_choropleth (app, block_df, block_json, tnm)
    outfp = f"holos_{app}_{df_name}_map.html"
    mpnew.save(outfp)
    print (f'Completed in {time.time() - start} secs')





