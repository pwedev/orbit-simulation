import math
import numpy as np
import time


dt = 10**-4
dt2 = dt ** 2

G = 1.184 * 10 ** (-4)

list_planets = []

class planet:

    def __init__(self, mass_, vx_, vy_, x0_, y0_):

        self.mass = mass_
        self.pos = np.array([x0_, y0_])
        self.vel = np.array([vx_, vy_])
        self.pos_neu = 0

        list_planets.append(self)

    def getPos(self):
        return self.pos

    def getVel(self):
        return self.vel

    def getMass(self):
        return self.mass

    def setPos(self, pos_):
        self.pos_neu = pos_

    def setVel(self, vel_):
        self.vel = vel_

    def refresh(self):
        self.pos = self.pos_neu



def distance(p1, p2):

    if p1 is p2:
        return np.array([0, 0])

    dx = p1.getPos()[0] - p2.getPos()[0]
    dy = p1.getPos()[1] - p2.getPos()[1]

    return np.array([dx, dy])



def getForce(planet):

    ax, ay = 0, 0

    for p in list_planets:
        if planet is p:
            continue

        dx, dy = distance(planet, p)
        r = np.sqrt(dx**2 + dy**2)
        mass = p.getMass()

        if r != 0:
            ax += -dx * G * mass / np.abs(r ** 3)
            ay += -dy * G * mass / np.abs(r ** 3)

        #print(ax,ay)
    return np.array([ax, ay])



def calc_step(planet):

    pos = planet.getPos()
    vel = planet.getVel()
    force = getForce(planet)

    vxn = vel[0] + force[0] * dt
    xn = pos[0] + vxn * dt

    vyn = vel[1] + force[1] * dt
    yn = pos[1] + vyn * dt

    planet.setPos(np.array([xn, yn]))
    planet.setVel(np.array([vxn, vyn]))




# Testing precision of algorithm
def Ekin(planet):
    pos = planet.getPos()
    v = planet.getVel()
    return 0.5 * planet.getMass() * np.sqrt(v[0]**2 + v[1]**2) ** 2

def collision_check(p1, p2):
    pass




def main():

    t = float(0)
    tmax = float(1)

    f = open('paths_leapfrog.txt','w')

    sonne = planet(3.33*10**5, 0, 0, 0, 0)
    erde = planet(1, 1, 0, 0, 6.284) #6.284
    mond = planet(0.0123, 1.002695, 0, 0, 6.284 + 0.2212) #0.2212

    # Debug/Benchmark stuff
    print("Ekin0: ", Ekin(erde) + Ekin(sonne) + Ekin(mond))
    t0 = time.time()

    while t < tmax:

        for p in list_planets:
            pos = p.getPos()
            f.write(str(pos[0]) + " " + str(pos[1]) + " ")

        for p in list_planets:
            calc_step(p)
            p.refresh()

        f.write("\n")

        t += dt

    print("Ekin1: ", Ekin(erde) + Ekin(sonne) + Ekin(mond))


    t1 = time.time()
    print ((t1 - t0) * 10 ** 3, "ms für ", (tmax/dt), "Steps (", ((t1 - t0) * 10 ** 3)/(tmax/dt), " ms per step)")

    f.close()
    print("Fertig")



if __name__ == "__main__":
    main()
