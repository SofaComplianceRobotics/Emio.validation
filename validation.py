
from modules.targets import Targets
import Sofa


class TargetController(Sofa.Core.Controller):

    def __init__(self, target, effector, assembly):
        Sofa.Core.Controller.__init__(self)
        self.name="TargetController"

        self.positions = target.getMechanicalState().position.value
        self.steps = len(self.positions)
        self.effector = effector
        self.assembly = assembly

        self.animationSteps = 20 # Number of steps before going to the next target
        self.animationStep = self.animationSteps

    def onAnimateBeginEvent(self, _):

        if self.assembly.done:
            self.animationStep -= 1
            if self.steps >= 0 and self.animationStep == 0:
                self.steps -= 1
                self.animationStep = self.animationSteps
                self.effector.effectorGoal = [list(self.positions[self.steps]) + [0, 0, 0, 1]]


def createScene(rootnode):
    from utils.header import addHeader, addSolvers
    from parts.controllers.assemblycontroller import AssemblyController
    from parts.emio import Emio, getParserArgs

    args = getParserArgs()

    settings, modelling, simulation = addHeader(rootnode, inverse=True)

    rootnode.dt = 0.01
    rootnode.gravity = [0., -9810., 0.]
    addSolvers(simulation)

    # Add Emio to the scene
    # The args are set from introduction.md 
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

    # Target
    effectorTarget = modelling.addChild('Target')
    effectorTarget.addObject('EulerImplicitSolver', firstOrder=True)
    effectorTarget.addObject('CGLinearSolver', iterations=50, tolerance=1e-10, threshold=1e-10)
    effectorTarget.addObject('MechanicalObject', template='Rigid3',
                             position=[0, -150, 0, 0, 0, 0, 1],
                             showObject=True, showObjectScale=20)

    # Inverse components and GUI
    emio.addInverseComponentAndGUI(effectorTarget.getMechanicalState().position.linkpath)

    # Components for the connection to the real robot 
    emio.addConnectionComponents()

    # cubePositions = Targets(ratio=0.1, center=[0,-150,0], size=50).cube()
    # cube = modelling.addChild("CubeTargets")
    # cube.addObject("MechanicalObject", position=cubePositions, showObject=True, showObjectScale=10, drawMode=0)

    spherePositions = Targets(ratio=0.1, center=[0,-150,0], size=50).sphere()
    sphere = modelling.addChild("SphereTargets")
    sphere.addObject("MechanicalObject", position=spherePositions, showObject=True, showObjectScale=10, drawMode=0)

    rootnode.addObject(TargetController(sphere, emio.effector.EffectorCoord, assembly))

    return rootnode
