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
### Setup scone file protection (fspf) to secure the input fastq and output sam files
We utilize the file protection feature provided by Scone to achieve the secured storage of the input and output for the BWA alignment. This document has more information on that:
https://sconedocs.github.io/SCONE_Fileshield/

Here we assumes we are working on a common directory, say `workdir`, on the shared file system accessible by all nodes in the cluster. Under this working directory we have `data-original` and `volume` to store the unprotected and protected content respectively (The `volume` will be mounted in a running docker process as `data`).

### Job script generatation and submission
The script bwa_scone_run.py generates the scripts to be submitted to the compute nodes for the BWA alignment work. E.g., run the following in the `workdir` directory on the master/submitting node:

```
python bwa_scone_run.py 4 bio-sgx0[6-8,10] . split80 0
```

This will generate 4 separate scripts, in which has the subset of the BWA tasks, and then submit them to the specified 4 nodes. The `split80` shows the directory where the input data can be found.

When changing the last parameter to 1 it runs in dryrun mode to print out the generated scritps location and the command to be sumitted to each compute node.
