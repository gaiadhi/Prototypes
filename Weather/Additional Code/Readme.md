**Process to calculate Benchmark** - _TminBenchmark_2010-2014.ipynb and TmaxBenchmark_2010-2014.ipynb_
1. To calculate the benckmark, the closest points surrounding the PoS was taken. 
2. In order to find out the nearest points surrounding the PoS, either the latitude or longitude was increased or decreased by 1 unit, so this results in the 
next co-ordinate surrouding it.
For eg., Nearest points next to (10.5,79.5) are: {(9.5, 79.5), (11.5, 79.5), (10.5,78.5), (10.5, 80.5)}.
3. Once we come with the closest point, we assume that the PoS does not have an IMD value and we try to find the difference between the NASA PoS and IMD of nearby 
point to find bias/error.
4. We average the errors to find the MAE or use formulae to find other error metrics like MSE, RMSE.
5. Once we find these error metrics, we use these values as the base and try to find a better method that will reduce the error values (which turned out to be LR).


**Data used now**
1. We have used data for the years 2010-2014, a duration of 5 years, on the following 16 coordinates:
   {(8.5, 76.5​), (9.5, 76.5​), (10.5, 76.5​), (8.5, 78.5​), (9.5, 77.5​), (10.5, 77.5​), (11.5, 77.5​), (9.5, 78.5), (10.5, 78.5​), (11.5, 78.5​), (9.5, 79.5​), (10.5, 79.5​), (12.5, 78.5​), (12.5, 79.5​), (12.5, 80.5​), (11.5, 79.5​)}


**Testing data** - _RunningTests.ipynb_
1. Data used for test on TMIN and TMAX are random 20 records from the dataset of TMIN and TMAX respectively.
2. The 20 records included the columns: Date, Latitude, Longitude, NASA and IMD where IMD was the target variable.
3. IMD column was deleted before using the prediction algorithms and the predicted values were compared with the IMD column values to check the prediction error which was meant to be minimized.
4. The actual IMD and predicted values were compared using visualisations as well.


**Algorithms used** - _TminPrediction With Seasonality 2010-2014.ipynb and TmaxPrediction With Seasonality 2010-2014.ipynb_
1. Various ML algorithms were used to predict the temperature values before decieding which algorithm works best for predicting the minimum and maximum temperatures respectively.
2. It was found that Linear Regression with seasonality worked best for both and this was finally used.
3. The other algorithms used for comparison are: Lasso, Ridge, SVM, and Benchmark. This was compared with and without seasonality which totals out to 10 different methods.
4. All of these implementations are also attached to this folder
