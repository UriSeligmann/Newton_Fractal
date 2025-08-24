# Newton Fractal Viewer

A high-performance GPU-accelerated Newton fractal generator with an interactive PyQt6 interface.

## Features

- **GPU Acceleration**: Uses CuPy for fast computation on NVIDIA GPUs
- **Interactive Zooming**: Click and drag to zoom into fractal regions
- **Custom Functions**: Enter any complex function (e.g., `z**3 - 1`, `exp(z) - sin(z)`)
- **High Resolution**: Adjustable resolution multiplier for detailed renders
- **Export**: Save fractals as PNG/JPEG images

## Screenshots

![Main Interface](Images/Screenshot%202025-08-24%20133844.png)
*Main application interface*

![Fractal Generation](Images/Screenshot%202025-08-24%20134222.png)
*Real-time fractal computation with progress tracking*

## Example Fractals

| Function | Result |
|----------|--------|
| $z^3 - 1$ | ![z^3-1](Images/fractal_zxx3-1_20250824_132820.jpg) |
| $0.1 \cdot e^z - \sin(z)$ | ![0.1*exp(z)-sin(z)](Images/fractal_0.1xexp(z)-sin(z)_20250824_133225.png) |
| $e^{\sin(z^3) + \cos(z^3)} + 3$ | ![complex function](Images/fractal_exp(sin(zxx3)+cos(zxx3))+3_20250824_131533.jpg) |
| $\tan(z^3) + \cos(z^3) + \sin(z^3)$ | ![trigonometric](Images/fractal_tan(zxx3)+cos(zxx3)+sin(zxx3)_20250824_134225.jpg) |

## Requirements

- Python 3.7+
- PyQt6
- CuPy (NVIDIA GPU with CUDA 13.0+ support)
- SymPy
- NumPy
- **Hardware**: Strong GPU recommended (tested on GeForce RTX 4060)

## Installation

```bash
pip install PyQt6 cupy sympy numpy
```

## Usage

```bash
python main.py
```

Enter a complex function in the input field and click "Compute" to generate the fractal. Use left-click and drag to zoom into interesting regions.

## Controls

- **Function Input**: Enter mathematical expressions using `z` as the complex variable
- **Compute**: Generate fractal for the current function
- **Resolution Multiplier**: Increase for higher quality (slower computation)
- **Reset Zoom**: Return to full fractal view
- **Save Image**: Export current fractal as image file
- **Exit**: Close application
