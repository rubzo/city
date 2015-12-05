#!/usr/bin/env python

import time
import random

class Agent:
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

class R(Agent):
    def __init__(self):
        self.icon = "h"

class C(Agent):
    def __init__(self):
        self.icon = "c"

class I(Agent):
    def __init__(self):
        self.icon = "i"

class Road(Agent):
    def __init__(self):
        self.icon = "?"

        self.vertical = True
        self.junction = False

        self.grown = False
        self.filled_up = False

        self.chance_spawn_junction = 0.09
        self.chance_spawn_building = 0.001

    def getSelf(self):
        if self.junction:
            return "+"
        elif self.vertical:
            return "|"
        return "-"

    def check_and_grow(self, world, x, y, spawn_vertical = False):
        if world.world.get((x, y)) == None:
            new_road = Road()
            if not self.junction and random.random() < self.chance_spawn_junction:
                new_road.junction = True
            elif not self.junction:
                new_road.vertical = self.vertical
            else:
                new_road.vertical = spawn_vertical

            world.spawnAgent(new_road, x, y)

    def check_and_spawn_building(self, world, x, y):
        if world.world.get((x, y)) == None:
            building = random.choice([R(), C(), I()])
            world.spawnAgent(building, x, y)

    def update(self, world):
        if not self.grown:
            if self.junction:
                self.check_and_grow(world, self.x, self.y - 1, True)
                self.check_and_grow(world, self.x, self.y + 1, True)
                self.check_and_grow(world, self.x - 1, self.y, False)
                self.check_and_grow(world, self.x + 1, self.y, False)
            else:
                if self.vertical:
                    self.check_and_grow(world, self.x, self.y - 1)
                    self.check_and_grow(world, self.x, self.y + 1)
                else:
                    self.check_and_grow(world, self.x - 1, self.y)
                    self.check_and_grow(world, self.x + 1, self.y)

        if not self.filled_up:
            if self.vertical and world.world.get((self.x - 1, self.y)) != None and world.world.get((self.x + 1, self.y)) != None:
                self.filled_up = True
            if not self.vertical and world.world.get((self.x, self.y - 1)) != None and world.world.get((self.x, self.y + 1)) != None:
                self.filled_up = True

        if not self.junction and not self.filled_up:
            if random.random() < self.chance_spawn_building:
                if self.vertical:
                    if random.random() < 0.5:
                        self.check_and_spawn_building(world, self.x - 1, self.y)
                    else:
                        self.check_and_spawn_building(world, self.x + 1, self.y)
                else:
                    if random.random() < 0.5:
                        self.check_and_spawn_building(world, self.x, self.y - 1)
                    else:
                        self.check_and_spawn_building(world, self.x, self.y + 1)

        return ("alive", self.x, self.y)

class World:
    def __init__(self):
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
road = Road()
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

steps = 0
while True:
   steps += 1
   world.update()
   world.draw()
   print("Steps: {}".format(steps))
   time.sleep(1.0/30)

