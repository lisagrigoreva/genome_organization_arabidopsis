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
# Run pannagram for thaliana and 31 A. lyrata genomes 
pannagram -cores 10 -path_in /groups/nordborg/projects/genome_organization/08_manuscripts/03_results/001_pannagram_31_lyr_thal/ -path_out /groups/nordborg/projects/genome_organization/08_manuscripts/03_results/001_pannagram_31_lyr_thal/out -ref "TAIR10" -nchr 8 -nchr_ref 5
# Run chromtools to arrangre crhomosomes together 
chromotools -path_project /groups/nordborg/projects/genome_organization/08_manuscripts/03_results/001_pannagram_31_lyr_thal/out  -genomes_out /groups/nordborg/projects/genome_organization/08_manuscripts/03_results/001_pannagram_31_lyr_thal/out/rearragned_genomes -rearrange -cores 30
# Run pannagram again (to get synteny plots for 31 lyrata genomes and msa aglignment)
pannagram -cores 10 -path_in /groups/nordborg/projects/genome_organization/08_manuscripts/03_results/001_pannagram_31_lyr_thal/out/rearragned_genomes -path_out /groups/nordborg/projects/genome_organization/08_manuscripts/03_results/001_pannagram_31_lyr_thal/out/rearragned_genomes/out -ref "TAIR10" -nchr 5 -nchr_ref 5 -one2one
# Extract features from the re-arranged genome
features -path_project /groups/nordborg/projects/genome_organization/08_manuscripts/01_data/27_genomes -ref 'TAIR10' -snp -seq -cores 30


