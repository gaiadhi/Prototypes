import pandas as pd
import matplotlib.pyplot as plt
import os
#https://pandas.pydata.org/docs/user_guide/visualization.html

def cultivar_plots (dir, block_df, var):

    if var == 'yield':
        col_to_use = 'Unadjusted Yield (kg/ha))'
    elif var == 'co2':
        col_to_use = 'CO2 Emitted (kg/ha)'
    elif var == 'n2':
        col_to_use = 'Nitrogen Used (kg/ha)'
    elif var == 'water':
        col_to_use = 'Water Used (mm)'

    planting_year=[]
    planting_day=[]
    for unique_pdate in block_df['Planting Date'].unique():
         planting_day.append(int(unique_pdate%1000))
         planting_year.append(int(unique_pdate/1000))

    cultivar_yearlyblockyield = pd.DataFrame()

    unique_cultivars = block_df['Cultivar'].unique()
    for i in unique_cultivars:
        print (i)
        yearly_block_yield = []
        for j in planting_year:
            #print (j)
            yearly_block_yield.append(block_df.loc[(block_df['Cultivar'] == i) & ((block_df['Planting Date']/1000).astype("int32")==float(j))][col_to_use].mean())
        print (yearly_block_yield)
        cultivar_yearlyblockyield[i] = yearly_block_yield
    if (len(planting_year) == 1):
        # column chart
        cultivar_yearlyblockyield.plot.barh()
        fname = 'cultivar_'+var+'_barh_plot.png'
    else:
        # box plot
        cultivar_yearlyblockyield.plot.box()
        fname = 'cultivar_' + var + '_box_plot.png'
    #plt.show()
    plt.savefig(os.path.join(dir, fname))
    plt.clf()
    return fname

if __name__ == "__main__":
    block_df = pd.read_pickle('BlockReport_df.pkl')
    cultivar_plots(".", block_df, 'yield')
    cultivar_plots(".", block_df, 'co2')
    cultivar_plots(".", block_df, 'n2')
    cultivar_plots(".", block_df, 'water')




