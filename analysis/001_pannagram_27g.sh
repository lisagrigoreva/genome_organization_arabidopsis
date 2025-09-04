#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=20
#SBATCH --mem-per-cpu=10G
#SBATCH --time=50:00:00
#SBATCH --partition=m
#SBATCH --qos="long"
#SBATCH --output=/groups/nordborg/projects/genome_organization/08_manuscripts/logs/pannagram_%A_%a.out
#SBATCH --error=/groups/nordborg/projects/genome_organization/08_manuscripts/logs/pannagram_%A_%a.err

# Activate environment
#conda activate pannagram


# Run pannagram for 27 genomes 
pannagram -cores 10 -path_in /groups/nordborg/projects/genome_organization/08_manuscripts/01_data/27_genomes -path_out  /groups/nordborg/projects/genome_organization/08_manuscripts/03_results/01_pannagram_27_genomes/ -ref "TAIR10" -nchr 5 -nchr_ref 5
# Get msa,seq and snps
features -path_project /groups/nordborg/projects/genome_organization/08_manuscripts/01_data/27_genomes -ref 'TAIR10' -snp -cores 30
