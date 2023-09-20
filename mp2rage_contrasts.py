#!/usr/bin/env python3

"""
Generate and manipulate contrasts offline.
"""
import argparse
import nibabel as nib
import numpy as np
import sys

from pathlib import Path
from scipy.ndimage import zoom
from warnings import warn


# Parameters for re-scaling UNI image from range [0, 4096] to range [-.5, .5]
_UNI_SHIFT = -0.5
_UNI_SCALE_FACTOR = 1/2**12

def make_psir(S1, S2):
    """
    Given 2 complex inversion images from an MP2RAGE sequence, generate 
    the corresponding PSIR contrast. TODO cite PSIR paper
    """
    
    # Determine polarity
    T1w=np.real(np.multiply(np.conj(S1),S2))
    f=np.sign(T1w) # polarity correction factor
    # Calculate PSIR
    PSIRn=np.multiply(np.abs(S1),f) #Numerator
    PSIRd=(np.abs(PSIRn)+np.abs(S2)) #Denominator
    PSIR=np.divide(PSIRn,PSIRd,
        out=np.zeros_like(PSIRn), where=(PSIRd!=0))
    # clean up edge-case voxels
    mask=(PSIRd>0)
    PSIR=np.multiply(PSIR,mask)
    mask=(PSIR<-2)
    np.put(PSIR,mask,-2)
    mask=(PSIR>2)
    np.put(PSIR,mask,2)
    

    return PSIR

def make_psir_nifti(inv1_file, inv2_file, out_file,
    uni_file=None, 
    inv1_phase = None, inv2_phase=None):
    """
    Given 2 inversion NIFTI files from an MP2RAGE sequence and either
    the scanner-generated MP2RAGE "UNI" image or the phases of the 2 
    inversions, generate the corresponding
    PSIR contrast and write to a NIFTI file. TODO cite PSIR paper

    :param inv1_file: Nifti image of 1st inversion
    :param inv2_file: Path to Nifti image of 2nd inversion
    :param out_file: Path to output file    
    """
    # load complex inputs
    inv1, inv2, header = _load_mp2rage_inputs(inv1_file, inv2_file, 
        uni_file=uni_file, 
        inv1_phase=inv1_phase, inv2_phase=inv2_phase)
    # calculate contrast
    PSIR = make_psir(inv1, inv2)
    # save as nifti
    PSIR_img = nib.nifti1.Nifti1Image(PSIR, None, header)
    PSIR_img.to_filename(out_file)

def make_mp2rage(S1, S2, beta=0):
    """
    Given 2 inversion images from an MP2RAGE sequencen, generate the 
    corresponding MP2RAGE contrast. Note that inversions must be
    polarity-corrected (that is, signed). TODO cite MP2RAGE paper
    """
    MP2RAGEn = S1 * (S2) - beta
    MP2RAGEd = np.square(np.abs(S1))+np.square(np.abs(S2)) + 2 * beta
    return np.divide(MP2RAGEn,MP2RAGEd,out=np.zeros_like(MP2RAGEn), where=(MP2RAGEd!=0))

def _load_mp2rage_inputs(inv1_file, inv2_file,
    uni_file=None, 
    inv1_phase = None, inv2_phase=None,):
    """
    TODO
    """

    #set up and check inputs
    inv1_file = Path(inv1_file)
    inv2_file = Path(inv2_file)

    # determine polarity mode
    if uni_file is not None:
        polarity_mode = 'uni' #get polarity from the UNI image
        uni_file = Path(uni_file)
    elif inv1_phase is not None or inv2_phase is not None:
        polarity_mode = 'phase'
        raise NotImplementedError('Phase output on the scanner is broken, ' +
            'so MP2RAGE recon using phase images is not supported yet!')
    elif uni_file is None:
        polarity_mode = 'mag_only'
        warn('No polarity information was supplied! The real-valued version ' +
            'of MP2RAGE will be used!')
    else:
        raise ValueError('polarity mode could not be determined. ' +
        'This code should be unreachable, how did you get here?')
    

    # load input magnitude data
    img_mag_inv1 = nib.load(inv1_file)
    S1=img_mag_inv1.get_fdata()
    img_mag_inv2 = nib.load(inv2_file)
    S2=img_mag_inv2.get_fdata()
    hdr = img_mag_inv1.header

    # add phase data
    if polarity_mode == 'uni':
        img_uni = nib.load(uni_file)
        uni_data= img_uni.get_fdata()
        # rescale to [-0.5, 0.5]
        uni_data = _UNI_SCALE_FACTOR * uni_data + _UNI_SHIFT
        #Calculate polarity-corrected S1 given UNI data and magnitude images:
        S1 = ( np.divide(uni_data, np.abs(S2), 
                    np.zeros_like(uni_data), where=(S2!=0))
             * (np.abs(S1)**2 + np.abs(S2)**2) )
    elif polarity_mode == 'phase':
        # load phase and add to S1 and S2
        raise NotImplementedError
    elif polarity_mode == 'mag_only':
        pass
    else:
        raise ValueError # should be unreachable

    return S1, S2, hdr

def make_mp2rage_nifti(inv1_file, inv2_file, out_file,
    uni_file=None, 
    inv1_phase = None, inv2_phase=None,
    beta=0):
    """
    Given 2 inversion NIFTI files from an MP2RAGE sequence and either
    the scanner-generated MP2RAGE "UNI" image or the phases of the 2 
    inversions, generate the corresponding
    MP2RAGE contrast and write to a NIFTI file. TODO cite MP2RAGE paper
    """
    out_file = Path(out_file)

    (S1, S2, hdr) = _load_mp2rage_inputs(inv1_file, inv2_file, 
        uni_file, inv1_phase, inv2_phase)

    MP2RAGE = make_mp2rage(S1, S2, beta)
    MP2RAGE_img = nib.nifti1.Nifti1Image(
        (MP2RAGE -  _UNI_SHIFT)/ _UNI_SCALE_FACTOR, # save in range [0, 4096]
        None, header=hdr)
    MP2RAGE_img.to_filename(out_file)

if __name__ == '__main__':
    desc = """ Given scanner MP2RAGE outputs, generate a "denoised" (i.e. 
    background-suppressed) image.) 
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--contrast', '-c', type=str,
        help='Contrast to generate. Choices are "mp2rage" or "psir". Only '
        'MP2RAGE is implemented at this time.') #TODO
    parser.add_argument('inv1_mag', type=str,
        help='magnitude image of 1st inversion.',)
    parser.add_argument('inv2_mag', type=str, 
        help='magnitude image of 2nd inversion.')
    parser.add_argument('out_file', type=str, 
        help='Output NIFTI file to write')
    parser.add_argument('--inv1_phase', '--p1', type=str, 
        default=None,
        help='phase image of 1st inversion. (Not Implemented)') #TODO
    parser.add_argument('--inv2_phase', '--p2', type=str, 
        default=None,
        help='phase image of 2nd inversion. (Not Implemented)') #TODO')
    parser.add_argument('--uni', '-u', '--combined', type=str, 
        default=None,
        help='scanner-generated combined MP2RAGE image ' +
            '(named "UNI_Images" by Siemens")')
    parser.add_argument('--beta', '-b', type=float, default=0.0, 
        help = 'Background suppression strength. 10000 generally works well.')
    args = parser.parse_args(sys.argv[1:])

    if args.contrast.lower() == 'mp2rage':
        make_mp2rage_nifti(args.inv1_mag, args.inv2_mag, args.out_file,
        uni_file=args.uni, beta=args.beta)
    elif args.contrast.lower() == 'psir':
        make_psir_nifti(args.inv1_mag, args.inv2_mag, args.out_file,
        uni_file=args.uni)
    else:
        raise NotImplementedError #TODO implement PSIR