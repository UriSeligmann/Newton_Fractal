# fractal_engine.py
import sympy as sp
import cupy as cp
import numpy as np

class NewtonFractalEngine:
    def __init__(self, func_str, width=1000, height=1000, max_iter=50, tol=1e-6):
        self.func_str = func_str
        self.width = width
        self.height = height
        self.max_iter = max_iter
        self.tol = tol
        self.xlim = (-2, 2)
        self.ylim = (-2, 2)

        # --- SymPy parsing ---
        z = sp.symbols('z')
        self.f_sym = sp.sympify(func_str)
        self.df_sym = sp.diff(self.f_sym, z)
        self.f_num = sp.lambdify(z, self.f_sym, 'cupy')
        self.df_num = sp.lambdify(z, self.df_sym, 'cupy')

    def compute(self, tile_size=1000, progress_callback=None):
        """
        Compute Newton iteration on GPU using tiling.
        """
        H, W = self.height, self.width
        full_image = cp.zeros((H, W, 3), dtype=cp.float32)

        if progress_callback:
            progress_callback(5)

        total_tiles = (H // tile_size + (H % tile_size > 0)) * \
                      (W // tile_size + (W % tile_size > 0))
        tiles_computed = 0

        y_coords = cp.linspace(self.ylim[0], self.ylim[1], H, dtype=cp.float32)
        x_coords = cp.linspace(self.xlim[0], self.xlim[1], W, dtype=cp.float32)

        for y_start in range(0, H, tile_size):
            for x_start in range(0, W, tile_size):
                y_end = min(y_start + tile_size, H)
                x_end = min(x_start + tile_size, W)

                tile_H = y_end - y_start
                tile_W = x_end - x_start
                
                # Create a grid for the current tile
                tile_x = x_coords[x_start:x_end][None, :]
                tile_y = y_coords[y_start:y_end][:, None]
                Z_tile = tile_x + 1j * tile_y

                iter_counts = cp.zeros_like(Z_tile.real, dtype=cp.float32)
                mask = cp.ones_like(Z_tile.real, dtype=bool)

                for i in range(self.max_iter):
                    Z_prev = Z_tile.copy()
                    
                    active_Z = Z_tile[mask]
                    if active_Z.size == 0:
                        break # All pixels converged
                    
                    F = self.f_num(active_Z)
                    dF = self.df_num(active_Z)

                    # Guard against division by zero
                    dF = cp.where(dF == 0, 1e-20 + 0j, dF)
                    
                    Z_tile[mask] = active_Z - F / dF
                    
                    moved = cp.abs(Z_tile - Z_prev) > self.tol
                    iter_counts += moved.astype(cp.float32)
                    mask = mask & moved
                
                # Normalize iteration counts for the tile
                iter_norm_tile = iter_counts / self.max_iter
                full_image[y_start:y_end, x_start:x_end, :] = cp.stack([iter_norm_tile, iter_norm_tile, iter_norm_tile], axis=2)
                
                tiles_computed += 1
                if progress_callback:
                    progress = 10 + int(90 * tiles_computed / total_tiles)
                    progress_callback(progress)

        if progress_callback:
            progress_callback(100)

        return cp.asnumpy(full_image)