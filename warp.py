# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 14:02:38 2017

@author: clint
"""
import numpy as np
import nibabel as nib
from parcel_coords import warp_parcels
from warp_streamlines import transform_pts

class Warp(object):
    def __init__(self,ants_path="",file_in="",file_out="",template_path="",t_aff="",t_warp="",ref_img_path=""):
        self.ants_path = ants_path
        self.file_in = file_in
        self.file_out = file_out
        self.template_path = template_path
        self.ref_img_path = ref_img_path
        self.t_aff = t_aff
        self.t_warp = t_warp
    
    def streamlines(self):
        if not self.file_in.endswith((".trk",".trk.gz")):
            print "File format currently unsupported."
            return
        
        if self.ref_img_path == "":
            print "Specify reference image path: .ref_img_path = path to reference image"
            return
            
        print "Warping streamline file " + self.file_in
        template = nib.load(self.template_path)
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
            
        streams,hdr = nib.trackvis.read(self.file_in)
        offsets = []
        _streams = []
        for sl in streams:
            _streams.append(sl[0])
            offsets.append(_streams[-1].shape[0])
        allpoints = np.vstack(_streams)
        tx_points = transform_pts(allpoints, self.t_aff, self.t_warp, self.ref_img_path, self.ants_path, self.template_path, output_space="lps_voxmm")
        offsets = np.cumsum([0]+offsets)
        starts = offsets[:-1]
        stops = offsets[1:]
        new_hdr = template_trk_header.copy()
        new_hdr["n_count"] = len(_streams)
        nib.trackvis.write(self.file_out,[(tx_points[a:b],None,None) for a,b in zip(starts,stops)],hdr_mapping=new_hdr)
        print "Finished " + self.file_out    
        
    def parcellation(self):
        if not self.file_in.endswith((".nii",".nii.gz")):
            print "File format currently unsupported. Convert to NIFTI."
            return
            
        warp_parcels(self.file_in,self.file_out,self.t_aff,self.t_warp,self.ants_path,self.template_path)