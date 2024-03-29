"""
Here we solve the following system of equations:
    - d[h]/dt + d[q]/dx = 0
    - d[q]/dt + d[q**2/h + (g/2)*h**2]/dx = -g*h*(d[Z]/dx)

variables:
    - U  = [h, q]:
    - W = [h, q, Z]: 
    - U_int, W_int: left/right values of U, W


dim(W) = (3, Nx)

dim(W_int) = (3, 2, Nx):
    - 2: [h, q, Z]
    - 2: [pos, min]

REFERENCE: Diaz, M. J. C., Kurganov, A., & de Luna, T. M. (2019). Path-conservative central-upwind schemes for nonconservative hyperbolic systems. ESAIM: Mathematical Modelling and Numerical Analysis, 53(3), 959-985.

"""

import numpy as np

from hyperbopy.core.spatial_scheme import reconstruct_u

from .basemodel import BaseModel


class SW1LGlobal(BaseModel):

    name = 'SW1LGlobal'

    def __init__(self, g=None, r=None, theta=None, epsilon=None, dt_fact=None):
        self.g = g if g is not None else self.GRAVITATIONAL_CONSTANT
        self.r = r if r is not None else self.DENSITY_RATIO
        self.theta = theta if theta is not None else self.THETA
        self.epsilon = epsilon if epsilon is not None else self.EPSILON
        self.dt_fact = dt_fact if dt_fact is not None else self.DT_FACT
        #
        self.gprime = self.g*(1 - self.r)
        self.var_names = ['h', 'q', 'Z']

    # #### spatial discretization functions

    def compute_F(self, W_int):
        return np.swapaxes(
            np.array([W_int[1, ...],
                      W_int[1, ...]**2/W_int[0, ...] +
                          (self.gprime/2)*W_int[0, ...]**2,
                      ]),
            0, 1)

    def compute_S(self, W, W_int):
        l1 = -self.gprime*W[0, 1:-1]*(W_int[-1, 1, 1:] - W_int[-1, 0, :-1])
        return np.array([np.zeros_like(l1), l1])

    def compute_B(self, W, W_int):
        return np.zeros_like(W[:-1, 1:-1])

    def compute_Spsi_int(self, W, W_int):
        l1 = -(self.gprime/2)*(W_int[0, 0, :] + W_int[0, 1, :]) * \
            (W_int[-1, 0, :] - W_int[-1, 1, :])
        return np.array([np.zeros_like(l1), l1])

    def compute_Bpsi_int(self, W, W_int):
        return np.zeros_like(W_int[:-1, 0, :])

    def compute_Ainv_int(self, W, W_int):
        zero = np.zeros_like(W_int[0, 0, :])
        one = np.ones_like(W_int[0, 0, :])
        #
        l1 = np.array([zero, 2/(self.gprime*W_int[0, 0, :] + W_int[0, 1, :])])
        l2 = np.array([one, zero])
        return np.array([l1, l2])

    def compute_local_speeds(self, W_int, dx):
        # reconstruct u
        u_int = reconstruct_u(W_int[0], W_int[1], self.epsilon)
        # ensure consistency among variables
        W_int[1, ...] = u_int*W_int[0, ...]
        #
        ap_int = np.row_stack((u_int + np.sqrt(self.gprime*W_int[0, ...]),
                               np.zeros_like(u_int[0, :]))).max(axis=0)
        am_int = np.row_stack((u_int - np.sqrt(self.gprime*W_int[0, ...]),
                               np.zeros_like(u_int[0, :]))).min(axis=0)
        return np.array([ap_int, am_int]), dx/(2*np.amax([ap_int, -am_int]))
