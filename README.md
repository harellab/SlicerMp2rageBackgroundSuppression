# SlicerMp2rageBackgroundSuppression
This is an extension for 3D Slicer that is used to filter background noise (aka denoising) for MP2RAGE Image acquisitions.

Required Inputs:
1. MP2RAGE uniform images (UNI) 
2. The first inversion recovery sequence (INV1) from MP2RAGE
3. The second inversion recovery sequence (INV2) from MP2RAGE

Extension Workflow:
1. Load the MP2RAGE data sets (UNI, INV1, INV2) into 3D Slicer as volumes.
![Alt text](Screenshot1.png)

2. Select the corresponding UNI, INV1, and INV2 volumes.  The supression strength is normalized relative to an estimated noise variance calculated at the corner of the image.  The default suppression strength is set at 1000; useful suppression strength may scale several orders of magnitude.  Higher suppression strength trades increased background noise suppression for increased bias field effects.
3. To filter the background noise, create a new volume or select an existing volume.
![Alt text](Screenshot2.png)


Disclaimer

Mp2rageBackgroundSuppression, same as 3D Slicer, is a research software. It is NOT an FDA-approved medical device. It is not intended for clinical use. The user assumes full responsibility to comply with the appropriate regulations.

Support

Please feel free to contact The Harel Lab github organization for questions, feedback, suggestions or bugs. https://github.com/harellab/SlicerMp2rageBackgroundSuppression/issues

Acknowledgments

Development of SlicerAblationPlanner was supported in part by the following NIH grants:

