from franz.openrdf.connect import ag_connect
from franz.openrdf.query.query import QueryLanguage
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# login credentials for the allegrograph superuser
username = 'esthervandijk'
pw = 'fitbitwearabletest'

# for now there is only one user: 23RGC3, when you want to query another user (when possible)
# you can replace the ID. When doing population or hospital patients analysis, it is not necessary
# to know patient/userID's 

queryString = f"""
PREFIX fitbit:<https://github.com/Swatisoni27/DSIP2023_fieldlab4/tree/main/vocab/>
PREFIX fitbitblob:<https://github.com/Swatisoni27/DSIP2023_fieldlab4/blob/main/vocab/>
SELECT *
WHERE {{?s fitbitblob:userid "23RGC3"^^xsd:string .        
        ?s fitbit:datetime ?date ;
           fitbit:duration ?sleepduration ;
           fitbit:efficiency ?sleepefficiency ;
           fitbit:restingheartrate ?restingheartrate ;
           fitbit:steps ?steps ;
           fitbit:fat ?fat ;
           fitbit:BMI ?bmi ;
           fitbit:veryactiveminutes ?veryactiveminutes ;
           fitbit:sedentaryminutes ?sedentaryminutes ;
           fitbit:lightlyactiveminutes ?lightlyactiveminutes ;
           fitbit:fairlyactiveminutes ?fairlyactiveminutes .}}
ORDER BY ?date
"""

# connect to allegrograph to perform the SPARQL query and transform to pandas dataframe
with ag_connect('DSIP_fieldlab4_fitbit_triples', user=username, password=pw) as conn:
    tupleQuery = conn.prepareTupleQuery(QueryLanguage.SPARQL, queryString)
    result = tupleQuery.evaluate()
    features_user = result.toPandas()
# print(features_user)


## plot that shows the CVH score for the average sleep duration per day and average active minutes per week
# calculate the 'active minutes' per week
features_user['PA_minutes'] = features_user['fairlyactiveminutes'] + features_user['veryactiveminutes']
features_user['weeknumber'] = [features_user['date'][i].isocalendar()[1] for i in range(len(features_user))]
features_per_week = (features_user.groupby('weeknumber').sum())

# life's 8 essentials scale for physical activity:
maximum = max(features_per_week['PA_minutes'])+10
points = np.array([100, 90, 80, 60, 40, 20, 0])
scale = [(150, maximum), (120, 150), (90, 120), (60, 90), (30, 60), (1, 30), (0, 1)]

# plotting parameters
cmap = matplotlib.cm.RdYlGn

bottom, top = 0.1, 0.9
left, right = 0.1, 0.8
size_ticks = 13
size_labels = 15
size_titles = 16

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=[8, 4])
fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=0.15, wspace=0.30)

# active minutes per week subplot
boxplot1 = ax1.boxplot(features_per_week['PA_minutes'].astype(float))
for median in boxplot1['medians']:
    median.set_color('black')
ax1.set_ylabel('Minutes per week', size=size_labels)
ax1.set_xticklabels(['Physical activity'], fontsize=size_labels)
ax1.tick_params(axis='y', labelsize=size_ticks)
ax1.set_ylim(0, maximum)

# background for this subplot
for i, p in enumerate(points):
    ax1.axhspan(ymin=scale[i][0], ymax=scale[i][1], facecolor=cmap(p/100), alpha=0.5)

# life's 8 essentials scale for sleep duration:
maximum = max(features_user['sleepduration'])/(1000*3600)+1
points = np.array([100, 90, 70, 40, 20, 0])
scale = [(7, 9), (9, 10), (6, 7), (5, 6), (4, 5), (0, 4)]

# sleep subplot
mask_sleep = (features_user['sleepduration']!=0)
boxplot2 = ax2.boxplot(features_user['sleepduration'][mask_sleep].astype(float)/(1000*3600))
for median in boxplot2['medians']:
    median.set_color('black')
ax2.set_ylabel('Hours per day', size=size_labels)
ax2.set_xticklabels(['Sleep duration'], fontsize=size_labels)
ax2.tick_params(axis='y', labelsize=size_ticks)
ax2.set_ylim(0, maximum)

# background for subplot 2
for i, p in enumerate(points):
    ax2.axhspan(ymin=scale[i][0], ymax=scale[i][1], facecolor=cmap(p/100), alpha=0.5)
ax2.axhspan(ymin=10, ymax=maximum, facecolor=cmap(40/100), alpha=0.5)

# colorbar
norm = matplotlib.colors.Normalize(0, 100)
cmappable = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
cb_ax = fig.add_axes([0.85, bottom, 0.05, top-bottom])
cb = plt.colorbar(cmappable, ax=(ax1, ax2), cax=cb_ax, ticks=[0, 20, 40, 60, 80, 100])
cb.set_label(label='CVH points', size=size_labels)
cb.ax.tick_params(labelsize=size_ticks)

# save plot
fig.savefig('CVH_scores.png')


## resting heart rate plot

fig5, axes = plt.subplots(1, 1, figsize=[9, 5])
fig5.suptitle('Resting heart rate over a period of two months', fontsize=size_titles)
mask_hr = (features_user['restingheartrate']!=0)
axes.plot(features_user['date'][mask_hr], features_user['restingheartrate'][mask_hr])
axes.set_xlabel('Date', size=size_labels)
axes.set_ylabel('Resting heart rate', size=size_labels)
axes.tick_params(labelsize=14)
axes.grid()
fig5.tight_layout()
fig5.savefig('resting_heart_rate.png')

## steps plot

physical_activity_mask = (features_user['sedentaryminutes']!=1440.0)

fig8, ax = plt.subplots()
fig8.suptitle('Number of steps during two months', size=16)

ax.hist(features_user['steps'][physical_activity_mask].astype(float))
ax.set_ylabel('Number of days', size=15)
ax.set_xlabel('Number of steps', size=15)
ax.tick_params(labelsize=13)

fig8.savefig('steps_hist.png')


### some more figures, that we don't show in our report

# fig1 = plt.figure(figsize=[10, 5])
# plt.scatter(features_user['date'], features_user['sleepduration']/(1000*3600), c=features_user['sleepefficiency'])
# plt.colorbar(label='Sleep efficiency score')
# plt.xlabel('Date', size=size_labels)
# plt.ylabel('Sleep duration (hours)', size=size_labels)
# plt.grid()
# fig1.savefig('sleep_over_time.png')

# mask_sleep = (features_user['sleepduration']!=0)

# fig2 = plt.figure(figsize=[11, 5])
# plt.scatter(features_user['date'][mask_sleep], features_user['sleepduration'][mask_sleep]/(1000*3600),
#              c=features_user['sleepefficiency'][mask_sleep])
# plt.colorbar(label='Sleep efficiency score')
# plt.xlabel('Date')
# plt.ylabel('Sleep duration (hours)')
# plt.grid()
# fig2.savefig('sleep_masked.png')

# # physical activity
# # sedentaryminutes - lightlyactiveminutes - fairlyactiveminutes - veryactiveminutes

# total_sed_minutes = np.sum(features_user['sedentaryminutes'])

# fig3 = plt.figure(figsize=[9, 5])
# plt.scatter(features_user['date'], features_user['sedentaryminutes']/60, color='red', label='Sedentary')
# plt.scatter(features_user['date'], features_user['lightlyactiveminutes']/60, color='orange', label='Lightly active')
# plt.scatter(features_user['date'], features_user['fairlyactiveminutes']/60, color='yellow', label='Fairly active')
# plt.scatter(features_user['date'], features_user['veryactiveminutes']/60, color='green', label='Very active')
# plt.legend()
# plt.xlabel('Date')
# plt.ylabel('Hours per day')
# plt.grid()
# fig3.savefig('physical_activity.png')

# physical_activity_mask = (features_user['sedentaryminutes']!=1440.0)

# fig4, ax1 = plt.subplots(figsize=[9, 5])
# color='tab:red'
# ax1.scatter(features_user['date'][physical_activity_mask], features_user['sedentaryminutes'][physical_activity_mask]/60,
#              color='red', label='Sedentary')
# ax1.scatter(features_user['date'][physical_activity_mask], features_user['lightlyactiveminutes'][physical_activity_mask]/60,
#              color='orange', label='Lightly active')
# ax1.scatter(features_user['date'][physical_activity_mask], features_user['fairlyactiveminutes'][physical_activity_mask]/60,
#              color='yellow', label='Fairly active')
# ax1.scatter(features_user['date'][physical_activity_mask], features_user['veryactiveminutes'][physical_activity_mask]/60,
#              color='green', label='Very active')
# ax1.legend()
# ax1.tick_params(axis='y', labelcolor=color)
# ax1.set_xlabel('Date')
# ax1.set_ylabel('Hours per day', color=color)

# ax2 = ax1.twinx()

# color = 'tab:blue'
# ax2.set_ylabel('Steps', color=color)
# ax2.scatter(features_user['date'][physical_activity_mask], features_user['steps'][physical_activity_mask], color='black', s=4)
# # ax2.plot(features_user['date'][physical_activity_mask], features_user['steps'][physical_activity_mask], color='black')
# ax2.tick_params(axis='y', labelcolor=color)

# fig4.tight_layout()
# fig4.savefig('physical_activity_masked.png')



# data_physical_act = [(features_user['sedentaryminutes'][physical_activity_mask]/60).astype(float),
#                      (features_user['lightlyactiveminutes'][physical_activity_mask]/60).astype(float),
#                      (features_user['fairlyactiveminutes'][physical_activity_mask]/60).astype(float),
#                      (features_user['veryactiveminutes'][physical_activity_mask]/60).astype(float)]
# # Plotting the box plot
# size_labels = 15
# size_ticks = 13
# size_titles = 17
# fig6, ax = plt.subplots(2, 2)
# fig6.suptitle('Physical activity per day during two months', fontsize=size_titles)
# ax[0, 0].boxplot(data_physical_act[0])
# ax[0, 0].set_ylabel('Hours', size=size_labels)
# ax[0, 0].set_xticklabels(['Sedentary'], fontsize=size_labels)
# ax[0, 0].tick_params(axis='y', labelsize=size_ticks)

# ax[0, 1].boxplot(data_physical_act[1])
# ax[0, 1].set_ylabel('Hours', size=size_labels)
# ax[0, 1].set_xticklabels(['Lightly active'], fontsize=size_labels)
# ax[0, 1].tick_params(axis='y', labelsize=size_ticks)

# ax[1, 0].boxplot(data_physical_act[2])
# ax[1, 0].set_ylabel('Hours', size=size_labels)
# ax[1, 0].set_xticklabels(['Fairly active'], fontsize=size_labels)
# ax[1, 0].tick_params(axis='y', labelsize=size_ticks)

# ax[1, 1].boxplot(data_physical_act[3])
# ax[1, 1].set_ylabel('Hours', size=size_labels)
# ax[1, 1].set_xticklabels(['Very active'], fontsize=size_labels)
# ax[1, 1].tick_params(axis='y', labelsize=size_ticks)
# # features_user.boxplot(column=['sedentaryminutes', 'lightlyactiveminutes',
# #                                'fairlyactiveminutes', 'veryactiveminutes'], by='date', ax=ax, vert=False)
# fig6.tight_layout()
# fig6.savefig('physical_activity_boxplot.png')


# fig7, ax = plt.subplots(figsize=[3, 3])
# fig7.suptitle('Number of steps per day', size=13)

# ax.boxplot(features_user['steps'][physical_activity_mask].astype(float))
# ax.set_ylabel('Number of steps', size=13)
# ax.tick_params(axis='y', labelsize=10)
# fig7.tight_layout()
# fig7.savefig('steps_boxplot.png')




# fig9, ax = plt.subplots(figsize=[4, 4])
# fig9.suptitle('Sleep per night during two months', size=13)
# ax.boxplot((features_user['sleepduration'][mask_sleep]/(1000*3600)).astype(float))
# ax.set_ylabel('Average sleep duration (hours)', size=13)
# ax.grid()
# ax.tick_params(axis='y', labelsize=10)
# fig9.tight_layout()
# fig9.savefig('sleep_boxplot.png')