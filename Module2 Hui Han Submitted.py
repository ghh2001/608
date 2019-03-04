import datashader as ds # updated , Hui Han
import datashader.transfer_functions as tf
import datashader.glyphs
from datashader import reductions
from datashader.core import bypixel
from datashader.utils import lnglat_to_meters as webm, export_image
from datashader.colors import colormap_select, Greys9, viridis, inferno
import copy


from pyproj import Proj, transform
import numpy as np
import pandas as pd
import urllib
import json
import datetime
import colorlover as cl


#import plotly.plotly as py
import plotly.offline as py# no need for plotly web key
import plotly.graph_objs as go
from plotly import tools

from shapely.geometry import Point, Polygon, shape
# In order to get shapley, you'll need to run [pip install shapely.geometry] from your terminal

from functools import partial

from IPython.display import GeoJSON

py.init_notebook_mode()


#ny = pd.read_csv('pluto_18v2.csv')
ny = pd.read_csv('nyc_pluto_18v2_csv/pluto_18v2.csv')

# Getting rid of some outliers
#ny = ny[(ny['YearBuilt'] > 1850) & (ny['YearBuilt'] < 2020) & (ny['NumFloors'] != 0)]  # no caps
ny = ny[(ny['yearbuilt'] > 1850) & (ny['yearbuilt'] < 2020) & (ny['numfloors'] != 0)]
ny.head()


#tools.set_credentials_file('john19','3oS1hOGMkhQACjzPssJj')  --no need for plotly account, now John

trace = go.Scatter(
    # I'm choosing BBL here because I know it's a unique key.
    x = ny.groupby('yearbuilt').count()['bbl'].index,
    y = ny.groupby('yearbuilt').count()['bbl']
)

layout = go.Layout(
    xaxis = dict(title = 'Year Built'),
    yaxis = dict(title = 'Number of Lots Built')
)

fig = go.Figure(data = [trace], layout = layout)

py.iplot(fig, filename = 'ny-year-built')


# Start your answer here, inserting more cells as you go along
newDF = ny[['numfloors', 'yearbuilt']].copy()# Selecting 2 Coloumns
newDF = newDF.sort_values(by = ['yearbuilt']).copy() # Sorting by Year
newDF['buildingcount'] = 1#assigning all 1 value
floors = ((np.ceil(newDF['numfloors']) - 1) // 10 * 10 + 1).astype(int) # round
newDF['bloorbins'] = ['{0:03d} to {1:03d} Floors'.format(x, x+9) for x in floors] # bins
binnedDF = newDF.groupby(['yearbuilt', 'floorbins'], as_index=False).agg({"buildingcount":'sum'})

trace = go.Heatmap(x=np.array(binnedDF.YearBuilt),
                  y=np.array(binnedDF.FloorBins),
                  z=np.array(binnedDF.BuildingCount),
                  colorscale='Jet')

layout = go.Layout(
    title='Number of Buildings Built',
    xaxis = dict(title = 'Built Year'),
    yaxis = dict(title = 'Binned Floors')
)

fig = go.Figure(data = [trace], layout = layout)

py.iplot(fig, filename = 'FloorsBinned')

Average Number of Floors
In [16]:
trace = go.Scatter(
    x = newDF.groupby(['YearBuilt']).mean()['NumFloors'].index,
    y = newDF.groupby(['YearBuilt']).max()['NumFloors']
)

layout = go.Layout(
    xaxis = dict(title = 'Year Built'),
    yaxis = dict(title = 'Average Number Of FLoors')
)

fig = go.Figure(data = [trace], layout = layout)

py.iplot(fig, filename = 'AvgNumOfFloor')



assess =ny[['AssessTot', 'AssessLand','lon','lat']].copy()
assess['AssBuilding'] = assess['AssessTot'].sub(assess['AssessLand'], axis=0) # Subtract to get Building Value
labels = ['A', 'B', 'C']
assess['AssLandBins'] =  pd.qcut(assess.AssessLand, 3, labels=labels)
assess['AssBuldBins'] =  pd.qcut(assess.AssBuilding, 3, labels=labels)
assess['Comb'] = assess.AssLandBins.astype(str) + '_' + assess.AssBuldBins.astype(str)
assess.Comb = assess.Comb.astype('category')
colors = {'A_A': '#e8a8e8', 'A_B': '#a4acac', 'A_C': '#c85a5a', 
          'B_A': '#b0a5df', 'B_B': '#ad9ea5', 'B_C': '#c85356', 
          'C_A': '#64ccbe', 'C_B': '#a27f8c', 'C_C': '#c74249'}
NewYorkCity   = (( -74.29,  -73.69), (40.49, 40.92))
cvs = ds.Canvas(700, 700, * NewYorkCity)
agg = cvs.points(assess, 'lon', 'lat', ds.count_cat('Comb')) 
view = tf.shade(agg, color_key = colors)
export(tf.spread(view, px=1), 'Cloropleth')



