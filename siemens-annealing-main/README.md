[![DOI](https://zenodo.org/badge/497859526.svg)](https://zenodo.org/badge/latestdoi/497859526)

# Quantum Computing Programming: Train Routing Problem Using Quantum Annealing

## Dependency installation

Make sure you have the conda installed and activated.
To install dependencies:

```
pip install -r requirements.txt
```

## Demo

To run a demo with linear programming and QUBO, move to folder

```
cd src/railway_solvers
```
### Linear programming
Run a simple dataset with linear programming:

```
python lp_representation.py
```

### QUBO
Run QUBO:

```
python qubo.py
```


## Getting a solution:

## Visualization
Get the heatmap of qubo

```
cd src/qubo_visualization
```

Run visualization.py

```
python visualization.py
```

The output image will be stored in qubo_visualization/figures.

## Plotting
Generating all schedule and rail network plots:
```
python generate_all_plots.py
```
The output images will be stored in plots.

## Data Set Generation
```
cd src/helpers
```
Generate randomized problem instances with methods in:
```
generate_json.py
```
Add additional (randomized) delays with:
```
add_delays.py
```

## Example 
```
python main.py
```