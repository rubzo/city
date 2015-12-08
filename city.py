#!/usr/bin/env python

import time
import random
import sys

class Agent(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.color = "black"

    def getColor(self):
        return self.color

    def update(self, world):
        return ("alive", self.x, self.y)

class Blocker(Agent):
    def __init__(self):
        self.color = "white"

class Residential(Agent):
    def __init__(self):
        self.color = "green"

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
        self.color = "red"

        self.chance_cleanup = 0.0005

    def update(self, world):
        if random.random() < self.chance_cleanup:
            return ("dead", 0, 0)
        return ("alive", self.x, self.y)

class Commercial(Agent):
    def __init__(self):
        self.color = "blue"

class Industrial(Agent):
    def __init__(self):
        self.color = "yellow"

class Road(Agent):
    def __init__(self):
        self.color = "gray"

class VerticalRoad(Road):
    def __init__(self):
        self.color = "#282B2A"
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
        self.color = "#282B2A"
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
        self.color = "#282B2A"
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

    def draw(self, canvas, scale):
        for y in range(self.y_min, self.y_max+1):
            for x in range(self.x_min, self.x_max+1):
                agent = self.world.get((x, y), None)
                color = 'black'
                outline = 'black'
                if agent:
                    color = agent.getColor()
                a_y = ((y - self.y_min) + 1) * scale
                a_x = ((x - self.x_min) + 1) * scale
                canvas.create_oval(a_x, a_y, a_x + scale, a_y + scale, outline = outline, fill = color)

world = World()

width = 40
#width = 120
height = 40
scale = 10

for i in xrange(0, width):
    world.seedAgent(Blocker(), i, 0)
    world.seedAgent(Blocker(), i, height)
for i in xrange(0, height):
    world.seedAgent(Blocker(), 0, i)
    world.seedAgent(Blocker(), width, i)

road = VerticalRoad()
world.seedAgent(road, width/2, height/2)

print("Performing initial simulation of 1000 steps...")
for i in xrange(0, 1000):
    world.update()

import Tkinter
root = Tkinter.Tk()

def kp(event):
    if event.keysym == 'Escape':
        root.destroy()
root.bind_all('<KeyPress>', kp)

canvas = Tkinter.Canvas(root, width = (width+3) * scale, height = (height+3) * scale, background = 'black')
canvas.pack()

updates = 200
steps = 0

def update():
    global world, canvas, root, scale, updates, steps

    start = time.time()
    for i in xrange(0, updates):
        world.update()
    end = time.time()
    steps += updates

    if (end - start) > 1:
        updates = updates / 2
    elif (end - start) < 0.8:
        updates = int(updates * 1.2)
    print("Took {:.2f}s to simulate. Adjusted to {} updates. Total steps: {}".format(end - start, updates, steps))
    world.draw(canvas, scale)
    canvas.update_idletasks()
    root.after(1000 - int((end - start) * 1000), update)

root.after(0, update)
root.attributes('-topmost', 1)
root.update()
root.attributes('-topmost', 0)
root.mainloop()
