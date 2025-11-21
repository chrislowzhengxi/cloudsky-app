#!/bin/bash -l

#SBATCH --job-name=puzzle_cracker
#SBATCH --output=outs/puzzle_output_%j.out
#SBATCH --error=outs/puzzle_error_%j.err

## ---- Partition/Account Options ----
#SBATCH --account=pi-imoskowitz
##SBATCH --partition=amd-hm
#SBATCH --partition=bigmem
##SBATCH --partition=amd

## ---- Memory Options ----
#SBATCH --mem=64G       # Plenty for this job

## ---- CPU Options ----
##SBATCH --cpus-per-task=120   # Good default; adjust if desired
#SBATCH --cpus-per-task=32

## ---- Time ----
#SBATCH --time=06:00:00      # Should be enough; adjust if needed

## ---- Notifications ----
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=chrislowzhengxi@uchicago.edu

# ---- Environment Setup ----
module load python/anaconda-2022.05
source activate /project/xyang2/software-packages/env/velocity_2025Feb_xy

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK

# ---- Cleanup: keep only the 5 most recent logs ----
# ls -t outs/puzzle_output_*.out | tail -n +6 | xargs -r rm -f
# ls -t outs/puzzle_error_*.err | tail -n +6 | xargs -r rm -f

# ---- Code Execution ----

cd /project/imoskowitz/xyang2/chrislowzhengxi/code/gastrulation_check/puzzle/

echo "Running puzzle solver on ${SLURM_CPUS_PER_TASK} cores..."


# python fast_solve_easy.py
python faster_puzzle.py
