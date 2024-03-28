#!/usr/bin/env python3

"""
Generate and manipulate contrasts offline.
"""
import numpy as np

# Parameters for re-scaling UNI image
UNI_RANGE= [-0.5, 0.5]

def estimate_signed_inv1(inv1, inv2, uni):
    """
    Given unsigned UNI image and 2nd inversion, estimate the signed 
    1st inversion. This assumes the inv2 image is all positive. This 
    assumption should hold for all reasonable MP2RAGE acquisition
    parameters.
    
    :param uni: MP2RAGE ("_UNI") contrast image. Must be scaled to between
        -0.5 and 0.5, and zero-point must be correct.
    """
    inv1 = inv1.astype(float)
    inv2 = inv2.astype(float)
    #Calculate polarity-corrected S1 given UNI data and magnitude images:
    return ( np.divide(uni, np.abs(inv2), 
                np.zeros_like(uni), where=(inv2!=0))
            * (np.abs(inv1)**2 + np.abs(inv2)**2) )

def make_mp2rage_from_signed_inversions(S1, S2, beta=0):
    """
    Given 2 inversion images from an MP2RAGE sequence, generate the 
    corresponding MP2RAGE contrast with background suppression. Note that 
    inversions must be polarity-corrected (that is, signed). TODO cite MP2RAGE paper
    """
    S1 = S1.astype(float)
    S2 = S2.astype(float)
    
    MP2RAGEn = (S1 * (S2)) - beta
    MP2RAGEd = np.square(np.abs(S1))+np.square(np.abs(S2)) + 2*beta
    uni = np.divide(MP2RAGEn,MP2RAGEd,out=np.zeros_like(MP2RAGEn), where=(MP2RAGEd!=0))
    
    return uni

def _estimate_noise(img):
    """Estimate noise standard deviation. 
    Assumes corner of volume containes only air."""
    WINDOW_SIZE = 16 # 1-d length (in voxels) of cube ROI for noise estimation
    noise_window = img[:WINDOW_SIZE, :WINDOW_SIZE, :WINDOW_SIZE]
    return np.std(np.ravel(noise_window))

def rescale_array(in_array, range_in=None, range_out = [0,1]):
    """Linearly rescale input array so that range_in is compressed/expanded to 
    range_out. """
    # cast in_array to float
    in_array = np.array(in_array, dtype=float)

    # if not specified, calculate input range
    if range_in is None:
        range_in = [np.min(np.ravel(in_array)), np.max(np.ravel(in_array))]
    
    # if no rescaling needs to be done, quit early
    if np.all(range_out == range_in):
        return in_array

    # calculate scale factors using 2-point linear equation formula
    scale_factor = (range_out[1] - range_out[0])/(range_in[1] - range_in[0])
    shift = range_out[0] - scale_factor * range_in[0]

    return scale_factor * in_array + shift

def make_mp2rage_from_unsigned(uinv1, uinv2, uuni, strength=0, range_in=None,
        dtype_out=np.single, range_out=UNI_RANGE):
    """
    Given arrays of unsigned INV1, INV2, and UNI image data an MP2RAGE 
    acquisition, perform background subtraction and return the result. This 
    requires first recovering an estimate of the signed versions of all images.
    """

    uuni = rescale_array(uuni, range_in, UNI_RANGE)
    inv1 = estimate_signed_inv1(uinv1, uinv2, uuni)
    # Assume all voxels magnetization has crossed 0 and is rising by time TI2.
    # Therefore unsigned and signed inv2 images are identical.
    inv2 = uinv2 
    
    # Normalize suppression strength by estimated noise level. 
    noise_stdev = _estimate_noise(inv2)
    beta = strength * noise_stdev #TODO should we normalize by variance or standar deviation?

    uni = make_mp2rage_from_signed_inversions(inv1, inv2, beta)
    print(f'UNI is range [{str(np.min(np.ravel(uni)))}, {str(np.max(np.ravel(uni)))}]')
    return rescale_array(uni, UNI_RANGE, range_out).astype(dtype_out)

if __name__ == '__main__':
    pass #TODO do we need this?
