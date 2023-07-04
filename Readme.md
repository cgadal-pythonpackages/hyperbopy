# shallowpy

The `shallowpy` module allows solving 1D non-conservative hyperbolic systems of equations of the form:

```math

\boldsymbol{U}_{t} + \boldsymbol{F}(\boldsymbol{U}, Z)_{x}  = B(\boldsymbol{U},Z)\boldsymbol{U}_{x} + \boldsymbol{S}(\boldsymbol{U})Z_{x},

```

where:
 - $\boldsymbol{U} \in \mathbb{R}^{N}$ is a vector of unkown quantities
 - $\boldsymbol{F}: \in \mathbb{R}^{N} \to \mathbb{R}^{N}$ is a non-linear flux
 - $B(\boldsymbol{U},Z) \in \mathbb{R}^{N \times N}$ is a non-conservative term
 - $\boldsymbol{S}(\boldsymbol{U}) \in \mathbb{R}^{N \times N}$ is a source term.

The numerical schemes are:
- spatial: well-balanced path-conservative central-upwind scheme for the spatial discretization (unless specified otherwise) [[1]](#1)
- temporal: stage-3 order-3 explicit strong stability preserving Runge-Kutta [eSSPRK 3-3] in time [[2]](#2)

## Usage

Here, we show how to solve the one-layer shallow water equations already implemented in `shallowpy`. More examples are available in the `reference_cases` directory.

```python
import numpy as np

from shallowpy import run_model
from shallowpy.models import SW_1L_global

# ## Domain size
L = 10   # domain length [m]

# ## Grid parameters
tmax = 2.5  # s  max time
Nx = 1000  # spatial grid points number (evenly spaced)
x = np.linspace(0, L, Nx)
dx = L/(Nx - 1)

# ## Initial condition
# Bottom topography
Z = 0*x
# fluid height
hmin = 1e-10
l0 = 5
h0 = 0.5
h = hmin*np.ones_like(x) + np.where(x <= l0, h0, 0) 
# fluid velocity
q = np.zeros_like(x)

W0 = np.array([h, q, Z])

# ## model instance initialization
model = SW_1L_global()  # with default parameters

# ## Run model
U, t = run_model(model, W0, tmax, dx, 
                 plot_fig=True, dN_fig=50, x=x, Z=Z)

```

## Implemented models

- $h$: layer height
- $u$: layer velocity
- $q = hu$: layer discharge
- $Z$: bottom topography
- $r = \rho_1/\rho_2$: layer density ratio ($r <=1$)

with subscripts $1$ and $2$ denoting the upper light and lower heavy layers, respectively.

### One-layer models

- #### One-layer shallow water (globally conservative)

  - `model = '1L_global'`

```math
\begin{aligned}

\left[h\right]_{t} + [q]_{x} &= 0, \\
[q]_{t} + \left[\frac{q^{2}}{h} + \frac{g(1-r)}{2}h^{2}\right]_{x} &= -g(1-r) h[Z]_{x}, \\

\end{aligned}

```

- #### One-layer shallow water (locally conservative)

  - `model = '1L_local'`

```math
\begin{aligned}

\left[h\right]_{t} + [hu]_{x} &= 0, \\
[u]_{t} + \left[\frac{u^{2}}{2} + g(1-r)(h + Z) \right]_{x} &= 0, \\

\end{aligned}

```

- #### One-layer non-hydrostatic shallow water (globally conservative)

  - `model = '1L_non_hydro_global'`

```math
\begin{aligned}

\left[h\right]_{t} + [q]_{x} &= 0, \\
[q]_{t} + \alpha_{\rm M} [M]_{t} + \left[\frac{q^{2}}{h} + \frac{g(1-r)}{2}h^{2}\right]_{x} &= -g(1-r) h[Z]_{x} - \alpha_{\rm N} N + p^{a} [h + Z]_{x}, \\

\end{aligned}

```

  where:

```math
\begin{aligned}

M &= \left[-\frac{1}{3}h^{3}[u]_{x} + \frac{1}{2}h^{2}u[Z]_{x}\right]_{x} + [Z]_{x}\left(-\frac{1}{2}h^{2}[u]_{x} + h u [Z]_{x}\right), \\

N &= \left[ [h^{2}]_{t}\left( h [u]_{x} - [Z]_{x} u \right)   \right]_{x} + 2[Z]_{x}[h]_{t}\left( h [u]_{x} - [Z]_{x} u\right) - [Z]_{x, t} \left(-\frac{1}{2}h^{2}[u]_{x} + h u [Z]_{x}\right), \\

\end{aligned}

```
  are the non-hydrostatic terms, and $p^{a}$ is an external constant pressure applied on the surface.


  > **Note**
  > The spatial discretization scheme is here a well-balanced central upwind scheme. For additional details, please refer to [[3]](#3).

### Two-layer models

- #### Two-layer shallow water (layerwise conservative)

  - `model = '2L_layerwise'`

```math
\begin{aligned}

\left[h_{1}\right]_{t} + [q_{1}]_{x} &= 0, \\
[h_{2}]_{t} + [q_{2}]_{x} &= 0, \\
[q_{1}]_{t} + \left[\frac{q_{1}^{2}}{h_{1}} + \frac{g}{2}h_{1}^{2}\right]_{x} &= -g h_{1}[h_{2} + Z]_{x}, \\
[q_{2}]_{t} + \left[\frac{q_{2}^{2}}{h_{2}} + \frac{g}{2}h_{2}^{2}\right]_{x} &= -g h_{2}[r h_{1} + Z]_{x},

\end{aligned}

```

- #### Two-layer shallow water (locally conservative)

  - `model = '2L_layerwise'`

```math
\begin{aligned}

\left[h_{1}\right]_{t} + [h_{1}u_{1}]_{x} &= 0, \\
[h_{2}]_{t} + [h_{2}u_{2}]_{x} &= 0, \\
[u_{1}]_{t} + \left[\frac{u_{1}^{2}}{2} + g(h_{1} + h_{2} + Z)\right]_{x} &= 0, \\
[u_{2}]_{t} + \left[\frac{u_{2}^{2}}{2} + g(rh_{1} + h_{2} + Z)\right]_{x} &= 0, \\

\end{aligned}

```

## Custom models

Using custom models is not yet possible, due to the way boundary conditions are implemented. This will be fixed soon.

## Installation

- Clone or download this repository
- `cd shallowpy`
- `pip3 install -e ./` (editable mode installation)


## References

- <a id="1">[1]</a> Diaz, M. J. C., Kurganov, A., & de Luna, T. M. (2019). Path-conservative central-upwind schemes for nonconservative hyperbolic systems. ESAIM: Mathematical Modelling and Numerical Analysis, 53[3], 959-985.

- <a id="2">[2]</a> Isherwood, L., Grant, Z. J., & Gottlieb, S. (2018). Strong stability preserving integrating factor Runge--Kutta methods. SIAM Journal on Numerical Analysis, 56[6], 3276-3307.

- <a id="3">[3]</a> Chertock, A., & Kurganov, A. (2020). Central-upwind scheme for a non-hydrostatic Saint-Venant system. Hyperbolic Problems: Theory, Numerics, Applications, 10.

## Changelog

- **04/07/02023**: version: 0.1.0
  - Reworking all code, separating model definition, spatial scheme and temporal scheme. 

- **20/06/02023**:
  - adding non-hydro globally conservative on-layer model

- **13/06/2023**: version: 0.0.1
  - changing repo organization to be able to select within system of equations
  - adding the locally conservative two-layer model [dam break shows shock solution]
  - adding the globally conservative one-layer model [dam break shows Ritter solution]
  - adding the locally conservative one-layer model [dam break shows shock solution]

- **09/06/2023**: First stable version (two layer globally) with validated reference examples. So far, no shock for dam-break solution, which exhibits the Ritter solution.
  
- **07/06/2023**: First commit