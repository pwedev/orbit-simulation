import math
import numpy as np
import time



dt = 0.0001
dt2 = dt ** 2

list_planets = []

G = 1.184 * 10 ** (-4)

class planet:


    def __init__(self, mass_, x0_, y0_, vx_, vy_):

        self.mass = mass_
        self.pos = np.array([x0_, y0_, x0_ + vx_*dt, y0_ + vy_*dt]) #evtl + a?
        self.pos_neu = 0

        list_planets.append(self)

    def getPos(self):
        return self.pos

    def getMass(self):
        return self.mass

    def newPos(self, pos_):
        self.pos_neu = pos_

    def refresh(self):
        self.pos = self.pos_neu



def distance(p1, p2):

    if p1 is p2:
        return np.array([0, 0])

    dx = p1.getPos()[2] - p2.getPos()[2]
    dy = p1.getPos()[3] - p2.getPos()[3]

    return np.array([dx, dy])



def getForce(planet):

    ax, ay = 0, 0

    for p in list_planets:
        if planet is p:
            continue

        dx, dy = distance(planet, p)
        r = np.sqrt(dx**2 + dy**2)

        if dx != 0:
            ax += -dx * G * p.getMass() / np.abs(r ** 3)
        if dy != 0:
            ay += -dy * G * p.getMass() / np.abs(r ** 3)

        #print(ax,ay)
    return np.array([ax, ay])



def calc_step(planet):

    pos = planet.getPos()
    force = getForce(planet)

    xn = 2 * pos[2] - pos[0] + force[0] * dt2
    yn = 2 * pos[3] - pos[1] + force[1] * dt2

    planet.newPos(np.array([pos[2], pos[3], xn, yn]))


# Test
def Ekin(planet):
    pos = planet.getPos()
    v = ((pos[2] - pos[0]) + (pos[3] - pos[1]))/dt
    return 0.5 * planet.getMass() * v**2



t = float(0.)
tmax = float(1)

f = open('dreikörper.txt','w')

sonne = planet(3.33*10**5, 0, 0, 0, 0)
erde = planet(1, 1, 0, 0, 6.284)
mond = planet(0.0123, 1.002695, 0, 0, 6.284 + 0.2212)


#print("Ekin0: ", Ekin(erde), Ekin(sonne), Ekin(erde) + Ekin(sonne))

t0 = time.time()

while t < tmax:

    for p in list_planets:
        calc_step(p)
        pos = p.getPos()
        f.write(str(pos[2]) + " " + str(pos[3]) + " ")

    for p in list_planets:
        p.refresh()

    f.write("\n")

    t += dt

#print("Ekin0: ", Ekin(erde), Ekin(sonne), Ekin(erde) + Ekin(sonne))

t1 = time.time()
print ((t1 - t0) * 10 ** 3, "ms für ", (tmax/dt), "Steps (", ((t1 - t0) * 10 ** 3)/(tmax/dt), " ms per step)")

f.close()
print("Fertig")
