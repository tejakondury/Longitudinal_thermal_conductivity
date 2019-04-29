import numpy as np

r1=np.loadtxt('results_homogenized_composite_avg_1')
r2=np.loadtxt('results_homogenized_composite_avg_2')
r4=np.loadtxt('results_homogenized_composite_avg_4')
r5=np.loadtxt('results_homogenized_composite_avg_5')


#r2=np.loadtxt('results_therm_cond_2step_2_mean')
#r3=np.loadtxt('results_therm_cond_2step_3_mean')
#r4=np.loadtxt('results_therm_cond_2step_4_mean')
#r5=np.loadtxt('results_therm_cond_2step_5_mean')

r=[r1,r2,r4,r5];

temp=[293.0,300.0,325.0,350.0,375.0,400.0,425.0,450.0,475.0,500.0,525.0,550.0,575.0,600.0,605.0,610.0,615.0,616.0,617.0,618.0,619.0,620.0,625.0,630.0,635.0,640.0,645.0,650.0,660.0,665.0,670.0,680.0,690.0,700.0]

res=np.ndarray(shape=(len(temp),6))

# calculate Mean
for q in range(len(temp)):   # cycliing through the tmep range
    temp_point=temp[q]
    cum_sum=0.0
    obs=0.0
    min_val=100.0      # initial set up to get things moving
    max_val=0.0
    for k in range(len(r)):        # cycling through the number of results
        for i in range(len(r[k])): # cycling through each temperature in the result
            if r[k][i][1]==temp_point:
                sum=r[k][i][0]
                cum_sum=cum_sum+sum
                obs=obs+1
                if r[k][i][1]<=min_val:
                    min_val=r[k][i][1]
                if r[k][i][1]>=max_val:
                    max_val=r[k][i][1]


    if obs!=0:
        avg_sum=cum_sum/obs
    else:
        avg_sum=cum_sum

    print ('The average K at temperature',temp_point,'is',avg_sum,'with n = ',obs)
    res[q][0]=temp_point
    res[q][1]=avg_sum
    res[q][2]=min_val
    res[q][3]=max_val
    res[q][4]=obs
# Standard Deviation

for q in range(len(temp)):
	s_diff_sq_cum=0.0
	for k in range(len(r)):
		for i in range(len(r[k])):
			if res[q][4]!=0:
				s_diff=r[k][i][0]-res[q][1]
				s_diff_sq=s_diff*s_diff
				s_diff_sq_cum=s_diff_sq_cum+s_diff_sq
			s_devi=np.sqrt(s_diff_sq_cum/(res[q][4]-1))
			res[q][5]=s_devi

# Plot the results
#print(res)
#plt.scatter(res[:][0],res[:][1])
#plt.show()

# save files into an array
np.savetxt('stat_homog_output',res)
