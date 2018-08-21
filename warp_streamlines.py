#!/usr/bin/env python
import nibabel as nib
import numpy as np
import os
from scipy.io.matlab import savemat

"""
Takes a set of streamlines, converts them to their 
endpoints, warps them to template space and converts
them to a voxel.
"""

def transform_pts(pts, t_aff, t_warp, ref_img_path, ants_path, template_path,
        out_volume="",output_space="ras_voxels"):
    """
    return coordinates in 
    "ras_voxels" if you want to streamlines in ras ijk coordinates or 
    "lps_voxmm" if you want dsi studio streamline coordinates relative to the template
    """
    if not output_space in ("ras_voxels","lps_voxmm"):
        raise ValueError("Must specify output space")
    orig_dir = os.getcwd()

    warped_csv_out = "warped_output.csv"
    transforms = "-t [" + str(t_aff) + ", 1] " + "-t " + str(t_warp)

    # Load the volume from DSI Studio
    ref_img = nib.load(ref_img_path)
    voxel_size = np.array(ref_img.header.get_zooms())
    extents = np.array(ref_img.shape)
    extents[-1] = 0

    # Convert the streamlines to voxel indices, then to ants points
    voxel_coords =  abs(extents - pts / voxel_size ) 
    ants_mult = np.array([voxel_size[0],voxel_size[1],voxel_size[2]])
    ants_coord = voxel_coords * ants_mult - voxel_size[0]
    ants_coord[:,0] = -ants_coord[:,0]
    ants_coord[:,1] = -ants_coord[:,1]

    # Save the ants coordinates to a csv, then warp them
    np.savetxt(warped_csv_out,np.hstack([ants_coord,np.zeros((ants_coord.shape[0],1))]),
              header="x,y,z,t",delimiter=",",fmt="%f")

    # Apply the trandforms to
    os.system(ants_path + "/antsApplyTransformsToPoints " + \
              "-d 3 " + \
              "-i " + warped_csv_out + \
              " -o " + orig_dir + "/aattp.csv " + transforms
              )
    # Load template to get output space
    template = nib.load(template_path)
    warped_affine = template.affine

    adjusted_affine = warped_affine.copy()
    adjusted_affine[0] = -adjusted_affine[0]
    adjusted_affine[1] = -adjusted_affine[1]

    ants_warped_coords = np.loadtxt(orig_dir + "/aattp.csv", 
            skiprows=1, delimiter=",")[:,:3]
    os.remove("aattp.csv")
    to_transform = np.hstack([ants_warped_coords,np.ones((ants_warped_coords.shape[0],1))])
    new_voxels = (np.dot(np.linalg.inv(adjusted_affine),to_transform.T) + warped_affine[0,0])[:3]

    # Write out an image
    if out_volume:
        newdata = np.zeros(template.get_shape())
        ti, tj, tk = new_voxels.astype(np.int)
        newdata[ti,tj,tk] = 1
        warped_out = nib.Nifti1Image(newdata,warped_affine).to_filename(out_volume)
    os.chdir(orig_dir)
    if output_space == "ras_voxels":
        return new_voxels.astype(np.int).T

    elif output_space == "lps_voxmm":
        template_extents = template.get_shape()
        lps_voxels = new_voxels.copy()
        lps_voxels[0] = template_extents[0] - lps_voxels[0]
        lps_voxels[1] = template_extents[1] - lps_voxels[1]
        lps_voxmm = lps_voxels.T * np.array(template.header.get_zooms())[:3]
        return lps_voxmm




