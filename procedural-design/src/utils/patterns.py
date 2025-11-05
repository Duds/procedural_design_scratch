# patterns.py

def gray_scott_pattern(nx, ny, steps, Du, Dv, F, k, rng_seed=0, n_seeds=6):
    """
    Generate a Gray-Scott reaction-diffusion pattern on a 2D grid.
    
    Parameters:
        nx (int): Number of grid points in the x-direction.
        ny (int): Number of grid points in the y-direction.
        steps (int): Number of iterations to run the simulation.
        Du (float): Diffusion rate of U.
        Dv (float): Diffusion rate of V.
        F (float): Feed rate.
        k (float): Kill rate.
        rng_seed (int): Seed for random number generation.
        n_seeds (int): Number of random seed patches to initialize.

    Returns:
        U (ndarray): Concentration of U after simulation.
        V (ndarray): Concentration of V after simulation.
    """
    import numpy as np

    rng = np.random.default_rng(rng_seed)
    U = np.ones((ny, nx), dtype=np.float32)
    V = np.zeros((ny, nx), dtype=np.float32)

    # Random square seed patches
    for _ in range(n_seeds):
        sx = rng.integers(low=nx//4, high=3*nx//4)
        sy = rng.integers(low=ny//4, high=3*ny//4)
        r = max(2, min(nx, ny)//20)
        U[sy-r:sy+r, sx-r:sx+r] = 0.50
        V[sy-r:sy+r, sx-r:sx+r] = 0.25

    # 5-point Laplacian with periodic boundary conditions
    def laplacian(A):
        Ay_up = np.vstack([A[0:1, :], A[:-1, :]])
        Ay_down = np.vstack([A[1:, :], A[-1:, :]])
        Ax_left = np.hstack([A[:, -1:], A[:, :-1]])
        Ax_right = np.hstack([A[:, 1:], A[:, :1]])
        return Ax_left + Ax_right + Ay_up + Ay_down - 4.0 * A

    dt = 1.0
    for _ in range(steps):
        Lu = laplacian(U)
        Lv = laplacian(V)
        UVV = U * V * V
        U += (Du * Lu - UVV + F * (1.0 - U)) * dt
        V += (Dv * Lv + UVV - (F + k) * V) * dt
        np.clip(U, 0.0, 1.0, out=U)
        np.clip(V, 0.0, 1.0, out=V)

    return U, V