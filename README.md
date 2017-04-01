# DSN
Direct Streamline Normalization (DSN)

DSN overcomes both of the limitations of traditional reorientation approaches for spatially normalization diffusion data. DSN directly warps the subject's streamlines into the template space using the deformation fields from the normalization, avoiding the problem of generating tracts from distorted diffusion information. With DSN, DWI's can be acquired with any desired sampling scheme. Diffusion tensors, FODs, or ODFs can also be reconstructed using any desired method and streamlines generated using any algorithm. DSN has minimal influence on tract structure and topologic organization with no significant difference in network density and assortativity with only very small to small effect sizes after normalization. 

## Installation
Download the current version of DSN and enter its directory:

```bash
$ git clone https://github.com/clintg6/DSN.git
$ cd DSN
```
Next launch a python session in the DSN directory

```
$ python
>>> from warp import Warp
```
This will import the Warp class and the necessary methods for warping streamlines and parcellations directly into the template space. Currrently only TrackVis (.trk, trk.gz) and NIFTI (.nii, .nii.gz) are supported. Support for .tck (mrTRIX) and .vtk (Camino, MITK) is in development.

## Define paths
The path to the template volume, ANTs, and the associated output transforms from subject space to template space must be specified for both streamlines and parcellations 

```
template_path = "/remote/storage/clint/MVT/MVT_template2.nii.gz" # path to template
ants_path = "/home/clint/antsbin/bin" # path to ANTs
t_aff = "/remote/storage/clint/MVT/MVT_100307_T1w_Warped0Affine.txt" # path to affine transform
t_warp = "/remote/storage/clint/MVT/inverses/MVT_100307_T1w_Warped0InverseWarp.nii.gz" # path to deformation field
```

It is necessary to also specifiy the path to a native space reference volume where the native streamlines were constructed for streamline warping.

```
ref_img_path = "/remote/storage/clint/MVT/QA/100307_fa0.nii.gz"
```

## Warping
### Streamlines
Specify the path to the streamlines in native space and the output path you would like the warped streamlines to be saved.
```
native_trk = "/home/clint/Desktop/4dnii/100307/100307_10thous.trk.gz"
warped_trk = "/home/clint/Desktop/4dnii/100307/warped_100307_10thous.trk.gz"
```
To warp streamlines call Warp with the following path parameters:
```
wS = Warp(ants_path,native_trk,warped_trk,template_path,t_aff,t_warp,ref_img_path)
```
To begin warping the streamlines:
```
wS.streamlines()
```

### Parcellations
Specify the path to the parcellation in native space and the output path you would like the warped parcellation to be saved.
```
nat_par_path = "/home/clint/Desktop/4dnii/100307/easy_out/ROIv_scale60.nii.gz" 
warped_par_path = "/home/clint/Desktop/4dnii/100307/easy_out/warped_ROIv_scale60.nii.gz" 
```
To warp a parcellation call Warp with the following path parameters:
```
wP = Warp(ants_path,nat_par_path,warped_par_path,template_path,t_aff,t_warp)
```
To warp the parcellation:
```
wP.parcellation()
```

Credits
========
This source code was sponsored by a grant from the GE/NFL head health challenge. 
The content of the information does not necessarily reflect the position or
the policy of these companies, and no official endorsement should be inferred.

Authors
-------
 * Clint Greene
 * Matt Cieslak


