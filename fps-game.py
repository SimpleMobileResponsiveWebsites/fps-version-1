from panda3d.core import WindowProperties, CollisionTraverser, CollisionNode, CollisionRay, CollisionHandlerQueue
from panda3d.core import CollisionSphere, CollisionBox, Point3
from panda3d.showbase.ShowBase import ShowBase
from panda3d.core import LVector3
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import sys

class FPSGame(ShowBase):
    def __init__(self):
        super().__init__()

        # Window properties (fullscreen disabled, custom size)
        properties = WindowProperties()
        properties.setSize(800, 600)
        self.win.requestProperties(properties)

        # Disable default camera controls
        self.disableMouse()

        # Load a basic scene
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Add a player-controlled camera
        self.camera.setPos(0, 0, 2)
        self.mouse_sensitivity = 0.2
        self.accept("escape", sys.exit)

        # Movement
        self.key_map = {"forward": False, "backward": False, "left": False, "right": False}
        self.accept("w", self.update_key_map, ["forward", True])
        self.accept("w-up", self.update_key_map, ["forward", False])
        self.accept("s", self.update_key_map, ["backward", True])
        self.accept("s-up", self.update_key_map, ["backward", False])
        self.accept("a", self.update_key_map, ["left", True])
        self.accept("a-up", self.update_key_map, ["left", False])
        self.accept("d", self.update_key_map, ["right", True])
        self.accept("d-up", self.update_key_map, ["right", False])

        # Crosshair
        self.crosshair = self.loader.loadModel("models/misc/sphere")
        self.crosshair.setScale(0.01)
        self.crosshair.setColor(1, 0, 0, 1)
        self.crosshair.reparentTo(self.camera)

        # Shooting
        self.accept("mouse1", self.shoot)

        # Game update task
        self.taskMgr.add(self.update, "update")

    def update_key_map(self, key, value):
        self.key_map[key] = value

    def update(self, task):
        # Camera movement
        self.process_mouse()
        self.process_movement()

        return Task.cont

    def process_mouse(self):
        # Get mouse input for looking around
        if self.mouseWatcherNode.hasMouse():
            md = self.win.getPointer(0)
            x = md.getX()
            y = md.getY()

            self.win.movePointer(0, 400, 300)
            self.camera.setH(self.camera.getH() - (x - 400) * self.mouse_sensitivity)
            self.camera.setP(self.camera.getP() - (y - 300) * self.mouse_sensitivity)

    def process_movement(self):
        # WASD movement
        speed = 5 * globalClock.getDt()
        direction = LVector3(0, 0, 0)

        if self.key_map["forward"]:
            direction += self.camera.getQuat().getForward()
        if self.key_map["backward"]:
            direction -= self.camera.getQuat().getForward()
        if self.key_map["left"]:
            direction -= self.camera.getQuat().getRight()
        if self.key_map["right"]:
            direction += self.camera.getQuat().getRight()

        direction.setZ(0)  # Prevent flying
        direction.normalize()

        self.camera.setPos(self.camera.getPos() + direction * speed)

    def shoot(self):
        # Raycasting to simulate shooting
        ray = CollisionRay()
        ray.setOrigin(self.camera.getPos())
        ray.setDirection(self.camera.getQuat().getForward())

        collision_node = CollisionNode("ray")
        collision_node.addSolid(ray)
        collision_node.setFromCollideMask(1)
        collision_node_path = self.camera.attachNewNode(collision_node)

        collision_handler = CollisionHandlerQueue()
        self.cTrav = CollisionTraverser()
        self.cTrav.addCollider(collision_node_path, collision_handler)
        self.cTrav.traverse(self.render)

        if collision_handler.getNumEntries() > 0:
            collision_handler.sortEntries()
            hit = collision_handler.getEntry(0).getIntoNodePath()
            print(f"Hit: {hit}")
        else:
            print("Missed!")

        collision_node_path.removeNode()

# Run the game
game = FPSGame()
game.run()
