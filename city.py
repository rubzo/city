#!/usr/bin/env python

import time
import random
import sys

class Agent(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.icon = "x"

    def getSelf(self):
        return self.icon

    def update(self, world):
        return ("alive", self.x, self.y)

class Blocker(Agent):
    def __init__(self):
        self.icon = "#"

class Residential(Agent):
    def __init__(self):
        self.icon = '\033[92m' + "R" + '\033[0m'

        self.chance_become_derelict = 0.001

    def check_for_industrial(self, world):
        return isinstance(world.world.get((self.x, self.y - 1)), Industrial) or \
            isinstance(world.world.get((self.x, self.y + 1)), Industrial) or \
            isinstance(world.world.get((self.x - 1, self.y)), Industrial) or \
            isinstance(world.world.get((self.x + 1, self.y)), Industrial)

    def update(self, world):
        if self.check_for_industrial(world) and random.random() < self.chance_become_derelict:
            derelict = Derelict()
            world.spawnAgent(derelict, self.x, self.y)
            return ("dead", 0, 0)
        return ("alive", self.x, self.y)

class Derelict(Agent):
    def __init__(self):
        self.icon = '\033[95m' + "x" + '\033[0m'

        self.chance_cleanup = 0.0005

    def update(self, world):
        if random.random() < self.chance_cleanup:
            return ("dead", 0, 0)
        return ("alive", self.x, self.y)

class Commercial(Agent):
    def __init__(self):
        self.icon = '\033[94m' + "C" + '\033[0m'

class Industrial(Agent):
    def __init__(self):
        self.icon = '\033[93m' + "I" + '\033[0m'

class Road(Agent):
    def __init__(self):
        pass

class VerticalRoad(Road):
    def __init__(self):
        self.icon = "|"
        self.chance_extend = 0.05
        self.chance_spawn_junction = 0.09
        self.chance_spawn_building = 0.001

    def update(self, world):
        if random.random() < self.chance_extend:
            if random.random() < self.chance_spawn_junction:
                world.checkEmptyAndSpawnThisType(CrossRoad, self.x, self.y - 1)
            else:
                world.checkEmptyAndSpawnSameType(self, self.x, self.y - 1)
        if random.random() < self.chance_extend:
            if random.random() < self.chance_spawn_junction:
                world.checkEmptyAndSpawnThisType(CrossRoad, self.x, self.y + 1)
            else:
                world.checkEmptyAndSpawnSameType(self, self.x, self.y + 1)
        if random.random() < self.chance_spawn_building:
            building_choice = random.choice([Residential, Commercial, Industrial])
            world.checkEmptyAndSpawnThisType(building_choice, self.x - 1, self.y)
        if random.random() < self.chance_spawn_building:
            building_choice = random.choice([Residential, Commercial, Industrial])
            world.checkEmptyAndSpawnThisType(building_choice, self.x - 1, self.y)

        return ("alive", self.x, self.y)

class HorizontalRoad(Road):
    def __init__(self):
        self.icon = "-"
        self.chance_extend = 0.05
        self.chance_spawn_junction = 0.09
        self.chance_spawn_building = 0.001

    def update(self, world):
        if random.random() < self.chance_extend:
            if random.random() < self.chance_spawn_junction:
                world.checkEmptyAndSpawnThisType(CrossRoad, self.x - 1, self.y)
            else:
                world.checkEmptyAndSpawnSameType(self, self.x - 1, self.y)
        if random.random() < self.chance_extend:
            if random.random() < self.chance_spawn_junction:
                world.checkEmptyAndSpawnThisType(CrossRoad, self.x + 1, self.y)
            else:
                world.checkEmptyAndSpawnSameType(self, self.x + 1, self.y)
        if random.random() < self.chance_spawn_building:
            building_choice = random.choice([Residential, Commercial, Industrial])
            world.checkEmptyAndSpawnThisType(building_choice, self.x, self.y - 1)
        if random.random() < self.chance_spawn_building:
            building_choice = random.choice([Residential, Commercial, Industrial])
            world.checkEmptyAndSpawnThisType(building_choice, self.x, self.y + 1)

        return ("alive", self.x, self.y)

class CrossRoad(Road):
    def __init__(self):
        self.icon = "+"
        self.chance_extend = 0.05
        self.chance_spawn_junction = 0.09
        self.chance_spawn_building = 0.001

    def update(self, world):
        if random.random() < self.chance_extend:
            world.checkEmptyAndSpawnThisType(HorizontalRoad, self.x - 1, self.y)
        if random.random() < self.chance_extend:
            world.checkEmptyAndSpawnThisType(HorizontalRoad, self.x + 1, self.y)
        if random.random() < self.chance_extend:
            world.checkEmptyAndSpawnThisType(VerticalRoad, self.x, self.y - 1)
        if random.random() < self.chance_extend:
            world.checkEmptyAndSpawnThisType(VerticalRoad, self.x, self.y + 1)


        return ("alive", self.x, self.y)


    #def check_and_spawn_building(self, world, x, y):
    #    if world.world.get((x, y)) == None:
    #        building = random.choice([Residential(), Commercial(), Industrial()])
    #        world.spawnAgent(building, x, y)


class World:
    def __init__(self):
        # TODO: Control access to world
        self.world = dict()
        self.next_world = dict()
        self.x_min = 0
        self.y_min = 0
        self.x_max = 0
        self.y_max = 0

    def update(self):
        self.next_world = dict()
        self.x_min = 0
        self.y_min = 0
        self.x_max = 0
        self.y_max = 0
        for agent in self.world.values():
            (state, x, y) = agent.update(self)
            if state == "alive":
                if x < self.x_min:
                    self.x_min = x
                elif x > self.x_max:
                    self.x_max = x
                if y < self.y_min:
                    self.y_min = y
                elif y > self.y_max:
                    self.y_max = y
                self.next_world[(x, y)] = agent
        self.world = self.next_world

    def checkEmptyAndSpawnSameType(self, agent, x, y):
        if self.world.get((x, y)) == None:
            new_agent = type(agent)()
            self.spawnAgent(new_agent, x, y)

    def checkEmptyAndSpawnThisType(self, agent_type, x, y):
        if self.world.get((x, y)) == None:
            new_agent = agent_type()
            self.spawnAgent(new_agent, x, y)

    def seedAgent(self, agent, x, y):
        agent.x = x
        agent.y = y
        self.world[(x, y)] = agent

    def spawnAgent(self, agent, x, y):
        agent.x = x
        agent.y = y
        self.next_world[(x, y)] = agent

    def draw(self):
        for y in range(self.y_min, self.y_max+1):
            line = " "
            for x in range(self.x_min, self.x_max+1):
                agent = self.world.get((x, y), None)
                if agent:
                    line += agent.getSelf()
                else:
                    line += " "
            print(line)
        print("Agent count: {}".format(len(self.world)))

world = World()
road = VerticalRoad()
world.seedAgent(road, 0, 0)
for i in xrange(-20, 21):
    blocker = Blocker()
    world.seedAgent(blocker, -20, i)
    blocker = Blocker()
    world.seedAgent(blocker, 20, i)
    blocker = Blocker()
    world.seedAgent(blocker, i, -20)
    blocker = Blocker()
    world.seedAgent(blocker, i, 20)

realtime = len(sys.argv) > 1 and sys.argv[1] == "realtime"

t = time.time()

steps = 0
while True:
    steps += 1

    world.update()

    if realtime:
        world.draw()
        print("Steps: {}".format(steps))
        time.sleep(1.0/20)
    else:
        if steps % 1000 == 0:
            world.draw()
            print("Steps: {}".format(steps))
            new_t = time.time()
            elapsed_time = new_t - t
            t = new_t
            print("Steps per second: {}".format(1000 / elapsed_time))
