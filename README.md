# MorphoExtract
The purpose of this script is to automatically extract a set of measures from .tif or .ims single planes or stacks created in Bitplane Imaris. It was originally create to evaluate microglia morphology.
This script was tested for Bitplane Imaris versions above 7.4. .ims files generated in prior versions might not work. 

IMPORTANT: If you are running this script on multiple files with more than one color channel, make sure all the channels are in the same order for all images!

Available morphological parameters to select from:

		Fractal Dimension - Measure of complexity derived from box-counting methodology. Uses BoneJ algorithm - http://bonej.org/fractal
		
		Convex Hull - smallest bounding polygon - ConvexHull3D plugin - https://imagej.nih.gov/ij/plugins/3d-convex-hull/index.html
		
		Solidity - Area or Volume /Convex Hull - ConvexHull3D plugin - https://imagej.nih.gov/ij/plugins/3d-convex-hull/index.html

Created by Pedro Ferreira @ https://github.com/PedroACFerreira

If used for publication purposes, please cite as: 

Ferreira, P (2019) Automated ImageJ script for morphological parameters extraction from microscopy images. https://github.com/PedroACFerreira/MorphoExtract

Also cite the authors of the plugins mentioned above!
