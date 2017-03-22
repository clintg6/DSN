"""

"""

import numpy as np
import nibabel as nib
import glob
from parcel_coords import indices2coords
from parcel_coords import warp_parcels
from warp_streamlines import transform_pts

# control what you want to warp
warp_parcellation = True
warp_streamlines = True

# shared parameters
subject_id = str(100307)
template_path = "/remote/storage/clint/MVT/MVT_template2.nii.gz" # define path to template
ants_path = "/home/clint/antsbin/bin" # define path to ANTs
t_aff = glob.glob("/remote/storage/clint/MVT/MVT_" + subject_id + "*.txt") #path to affine transform
t_warp = glob.glob("/remote/storage/clint/MVT/inverses/MVT_" + subject_id + "*InverseWarp.nii.gz") #path to deformation field

# directly warp parcellation labels
# specify path to native space parcellation and output path to warped parcellation
parcel_in = "/home/clint/Desktop/4dnii/" + subject_id + "/easy_out/ROIv_scale60.nii.gz" 
parcel_out = "/home/clint/Desktop/4dnii/" + subject_id + "/easy_out/test_warped_ROIv_scale60.nii.gz" 
if warp_parcellation:
    print "Warping parcellation " + parcel_in
    warp_parcels(parcel_in,parcel_out,t_aff,t_warp,ants_path,template_path)
    print "Finished " + parcel_out

# direct streamline normalization
# specify path to native space tracts and output path to warped tracts
ref_img_path = "/home/clint/Desktop/4dnii/" + subject_id + "/" + subject_id + ".src.gz.image0.nii.gz" # specify path to native space volume
native_trk = "/home/clint/Desktop/4dnii/" + subject_id + "/" + subject_id + "_10thous.trk.gz"
warped_trk = "/home/clint/Desktop/4dnii/" + subject_id + "/test_" + subject_id + "_10thous.trk.gz"

if warp_streamlines:
    print "Warping streamline file " + native_trk
    template = nib.load(template_path)
    warped_affine = template.affine
    dims = template.header.get_data_shape()
    
    template_trk_header = np.array(('TRACK', 
    [dims[0],dims[1],dims[2]], 
    [warped_affine[0][0], warped_affine[1][1], warped_affine[2][2]], 
    [0.0, 0.0, 0.0], 0, ['', '', '', '', '', '', '', '', '', ''], 
    0, ['', '', '', '', '', '', '', '', '', ''], 
    [[-warped_affine[0][0], 0.0, 0.0, 0.0], 
     [0.0, -warped_affine[1][1], 0.0, 0.0], 
     [0.0, 0.0, warped_affine[2][2], 0.0], 
     [0.0, 0.0, 0.0, 1.0]], '', 'LPS', 'LPS', 
    [1.0, 0.0, 0.0, 0.0, 1.0, 0.0], 
    '', '', '', '', '', '', '', 10000, 2, 1000), 
     dtype=[('id_string', 'S6'), ('dim', '<i2', (3,)), 
         ('voxel_size', '<f4', (3,)), ('origin', '<f4', (3,)), 
         ('n_scalars', '<i2'), ('scalar_name', 'S20', (10,)), 
         ('n_properties', '<i2'), ('property_name', 'S20', (10,)), 
         ('vox_to_ras', '<f4', (4, 4)), ('reserved', 'S444'), 
         ('voxel_order', 'S4'), ('pad2', 'S4'), 
         ('image_orientation_patient', '<f4', (6,)), 
         ('pad1', 'S2'), ('invert_x', 'S1'), ('invert_y', 'S1'), 
         ('invert_z', 'S1'), ('swap_xy', 'S1'), ('swap_yz', 'S1'), 
         ('swap_zx', 'S1'), ('n_count', '<i4'), ('version', '<i4'), 
         ('hdr_size', '<i4')]
         )
        
    streams,hdr = nib.trackvis.read(native_trk)
    offsets = []
    _streams = []
    for sl in streams:
        _streams.append(sl[0])
        offsets.append(_streams[-1].shape[0])
    allpoints = np.vstack(_streams)
    tx_points = transform_pts(allpoints, t_aff, t_warp, ref_img_path, ants_path, template_path, output_space="lps_voxmm")
    offsets = np.cumsum([0]+offsets)
    starts = offsets[:-1]
    stops = offsets[1:]
    new_hdr = template_trk_header.copy()
    new_hdr["n_count"] = len(_streams)
    nib.trackvis.write(warped_trk,[(tx_points[a:b],None,None) for a,b in zip(starts,stops)],hdr_mapping=new_hdr)
    print "Finished " + warped_trk


    
