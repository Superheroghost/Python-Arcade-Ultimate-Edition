import unittest

from arcade_ue.physics import CollisionLayer, MovingPlatform, can_collide, create_physics_world


class PhysicsHelperTests(unittest.TestCase):
    def test_moving_platform_ping_pongs_between_endpoints(self):
        platform = MovingPlatform(0, 0, 10, 0, speed=10)
        first = platform.update(0.5)
        second = platform.update(0.5)
        third = platform.update(0.5)
        self.assertEqual(first, (5.0, 0.0))
        self.assertEqual(second, (10.0, 0.0))
        self.assertEqual(third, (5.0, 0.0))

    def test_collision_mask_helper(self):
        self.assertTrue(can_collide(CollisionLayer.PLAYER, CollisionLayer.ENEMY, CollisionLayer.ENEMY))
        self.assertFalse(can_collide(CollisionLayer.PLAYER, CollisionLayer.PICKUP, CollisionLayer.ENEMY))

    def test_physics_world_falls_back_without_pymunk(self):
        world, backend = create_physics_world(prefer_pymunk=False)
        self.assertEqual(backend, "arcade")
        self.assertEqual(world.__class__.__name__, "ArcadePhysicsWorld")


if __name__ == "__main__":
    unittest.main()
