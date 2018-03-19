"""Plot the results of experiment 2 that ran on BL.
"""

from __future__ import print_function
import nibabel as nib
import numpy as np
import dipy
import scipy
from nibabel.streamlines import load, save 
from compute_voxel_measures import compute_voxel_measures
from compute_streamline_measures import compute_loss_and_bmd, compute_roc_curve_lap
import matplotlib.pyplot as plt


if __name__ == '__main__':

    experiment = 'exp2' #'test' #'exp2'
    sub_list = ['993675']#, '996782', '995174']
    tract_name_list = ['Left_Arcuate']#, 'Callosum_Forceps_Minor']#, 'Right_Cingulum_Cingulate', 'Callosum_Forceps_Major']
    example_list = ['615441', '615744', '616645', '617748', '633847', '634748', '635245', '638049']
    true_tracts_dir = '/N/dc2/projects/lifebid/giulia/data/HCP3_processed_data_trk'
    results_dir = '/N/dc2/projects/lifebid/giulia/results/%s' %experiment

    DSC_values = np.zeros((len(sub_list), len(tract_name_list), len(example_list)))
    cost_values = np.zeros((len(sub_list), len(tract_name_list), len(example_list)))
    loss_values = np.zeros((len(sub_list), len(tract_name_list), len(example_list)))
    BMD_values = np.zeros((len(sub_list), len(tract_name_list), len(example_list)))

    for s, sub in enumerate(sub_list):

    	for t, tract_name in enumerate(tract_name_list):
	
  	    true_tract_filename = '%s/%s/%s_%s_tract.trk' %(true_tracts_dir, sub, sub, tract_name)
	    true_tract = nib.streamlines.load(true_tract_filename)
	    true_tract = true_tract.streamlines

    	    for e, example in enumerate(example_list):
	
	    	estimated_tract_filename = '%s/%s/%s_%s_tract_E%s.tck' %(results_dir, sub, sub, tract_name, example)	
		estimated_tract = nib.streamlines.load(estimated_tract_filename)
	        estimated_tract = estimated_tract.streamlines

	    	DSC, TP, vol_A, vol_B = compute_voxel_measures(estimated_tract, true_tract)	
	    	print("The DSC value is %s" %DSC)

	    	result_lap = np.load('%s/%s/%s_%s_result_lap_E%s.npy' %(results_dir, sub, sub, tract_name, example))
	    	min_cost_values = result_lap[1]
	    	cost = np.sum(min_cost_values)/len(min_cost_values)
		
		loss, BMD = compute_loss_and_bmd(estimated_tract, true_tract)

	    	DSC_values[s,t,e] = DSC
	    	cost_values[s,t,e] = cost
		loss_values[s,t,e] = loss
		BMD_values[s,t,e] = BMD

            #debugging
            DSC, TP, vol_A, vol_B = compute_voxel_measures(estimated_tract, estimated_tract)
            print("The DSC value is %s (must be 1)" %DSC)
            DSC, TP, vol_A, vol_B = compute_voxel_measures(true_tract, true_tract)
            print("The DSC value is %s (must be 1)" %DSC)

    #compute statistics
    DSC_vect = DSC_values.reshape((-1,))
    cost_vect = cost_values.reshape((-1,))
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(DSC_vect, cost_vect)
    print("The R value is %s" %r_value)
    
    # plot
    plt.interactive(True)
    plt.figure()
    color_list = ['g', 'r', 'y', 'b']
    markers_list = ['o', '^', '*', 'd']
    for i in range(len(sub_list)):
	for j in range(len(tract_name_list)):
	    plt.scatter(DSC_values[i,j,:], cost_values[i,j,:], c=color_list[i],  marker=markers_list[j], s=70, label=tract_name_list[j])
    plt.plot(DSC_vect, intercept + slope*DSC_vect, c='r', linestyle=':')
    plt.xlabel("DSC")
    plt.ylabel("cost")
    plt.title('R = %s' %r_value)
    plt.legend(loc=3)
    plt.show()


    target_tractogram_filename = '%s/%s/%s_output_fe.trk' %(true_tracts_dir, sub, sub)
    target_tractogram = nib.streamlines.load(target_tractogram_filename)
    target_tractogram = target_tractogram.streamlines
    superset_idx, true_tract_idx, correspondent_idx, y_true = compute_roc_curve_lap(result_lap, true_tract, target_tractogram)


