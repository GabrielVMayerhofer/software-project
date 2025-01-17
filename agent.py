from utils.ssl.Navigation import Navigation
from utils.ssl.base_agent import BaseAgent
from utils.Point import Point

# class ExampleAgent(BaseAgent):
#     def __init__(self, id=0, yellow=False):
#         super().__init__(id, yellow)

#     def distance_target(self):
#         if len(self.targets) == 0:
#             return float('inf')
#         return Point(self.robot.x, self.robot.y).dist_to(self.targets[0])

#     def decision(self):
#         if len(self.targets) == 0:
#             return

#         target_velocity, target_angle_velocity = Navigation.goToPoint(self.robot, self.targets[0])
#         self.set_vel(target_velocity)
#         self.set_angle_vel(target_angle_velocity)

#         return

#     def post_decision(self):
#         pass

class Agents(BaseAgent):
    def __init__(self, id, yellow=False):
        super().__init__(id, yellow)
    
    def distance_target(self):
        if len(self.targets) == 0:
            return float('inf')
        return Point(self.robot.x, self.robot.y).dist_to(self.targets[0])

    def decision(self):
        if len(self.targets) == 0:
            return

        dynamic_obstacles = [Point(r.x, r.y) for r in self.opponents.values()]
        teammate_obstacles = [Point(r.x, r.y) for r_id, r in self.teammates.items() if r_id != self.id]
        all_obstacles = dynamic_obstacles + teammate_obstacles

        target_velocity, target_angle_velocity = Navigation.goToPoint(self.robot, self.targets[0], all_obstacles)
        self.set_vel(target_velocity)
        self.set_angle_vel(target_angle_velocity)

        return

    def post_decision(self):
        pass
    
  

agents = [Agents(id=i, yellow=False) for i in range (10)]
for agent in agents:
    agent_robot = agent.step(agent.robot, opponents = agent.opponents, teammates = agent.teammates, targets=agent.targets)

# closest_distance = float('inf')
# closest_robot = None

# for agent in agents:
#     print(agent.robot.x, agent.robot.y)
#     distance = agent.distance_target()
#     print(distance)
#     if(distance < closest_distance):
#         closest_distance = distance
#         closest_robot = agent

# if(closest_robot):
#     closest_robot.decision()
