#!/usr/bin/env python3

"""
Generate and manipulate contrasts offline.
"""
import numpy as np

# Parameters for re-scaling UNI image from range [0, 4096] to range [-.5, .5]
_UNI_SHIFT = -0.5
_UNI_SCALE_FACTOR = 1/2**12

def estimate_signed_inv1(inv1, inv2, uni):
    """
    Given unsigned UNI image and 2nd inversion, estimate the signed 
    1st inversion. This assumes the inv2 image is all positive. This 
    assumption should hold for all reasonable MP2RAGE acquisition
    parameters."""
    # rescale to [-0.5, 0.5]
    uni = rescale_uni(uni)
    #Calculate polarity-corrected S1 given UNI data and magnitude images:
    return ( np.divide(uni, np.abs(inv2), 
                np.zeros_like(uni), where=(inv2!=0))
            * (np.abs(inv1)**2 + np.abs(inv2)**2) )

def make_mp2rage_from_signed_inversions(S1, S2, beta=0):
    """
    Given 2 inversion images from an MP2RAGE sequencen, generate the 
    corresponding MP2RAGE contrast. Note that inversions must be
    polarity-corrected (that is, signed). TODO cite MP2RAGE paper
    """
    MP2RAGEn = S1 * (S2) - beta
    MP2RAGEd = np.square(np.abs(S1))+np.square(np.abs(S2)) + 2 * beta
    return np.divide(MP2RAGEn,MP2RAGEd,out=np.zeros_like(MP2RAGEn), where=(MP2RAGEd!=0))

def rescale_uni(uni):
    return _UNI_SCALE_FACTOR * uni + _UNI_SHIFT #TODO calculate scale factor + shift instead of hardcoding 

def make_mp2rage_from_unsigned(uinv1, uinv2, uuni, beta=0):
    """
    Given arrays of unsigned INV1, INV2, and UNI image data an MP2RAGE 
    acquisition, perform background subtraction and return the result. This 
    requires first recovering an estimate of the signed versions of all images.
    """
    inv1 = estimate_signed_inv1(uinv1, uinv2, uuni)
    inv2 = uinv2 # assume all voxels magnetization has crossed 0 and is rising
    # by time TI2
    
    uni = make_mp2rage_from_signed_inversions(inv1, inv2, beta)
    return (uni -  _UNI_SHIFT)/ _UNI_SCALE_FACTOR, # save in range [0, 4096]

if __name__ == '__main__':
    pass #TODO do we need this?