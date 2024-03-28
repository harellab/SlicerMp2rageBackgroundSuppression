import logging
import os
import numpy as np
from typing import Annotated, Optional
import vtk
import SampleData
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode


#
# BackgroundNoiseSuppression
#

class BackgroundNoiseSuppression(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Background Noise Suppression"
        self.parent.categories = ["Filtering"] 
        self.parent.dependencies = [] 
        self.parent.contributors = ["Sam Brenny (UMN CMRR), Henry Braun (UMN CMRR)"]
        self.parent.helpText = """
This is a module for 3D Slicer that is used to filter background noise (aka denoising) for MP2RAGE Image acquisitions. 
For more information on this extension, visit https://github.com/harellab/SlicerUHFMRTools.
"""
        self.parent.acknowledgementText = """
Development of mp2rageBackgroundSuppression was supported in part by the following NIH grants:
Udall NIH P50 NS123109
"""

#
# BackgroundNoiseSuppressionParameterNode
#

@parameterNodeWrapper
class BackgroundNoiseSuppressionParameterNode:
    """
    The parameters needed by module.

    UNI_Image - The volume to suppress background noise.
    INV1_Image - The volume of the first inversion.
    INV2_Image - The volume of the second inversion.
    Output_Image - The output volume of the background-filtered UNI volume.
    """
    UNIInputVolume: vtkMRMLScalarVolumeNode
    INV1InputVolume: vtkMRMLScalarVolumeNode
    INV2InputVolume: vtkMRMLScalarVolumeNode
    OutputVolume: vtkMRMLScalarVolumeNode

#
# BackgroundNoiseSuppressionWidget
#

class BackgroundNoiseSuppressionWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/BackgroundNoiseSuppression.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = BackgroundNoiseSuppressionLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self) -> None:
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Removed code to Select default input nodes if nothing is selected yet

    def setParameterNode(self, inputParameterNode: Optional[BackgroundNoiseSuppressionParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if all([self._parameterNode,
                self._parameterNode.UNIInputVolume,
                self._parameterNode.INV1InputVolume,
                self._parameterNode.INV2InputVolume,
                self._parameterNode.OutputVolume]):  
            self.ui.applyButton.toolTip = "Apply background suppression"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input and output volume nodes"
            self.ui.applyButton.enabled = False

    def onApplyButton(self) -> None:
        """
        Run processing when user clicks "Apply" button.
        """
    
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(self.ui.UNI_Image.currentNode(), self.ui.INV1_Image.currentNode(), self.ui.INV2_Image.currentNode(),
                               self.ui.Output_Image.currentNode(), self.ui.DoubleSpinBox.value)
            # Default suppression strength = 1000
#
# BackgroundNoiseSuppressionLogic
#

class BackgroundNoiseSuppressionLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def getParameterNode(self):
        return BackgroundNoiseSuppressionParameterNode(super().getParameterNode())

    @staticmethod
    def assertVolumesAreAligned(volumes_to_check):
        ERR_TOL = 1E-15
        main_volume = volumes_to_check[0]
        main_shape = np.shape(slicer.util.arrayFromVolume(main_volume))

        # get ijk to ras matrix as a numpy array
        __tmp = vtk.vtkMatrix4x4()
        main_volume.GetIJKToRASMatrix(__tmp)
        main_sform = slicer.util.arrayFromVTKMatrix(__tmp)

        for check_volume in volumes_to_check[1:]:
            check_shape = np.shape(slicer.util.arrayFromVolume(check_volume))

            # get ijk to ras matrix as a numpy array
            __tmp = vtk.vtkMatrix4x4()
            check_volume.GetIJKToRASMatrix(__tmp)
            check_sform = slicer.util.arrayFromVTKMatrix(__tmp)

            if np.any(np.abs(main_sform - check_sform) > ERR_TOL):
                raise ValueError(f"IJK to RAS matrix of {check_volume.GetName()} "
                    + f"does not match that of {main_volume.GetName()}. " 
                    + "Double-check your data and re-sample to a common grid "
                    + "if necessary.")
            if np.any(main_shape != check_shape):
                raise ValueError(f"Voxel array of {check_volume.GetName()} is "
                    + f"size {str(check_shape)} but {main_volume.GetName()} is "
                    + f" size {str(main_shape)}. " 
                    + "Double-check your data and re-sample to a common grid "
                    + "if necessary.")
            

    def process(self,
                UNI_Image: vtkMRMLScalarVolumeNode, #UNI image
                INV1_Image: vtkMRMLScalarVolumeNode, #INV1 image
                INV2_Image: vtkMRMLScalarVolumeNode, #INV2 image
                Output_Image: vtkMRMLScalarVolumeNode, #output image
                Strength: float, 
                ) -> None:
        """
        Run the processing algorithm.
        :param UNI_Image: Volume to suppress background noise.
        :param INV1_Image: Volume of the first inversion.
        :param INV2_Image: Volume of the second inversion.
        :param Output_Image: Output volume of the background-filtered UNI volume.
        :param Strength: Strength of background noise suppression.
        """
       
        logging.info(f'UNI_Image is {UNI_Image.GetName()}')
        logging.info(f'INV1_Image is {INV1_Image.GetName()}')
        logging.info(f'INV2_Image is {INV2_Image.GetName()}')
        for check_val in [UNI_Image, INV1_Image, INV2_Image, Output_Image]:
            if not check_val:
                raise ValueError(f"input or output argument volume is invalid")

        self.assertVolumesAreAligned([UNI_Image, INV1_Image, INV2_Image])

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Run background suppression
        from Modules.mp2rage_contrasts import make_mp2rage_from_unsigned
        # Calculate ouput voxel data
        out_array = make_mp2rage_from_unsigned(
            slicer.util.arrayFromVolume(INV1_Image),
            slicer.util.arrayFromVolume(INV2_Image),
            slicer.util.arrayFromVolume(UNI_Image),
            Strength, #TODO fix hardcoding
            range_in = None,
            range_out=[0, 4095]
        )
        
        # Store result in output volume
        slicer.util.updateVolumeFromArray(Output_Image, out_array.astype(np.short))
        # Copy orientation affine from UNI image to output volume
        ijkToRas = vtk.vtkMatrix4x4()
        UNI_Image.GetIJKToRASMatrix(ijkToRas)
        Output_Image.SetIJKToRASMatrix(ijkToRas)
        #TODO make sure IJK to RAS direction matrix is correct for all orientations

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# BackgroundNoiseSuppressionTest
def registerSampleData():
        # Load test data
        SampleData.SampleDataLogic.registerCustomSampleDataSource(
        category='UNI',
        sampleName='UNI_Img',
        uris="https://github.com/harellab/SlicerDataRepository/raw/v0.0.1/BackgroundNoiseSupression/UNI_Test.nrrd",
        fileNames='UNI_Test.nrrd',
        checksums='SHA256:01d89243b52831d00adff018f5a9f1790bf5732ac4c904ac1ef3be58aec621a4',
        nodeNames='UNI_Img'
    ) 
        SampleData.SampleDataLogic.registerCustomSampleDataSource(
        category='INV1',
        sampleName='INV1_Img',
        uris="https://github.com/harellab/SlicerDataRepository/raw/v0.0.1/BackgroundNoiseSupression/INV1_Test.nrrd",
        fileNames='INV1_Test.nrrd',
        checksums='SHA256:500b05ce7264f2876b790b06bbcaf97ba8022b88cfd1ce1249f72dae511b55d5',
        nodeNames='INV1_Img'
    )
        SampleData.SampleDataLogic.registerCustomSampleDataSource(
        category='INV2',
        sampleName='INV2_Img',
        uris="https://github.com/harellab/SlicerDataRepository/raw/v0.0.1/BackgroundNoiseSupression/INV2_Test.nrrd",
        fileNames='INV2_Test.nrrd',
        checksums='SHA256:0dc90737c3209d565a3f0ce000dde04717b3b3201f8c633c9ab9d381101fe87f',
        nodeNames='INV2_Img'
    )

class BackgroundNoiseSuppressionTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()
    
    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        
        self.test_BackgroundNoiseSuppression1()
        # TODO add tests for invalid input data. e.g.: 
        #self.test_ijkrasmismatch()

    def test_BackgroundNoiseSuppression1(self):
        logic = BackgroundNoiseSuppressionLogic()

        registerSampleData()
        UNI_Img = SampleData.downloadSample('UNI_Img')
        INV1_Img = SampleData.downloadSample('INV1_Img')
        INV2_Img = SampleData.downloadSample('INV2_Img')

        # Run test
        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        outputVolume.SetName("Test_Output")
        logic.process(UNI_Img,INV1_Img,INV2_Img,outputVolume, 1000)
