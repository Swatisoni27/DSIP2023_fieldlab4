from franz.openrdf.connect import ag_connect
from franz.openrdf.query.query import QueryLanguage
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

username = 'esthervandijk'
pw = 'fitbitwearabletest'
# "a plain literal"
# "bonjour"@fr
# "13"^^xsd:integer
# "4.2"^^xsd:decimal
# "true"^^xsd:boolean

# if there are multiple users and you want a specific user you could add before the first line:
# (this doesn't work now because we have a dash between user and id)
# ?s fitbit:user-id "{insert user-id here}"^^xsd:string . 

queryString = f"""
PREFIX fitbit:<https://github.com/Swatisoni27/DSIP2023_fieldlab4/tree/main/vocab/>
SELECT *
WHERE {{?s fitbit:datetime ?date ;
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
print(queryString)
with ag_connect('DSIP_fieldlab4', user=username, password=pw) as conn:
    tupleQuery = conn.prepareTupleQuery(QueryLanguage.SPARQL, queryString)
    result = tupleQuery.evaluate()
    features_user = result.toPandas()
print(features_user)

# can actually now if the device is on the wrist through the device api: https://dev.fitbit.com/build/reference/device-api/body-presence/
# plot sleep duration and efficiency

size_labels = 20
size_titles = 20

fig1 = plt.figure(figsize=[10, 5])
plt.scatter(features_user['date'], features_user['sleepduration']/(1000*3600), c=features_user['sleepefficiency'])
plt.colorbar(label='Sleep efficiency score')
plt.xlabel('Date', size=size_labels)
plt.ylabel('Sleep duration (hours)', size=size_labels)
plt.grid()
fig1.savefig('sleep_over_time.png')

mask_sleep = (features_user['sleepduration']!=0)

fig2 = plt.figure(figsize=[11, 5])
plt.scatter(features_user['date'][mask_sleep], features_user['sleepduration'][mask_sleep]/(1000*3600),
             c=features_user['sleepefficiency'][mask_sleep])
plt.colorbar(label='Sleep efficiency score')
plt.xlabel('Date')
plt.ylabel('Sleep duration (hours)')
plt.grid()
fig2.savefig('sleep_masked.png')

# physical activity
# sedentaryminutes - lightlyactiveminutes - fairlyactiveminutes - veryactiveminutes

total_sed_minutes = np.sum(features_user['sedentaryminutes'])

fig3 = plt.figure(figsize=[9, 5])
plt.scatter(features_user['date'], features_user['sedentaryminutes']/60, color='red', label='Sedentary')
plt.scatter(features_user['date'], features_user['lightlyactiveminutes']/60, color='orange', label='Lightly active')
plt.scatter(features_user['date'], features_user['fairlyactiveminutes']/60, color='yellow', label='Fairly active')
plt.scatter(features_user['date'], features_user['veryactiveminutes']/60, color='green', label='Very active')
plt.legend()
plt.xlabel('Date')
plt.ylabel('Hours per day')
plt.grid()
fig3.savefig('physical_activity.png')

physical_activity_mask = (features_user['sedentaryminutes']!=1440.0)

fig4, ax1 = plt.subplots(figsize=[9, 5])
color='tab:red'
ax1.scatter(features_user['date'][physical_activity_mask], features_user['sedentaryminutes'][physical_activity_mask]/60,
             color='red', label='Sedentary')
ax1.scatter(features_user['date'][physical_activity_mask], features_user['lightlyactiveminutes'][physical_activity_mask]/60,
             color='orange', label='Lightly active')
ax1.scatter(features_user['date'][physical_activity_mask], features_user['fairlyactiveminutes'][physical_activity_mask]/60,
             color='yellow', label='Fairly active')
ax1.scatter(features_user['date'][physical_activity_mask], features_user['veryactiveminutes'][physical_activity_mask]/60,
             color='green', label='Very active')
ax1.legend()
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xlabel('Date')
ax1.set_ylabel('Hours per day', color=color)

ax2 = ax1.twinx()

color = 'tab:blue'
ax2.set_ylabel('Steps', color=color)
ax2.scatter(features_user['date'][physical_activity_mask], features_user['steps'][physical_activity_mask], color='black', s=4)
# ax2.plot(features_user['date'][physical_activity_mask], features_user['steps'][physical_activity_mask], color='black')
ax2.tick_params(axis='y', labelcolor=color)

fig4.tight_layout()
fig4.savefig('physical_activity_masked.png')

fig5, axes = plt.subplots(1, 1, figsize=[9, 5])
fig5.suptitle('Resting heart rate over a period of two months', fontsize=size_titles)
mask_hr = (features_user['restingheartrate']!=0)
axes.plot(features_user['date'][mask_hr], features_user['restingheartrate'][mask_hr])
axes.set_xlabel('Date', size=size_labels)
axes.set_ylabel('Resting heart rate', size=size_labels)
axes.tick_params(labelsize=14)
axes.grid()

# axes[1].hist(features_user['restingheartrate'][mask_hr])
# axes[1].set_xlabel('Resting heart rate')
# axes[1].set_ylabel('Number of days')
fig5.tight_layout()
fig5.savefig('resting_heart_rate.png')


data_physical_act = [(features_user['sedentaryminutes'][physical_activity_mask]/60).astype(float),
                     (features_user['lightlyactiveminutes'][physical_activity_mask]/60).astype(float),
                     (features_user['fairlyactiveminutes'][physical_activity_mask]/60).astype(float),
                     (features_user['veryactiveminutes'][physical_activity_mask]/60).astype(float)]
# Plotting the box plot
size_labels = 15
size_ticks = 13
size_titles = 17
fig6, ax = plt.subplots(2, 2)
fig6.suptitle('Physical activity per day during two months', fontsize=size_titles)
ax[0, 0].boxplot(data_physical_act[0])
ax[0, 0].set_ylabel('Hours', size=size_labels)
ax[0, 0].set_xticklabels(['Sedentary'], fontsize=size_labels)
ax[0, 0].tick_params(axis='y', labelsize=size_ticks)

ax[0, 1].boxplot(data_physical_act[1])
ax[0, 1].set_ylabel('Hours', size=size_labels)
ax[0, 1].set_xticklabels(['Lightly active'], fontsize=size_labels)
ax[0, 1].tick_params(axis='y', labelsize=size_ticks)

ax[1, 0].boxplot(data_physical_act[2])
ax[1, 0].set_ylabel('Hours', size=size_labels)
ax[1, 0].set_xticklabels(['Fairly active'], fontsize=size_labels)
ax[1, 0].tick_params(axis='y', labelsize=size_ticks)

ax[1, 1].boxplot(data_physical_act[3])
ax[1, 1].set_ylabel('Hours', size=size_labels)
ax[1, 1].set_xticklabels(['Very active'], fontsize=size_labels)
ax[1, 1].tick_params(axis='y', labelsize=size_ticks)
# features_user.boxplot(column=['sedentaryminutes', 'lightlyactiveminutes',
#                                'fairlyactiveminutes', 'veryactiveminutes'], by='date', ax=ax, vert=False)
fig6.tight_layout()
fig6.savefig('physical_activity_boxplot.png')


fig7, ax = plt.subplots(figsize=[3, 3])
fig7.suptitle('Number of steps per day', size=13)

ax.boxplot(features_user['steps'][physical_activity_mask].astype(float))
ax.set_ylabel('Number of steps', size=13)
ax.tick_params(axis='y', labelsize=10)
fig7.tight_layout()
fig7.savefig('steps_boxplot.png')

fig8, ax = plt.subplots()
fig8.suptitle('Number of steps during two months', size=16)

ax.hist(features_user['steps'][physical_activity_mask].astype(float))
ax.set_ylabel('Number of days', size=15)
ax.set_xlabel('Number of steps', size=15)
ax.tick_params(labelsize=13)

fig8.savefig('steps_hist.png')


fig9, ax = plt.subplots(figsize=[4, 4])
fig9.suptitle('Sleep per night during two months', size=13)
ax.boxplot((features_user['sleepduration'][mask_sleep]/(1000*3600)).astype(float))
ax.set_ylabel('Average sleep duration (hours)', size=13)
ax.grid()
ax.tick_params(axis='y', labelsize=10)
fig9.tight_layout()
fig9.savefig('sleep_boxplot.png')