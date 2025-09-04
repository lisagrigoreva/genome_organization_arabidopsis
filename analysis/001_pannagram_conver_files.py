## Read pannagram output files and convert them to the matrix 
import h5py, numpy as np, gzip

in_path = "/groups/nordborg/projects/genome_organization/08_manuscripts/03_results/01_pannagram_27_genomes/features/seq/seq_5_5_TAIR10.h5"
out_path = "/groups/nordborg/projects/genome_organization/08_manuscripts/03_results/01_pannagram_27_genomes/features/seq/converted_matricies/ref_5_5_matrix.tsv.gz"
chunk_rows = 500_000
compresslevel = 1

with h5py.File(in_path, "r") as f, gzip.open(out_path, "wt", compresslevel=compresslevel) as out:
    accs = sorted(f["accs"].keys())  # Go into the "accs" group in the H5 and list its dataset names (accession IDs).
    dsets = [f["accs"][a] for a in accs] # For each accession name, get the corresponding HDF5 dataset object
    L = dsets[0].shape[0] # Take number of positions (length)
    out.write("pos\t" + "\t".join(accs) + "\n") # Add header

    for start in range(0, L, chunk_rows): # Iterate over positions in chunks
        end = min(start + chunk_rows, L)
        block = np.stack([ds[start:end] for ds in dsets], axis=1).astype(str) # Slice rows
        pos = (np.arange(start, end) + 1).astype(str).reshape(-1, 1)  # 1-based
        out_block = np.concatenate([pos, block], axis=1)
        out.write("\n".join("\t".join(row) for row in out_block) + "\n")

print("Wrote:", out_path)

## Convert to vcf file (with non-variable sites)

import gzip
import sys

in_tsv = "/groups/nordborg/projects/genome_organization/08_manuscripts/03_results/01_pannagram_27_genomes/features/seq/converted_matricies/ref_5_5_matrix.tsv.gz"
out_vcf = "/groups/nordborg/projects/genome_organization/08_manuscripts/03_results/01_pannagram_27_genomes/features/seq/converted_matricies/seq_5_5.vcf.gz"
chrom = "Chr5" # Indicate chromosome 

VALID = {"A","C","G","T"}
MISSING = {"N","-"}
BASE_ORDER = {"A":0, "C":1, "G":2, "T":3}

def build_alts(ref, sample_bases):
    # unique valid non-REF bases, sorted A<C<G<T
    return sorted({b for b in sample_bases if b in VALID and b != ref},
                  key=lambda b: BASE_ORDER[b])

def gt_call(b, ref, alt_list):
    if b in MISSING or b not in VALID:
        return "./."
    if b == ref:
        return "0/0"
    if alt_list:
        try:
            k = alt_list.index(b) + 1  # 1-based ALT index
            return f"{k}/{k}"
        except ValueError:
            return "./."
    # no ALT alleles at this site and b != ref -> treat as missing
    return "./."

opener_in = gzip.open if in_tsv.endswith(".gz") else open
opener_out = gzip.open if out_vcf.endswith(".gz") else open

with opener_in(in_tsv, "rt") as fin, opener_out(out_vcf, "wt") as fout:
    header = fin.readline().rstrip("\n").split("\t")
    if header[0].lower() != "pos":
        sys.exit("First column must be 'pos'")
    if header[-1] != "TAIR10":
        sys.exit("Last column must be 'TAIR10'")
    samples = header[1:-1]

    # VCF header
    #fout.write("##fileformat=VCFv4.2\n")
    #fout.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
    #fout.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(samples) + "\n")

    for line in fin:
        parts = line.rstrip("\n").split("\t")
        pos = parts[0]
        row = parts[1:]
        ref_base = row[-1]
        sample_bases = row[:-1]

        # require valid REF
        if ref_base not in VALID:
            # keep non-ACGT reference sites out of VCF
            continue

        # ALT alleles present at this site
        alts = build_alts(ref_base, sample_bases)

        # ALT field: '.' if no alternate alleles
        alt_field = ",".join(alts) if alts else "."

        # Genotypes (keep non-variant sites)
        gts = [gt_call(b, ref_base, alts) for b in sample_bases]

        fout.write(f"{chrom}\t{pos}\t.\t{ref_base}\t{alt_field}\t.\tPASS\t.\tGT\t" + "\t".join(gts) + "\n")

print("Wrote", out_vcf)
