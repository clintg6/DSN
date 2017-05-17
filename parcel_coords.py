import numpy as np
import nibabel as nib
import os

def warp_parcels(par_path,par_out,t_aff,t_warp,ants_path,template_path):
    print "Warping parcellation " + par_path
    GM = nib.load(par_path)
    gm = GM.get_data()

    orig_dir = os.getcwd()
    orig_csv_out = "orig_par_coords.csv"
    transforms = "-t [" + str(t_aff) + ", 1] " + "-t " + str(t_warp)

    o_coords = np.array(np.unravel_index(np.flatnonzero(gm), gm.shape, order="C"))
    # convert to world coords
    vox_transform = np.vstack([o_coords[:3,:],np.zeros((1,o_coords.shape[1]))])
    orig_aff = GM.affine
    orig_world_coords = (np.dot(orig_aff,vox_transform) - orig_aff[0,0])[:3]
    orig_world_coords[1,:] = -orig_world_coords[1,:]
    orig_world_coords[0,:] = -orig_world_coords[0,:]
    
    np.savetxt(orig_csv_out,np.hstack([orig_world_coords.T,np.zeros((o_coords.shape[1],1))]),header="x,y,z,t",delimiter=",",fmt="%f")
    # Apply the trandforms to
    os.system(ants_path + "/antsApplyTransformsToPoints " + \
                  "-d 3 " + \
                  "-i " + orig_csv_out + \
                  " -o " + orig_dir + "/parcel.csv " + transforms
                  )
    ants_warped_coords = np.loadtxt(orig_dir + "/parcel.csv", skiprows=1, delimiter=",")[:,:3]
    template = nib.load(template_path)
    warped_affine = template.affine
    adjusted_affine = warped_affine.copy()
    adjusted_affine[0] = -adjusted_affine[0]
    adjusted_affine[1] = -adjusted_affine[1]
    to_transform = np.hstack([ants_warped_coords,np.ones((ants_warped_coords.shape[0],1))])
    new_voxels = (np.dot(np.linalg.inv(adjusted_affine),to_transform.T) + warped_affine[0,0])[:3]
    new_voxels = np.round(new_voxels).astype(np.int16)
    flatgm = gm.reshape(-1)
    gm_inds = np.flatnonzero(gm)
    o_label = flatgm[gm_inds]
    os.chdir(orig_dir)
    
    new_wp = np.zeros_like(gm) # assign native space labels to appropriate template spac voxels
    for l in range(o_label.shape[0]):   
        new_wp[new_voxels[0,l]-1,new_voxels[1,l]-1,new_voxels[2,l]-1] = o_label[l] 

    new_wp_nib = nib.Nifti1Image(new_wp, GM.affine)
    nib.save(new_wp_nib,par_out)
    print "Finished " + par_out
