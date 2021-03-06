"""
TV reconstruction example for simulated Skull CT data - 2D

Note: So far only works for phantom_number = '70100644'
"""

import odl
import numpy as np
import os
import adutils

# Discretization
reco_space = adutils.get_discretization(use_2D=True)

# Forward operator (in the form of a broadcast operator)
A = adutils.get_ray_trafo(reco_space, use_2D=True)

# Data
rhs = adutils.get_data(A, use_2D=True)

# Gradient operator
gradient = odl.Gradient(reco_space, method='forward')

# Column vector of operators
op = odl.BroadcastOperator(A, gradient)

Anorm = odl.power_method_opnorm(A, maxiter=2)
Dnorm = odl.power_method_opnorm(gradient,
                                xstart=odl.phantom.white_noise(gradient.domain),
                                maxiter=10)

# Estimated operator norm, add 10 percent
op_norm = 1.1 * np.sqrt(Anorm**2 + Dnorm**2)

print('Norm of the product space operator: {}'.format(op_norm))

lamb = 0.001  # l2NormGrad/l1NormGrad = 0.01

# l2-squared data matching
l2_norm = odl.solvers.L2NormSquared(A.range).translated(rhs)

# Isotropic TV-regularization i.e. the l1-norm
l1_norm = lamb * odl.solvers.L1Norm(gradient.range)

# Combine functionals
f = odl.solvers.SeparableSum(l2_norm, l1_norm)

# Set g functional to zero
g = odl.solvers.ZeroFunctional(op.domain)

# Accelerataion parameter
gamma = 0.5

# Step size for the proximal operator for the primal variable x
tau = 1.0 / op_norm

# Step size for the proximal operator for the dual variable y
sigma = 1.0 / op_norm  # 1.0 / (op_norm ** 2 * tau)

# Reconstruct
callbackShowReco = (odl.solvers.CallbackPrintIteration() &  # Print iterations
                    odl.solvers.CallbackShow(clim=[0.018, 0.022]))

callbackPrintIter = odl.solvers.CallbackPrintIteration()

# Use initial guess
x = adutils.get_initial_guess(reco_space)
x = A.domain.zero()

# Run such that last iteration is saved (saveReco = 1) or none (saveReco = 0)
saveReco = False
savePath = '/home/user/Simulated/120kV/'
niter = 400
odl.solvers.chambolle_pock_solver(x, f, g, op, tau=tau, sigma = sigma,
				  niter = niter, gamma=gamma, callback=callbackShowReco)
if saveReco:
    saveName = os.path.join(savePath,'reco/Reco_HelicalSkullCT_70100644Phantom_no_bed_Dose150mGy_TV_' +
                                          str(niter) + 'iterations.npy')
    adutils.save_image(x, saveName)
