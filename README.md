Reciprocal space viewer
=======================

This program reconstructs reciprocal space from diffraction
images. The orientation matrix is not necessary; only diffraction
geometry is required.

This program is inteded to visualize pathologies in the dataset such
as multiple-lattice, twinning, modulation, diffuse scattering and high
background. It is also useful for education.

Install
=======

1.  Build cctbx and DIALS.  
2.  Clone this repository your cctbx source directory, where you have 
    cctbx, dstbx, dials folders among others.
3.  Go to your cctbx build directory.
4.  Run libtbx.configure recviewer
5.  make

How to use
==========

Visuallization
==============

The output is in CCP4 map format (also known as MRC format). Thus, you
can use PyMOL, Chimera, Coot for visuallization. I suggest PyMOL's
volume rendering, provided that you have a decent video card.

PyMOL
-----

1.  Start PyMOL
2.  load output.ccp4 (if the file extension is .map, you have to add ', format=ccp4')
3.  Click [A] button and select [Volume]-[default].
4.  Click [Volume] button in the menu window. Adjust transfer function.
5.  For better quality of rendering,  
    set volume_layers, 512 (or even more, but it makes rendering slower)

Depending on the dataset, you might need  
set volume_data_range, 10
. The default is 5.

License
=======

Same as cctbx and DIALS. That is BSD license.


