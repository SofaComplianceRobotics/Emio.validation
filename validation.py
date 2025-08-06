
from modules.targets import Targets
import Sofa
import csv

resultsDirectory = "data/results/"


class TargetController(Sofa.Core.Controller):
    """
        A Controller to change the target of Emio, and save the collected data in a CSV file.

        target: Sofa node containing a MechanicalObject with the targets position
        effector: PositionEffector component
        assembly: Controller component for the assembly of Emio (set up animation of the legs and center part)
        steps: number of simulation steps to wait before going to the next target  
    """

    def __init__(self, emio, target, effector, assembly, steps=20):
        Sofa.Core.Controller.__init__(self)
        self.name="TargetController"

        self.emio = emio
        self.targetsPosition = target.getMechanicalState().position.value
        self.targetIndex = len(self.targetsPosition) - 1

        self.effector = effector
        self.assembly = assembly

        self.animationSteps = steps 
        self.animationStep = self.animationSteps
        self.createCSVFile()

    def onAnimateBeginEvent(self, _):
        """
            Change the target when it's time
        """
        if self.assembly.done:
            self.animationStep -= 1
            if self.targetIndex >= 0 and self.animationStep == 0:
                self.writeToCSVFile()
                self.targetIndex -= 1
                self.animationStep = self.animationSteps
                self.effector.effectorGoal = [list(self.targetsPosition[self.targetIndex]) + [0, 0, 0, 1]]

    def createCSVFile(self):
        """
            Clear or create the csv file in which we'll save the data
        """
        legname = self.emio.legsName[0]
        with open(resultsDirectory+legname+'Sphere.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';')
            spamwriter.writerow(["Target", "Simulation"])

    def writeToCSVFile(self):
        """
            Save the data in a csv file
        """
        legname = self.emio.legsName[0]
        with open(resultsDirectory+legname+'Sphere.csv', 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';')
            spamwriter.writerow([self.targetsPosition[self.targetIndex], 
                                 self.emio.effector.getMechanicalState().position.value[0][0:3]])


def createScene(rootnode):
    """
        Emio simulation
    """
    from utils.header import addHeader, addSolvers
    from parts.controllers.assemblycontroller import AssemblyController
    from parts.emio import Emio

    settings, modelling, simulation = addHeader(rootnode, inverse=True)

    rootnode.dt = 0.01
    rootnode.gravity = [0., -9810., 0.]
    addSolvers(simulation)

    # Add Emio to the scene
    emio = Emio(name="Emio",
                legsName=["blueleg"],
                legsModel=["tetra"],
                legsPositionOnMotor=["counterclockwisedown","clockwisedown","counterclockwisedown","clockwisedown"],
                centerPartName="bluepart",
                centerPartType="rigid",
                extended=True)
    if not emio.isValid():
        return

    simulation.addChild(emio)
    emio.attachCenterPartToLegs()
    assembly = AssemblyController(emio)
    emio.addObject(assembly)

    # Effector
    emio.effector.addObject("MechanicalObject", template="Rigid3", position=[0, 0, 0, 0, 0, 0, 1])
    emio.effector.addObject("RigidMapping", index=0)

    # Inverse components and GUI
    emio.addInverseComponentAndGUI([0, 0, 0, 0, 0, 0, 1], withGUI=False)
    emio.effector.EffectorCoord.maxSpeed.value = 50 # Limit the speed of the effector's motion

    # Components for the connection to the real robot 
    emio.addConnectionComponents()

    # Generation of the targets
    spherePositions = Targets(ratio=0.1, center=[0, -130, 0], size=80).sphere()
    sphere = modelling.addChild("SphereTargets")
    sphere.addObject("MechanicalObject", position=spherePositions, showObject=True, showObjectScale=10, drawMode=0)

    # We add a controller to go through the targets
    rootnode.addObject(TargetController(emio=emio,
                                        target=sphere, 
                                        effector=emio.effector.EffectorCoord, 
                                        assembly=assembly,
                                        steps=100))

    return rootnode
