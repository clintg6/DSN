import numpy as np
import nibabel as nib
import os

def indices2coords(inds, dims): 
    coors = np.zeros((len(dims),inds.shape[0]),dtype=np.int16,order='F')
    for d in range(len(dims)-1,-1,-1):
        coors[d,:] = np.floor((inds-1) / np.prod(dims[0:d])) + 1
        inds = inds - (coors[d,:]-1) * np.array([np.prod(dims[0:d])])  
    return coors

def coords2indices(coors, dims):
	inds = coors[:,0]
	for d in range(1,len(dims)):
		inds = inds + (coors[:,d]-1) * np.prod(dims[0:d])
	return inds

def warp_parcels(par_path,par_out,t_aff,t_warp,ants_path,template_path):
    print "Warping parcellation " + par_path
    GM = nib.load(par_path)
    gm = GM.get_data()
    dims = GM.get_header()['dim'][1:4]
    gm_vals = np.array([val for (i, val) in enumerate(gm.reshape(-1,order="F")) if val >= 1])
    gm_keys = np.unique(gm_vals)
    o_coords = np.empty([4,0],dtype=np.int16)
    orig_dir = os.getcwd()
    orig_csv_out = "orig_par_coords.csv"
    transforms = "-t [" + str(t_aff[0]) + ", 1] " + "-t " + str(t_warp[0])
    
    for key in range(1,np.max(gm_keys)+1):
        #print key
        gm_inds = np.array([i for (i, val) in enumerate(gm.reshape(-1,order="F")) if val == key]) + 1
        gm_coords = indices2coords(gm_inds,dims)
        gm_coords = np.vstack((gm_coords,np.tile(key,(1,gm_coords.shape[1]))))
        o_coords = np.hstack((gm_coords,o_coords))
        #parcel_lookup[key] = gm_coords
    
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
                  " -o parcel.csv " + transforms
                  )
    ants_warped_coords = np.loadtxt("parcel.csv", skiprows=1, delimiter=",")[:,:3]
    template = nib.load(template_path)
    warped_affine = template.affine
    adjusted_affine = warped_affine.copy()
    adjusted_affine[0] = -adjusted_affine[0]
    adjusted_affine[1] = -adjusted_affine[1]
    to_transform = np.hstack([ants_warped_coords,np.ones((ants_warped_coords.shape[0],1))])
    new_voxels = (np.dot(np.linalg.inv(adjusted_affine),to_transform.T) + warped_affine[0,0])[:3]
    new_voxels = np.round(new_voxels)
    o_label = np.array(np.int16([o_coords[3,:]]))
    os.chdir(orig_dir)
    
    new_wp = np.zeros_like(gm) # assign native space labels to appropriate template spac voxels
    for l in range(o_label.shape[1]):
        new_wp[new_voxels[0,l]-1,new_voxels[1,l]-1,new_voxels[2,l]-1] = o_label[0,l]    
        
    new_wp_nib = nib.Nifti1Image(new_wp, GM.affine)
    nib.save(new_wp_nib,par_out)
    print "Finished " + par_out