# bwa-sgx-scone
A parallel privacy preserved BWA solution using Intel SGX and Scone

This document and the scripts describe running BWA with Intel SGX and Scone to achieve privacy preserved reads mapping.

## Prerequisite
 - A HPC cluster with SGX-enabled compute nodes.
 - A Shared file system among the cluster nodes.
 - Docker is installed on the compute nodes.
 
## Reads data used in the experiments

Reference genome:
```
$ wget https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz
$ gunzip hg38.fa.gz
```

Sequence reads:
1000genome site:
ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data

Obtain a sample single end reads:
```
$ wget ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data/HG00096/sequence_read/SRR062634.filt.fastq.gz
$ gunzip SRR062634.filt.fastq.gz
```

For paired end data:
```
$ wget ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data/HG00096/sequence_read/SRR062634_1.filt.fastq.gz
$ wget ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase3/data/HG00096/sequence_read/SRR062634_2.filt.fastq.gz

$ gunzip SRR062634_1.filt.fastq.gz
$ gunzip SRR062634_2.filt.fastq.gz
```

The original file was too large and it takes days to finish the alignment in SGX. So we splice it to get two 1M sequence data (still in pairs)
```
head -4000000 SRR062634_1.filt.fastq > SRR062634_1M_1.fastq
head -4000000 SRR062634_2.filt.fastq > SRR062634_1M_2.fastq
```

## Reference split and reads dispatch
Split the reference genome using the utility python script:
```
$ python splitRef.py 80
```
You can specify the number of chunks to be split. We experimented with various values and found 80 is an optimal value to use to run with SGX.

Generate reads input file for DIDA dispatch:
```
$ cat > inputReads.txt << EOF
SRR062634.filt.fastq
EOF
```

You will need the SRR062634.filt.fastq file in the same directory.

Generate the paired reads input for DIDA dispatch
```
$ cat > inputReadsPair.txt << EOF
SRR062634_1M_1.fastq
SRR062634_1M_2.fastq
EOF
```

## Alignment using BWA
