import math
import numpy as np
from rsoccer_gym.Entities import Robot
from utils.Point import Point
from utils.Geometry import Geometry


PROP_VELOCITY_MIN_FACTOR: float = 0.1
MAX_VELOCITY: float = 1.5
ANGLE_EPSILON: float = 0.1
ANGLE_KP: float = 5
MIN_DIST_TO_PROP_VELOCITY: float = 720

ADJUST_ANGLE_MIN_DIST: float = 50
M_TO_MM: float = 1000.0


class Navigation:

  @staticmethod
  def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)
  
  @staticmethod
  def radians_to_degrees(radians):
    return radians * (180.0 / math.pi)
  
  @staticmethod
  def global_to_local_velocity(vx, vy, theta):
    vx_local = vx * math.cos(theta) + vy * math.sin(theta)
    vy_local = -vx * math.sin(theta) + vy * math.cos(theta)
    return Point(vx_local, vy_local)

  @staticmethod
  def map_value(value, lLower, lHigher, rLower, rHigher):
    if (lHigher - lLower) == 0:
      return
    
    return ((value - lLower) * (rHigher - rLower) / (lHigher - lLower) + rLower)

  @staticmethod
  def filter_obstacles(robot:Point, obstacles: list[Point], radius: float):
    return [obs for obs in obstacles if robot.dist_to(obs) < radius]

  @staticmethod
  def calculate_repulsion_force(robot: Point, obstacles: list[Point], radius: float, factor: float = 500):
    total_force = Point(0,0)
    for obstacle in obstacles:
      distance = robot.dist_to(obstacle)
      if 0 < distance < radius:
        direction = (robot - obstacle).normalize()
        repulsion = factor * (1.0 / distance - 1.0 / radius) / (distance ** 2)
        total_force += direction * repulsion
    
    # max_repulsion = factor / (radius ** 2)
    # if total_force.length() > max_repulsion:
    #   total_force = total_force.normalize() * max_repulsion
    return (total_force * M_TO_MM)

  @staticmethod
  def goToPoint(robot: Robot, target: Point, obstacles: list[Point], radius: float = 500):
    target = Point(target.x * M_TO_MM, target.y * M_TO_MM)
    robot_position = Point(robot.x * M_TO_MM, robot.y * M_TO_MM)
    robot_angle = Navigation.degrees_to_radians(Geometry.normalize_angle(robot.theta, 0, 180))
    
    obstacles = [Point(obs.x * M_TO_MM, obs.y * M_TO_MM) for obs in obstacles]

    max_velocity = MAX_VELOCITY
    distance_to_target = robot_position.dist_to(target)
    kp = ANGLE_KP

    # Use proportional speed to decelerate when getting close to desired target
    proportional_velocity_factor = PROP_VELOCITY_MIN_FACTOR
    min_proportional_distance = MIN_DIST_TO_PROP_VELOCITY

    if distance_to_target <= min_proportional_distance:
      max_velocity = max_velocity * Navigation.map_value(distance_to_target, 0.0, min_proportional_distance, proportional_velocity_factor, 1.0)

    filtered_obs = Navigation.filter_obstacles(robot_position, obstacles, radius)
    
    repulsion_force = Navigation.calculate_repulsion_force(robot_position, filtered_obs, radius)
    attraction_force = (target - robot_position).normalize()
    
    combined_target = target + repulsion_force + attraction_force

    new_target_angle = (combined_target - robot_position).angle()
    d_theta = Geometry.smallest_angle_diff(new_target_angle, robot_angle)

    if distance_to_target > ADJUST_ANGLE_MIN_DIST:
      v_angle = Geometry.abs_smallest_angle_diff(math.pi - ANGLE_EPSILON, d_theta)
      v_proportional = v_angle * (max_velocity / (math.pi - ANGLE_EPSILON))
      global_final_velocity = Geometry.from_polar(max_velocity, new_target_angle + repulsion_force.angle() * 0.7)
      target_velocity = Navigation.global_to_local_velocity(global_final_velocity.x, global_final_velocity.y, robot_angle)

      return target_velocity, -kp * d_theta
    else:
      return Point(0.0, 0.0), -kp * d_theta