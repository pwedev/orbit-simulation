import time

import mkp_verlet
import mkp_leapfrog
import mkp_leapfrog_numba

t0 = time.time()
mkp_verlet.main()
t1 = time.time()

print("Verlet methode: " + str(t1 - t0))

t0 = time.time()
mkp_leapfrog.main()
t1 = time.time()


# numba not efficient
# print("Leapfrog methode: " + str(t1 - t0))
#
# t0 = time.time()
# mkp_leapfrog_numba.main()
# t1 = time.time()
#
# print("Leapfrog methode (numba optimized): " + str(t1 - t0))
