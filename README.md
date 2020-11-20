# NITRATE-ENRICH-SHORT-READ
The steps taken to analyze the short reads generated by JGI for the PIE LTER fertilization experiment.

### A Few words about things not detailed in this git
First we downloaded the data from JGI using GLOBUS which is the safest and best way to download the data. Then we began working on annotation of the short reads due to the poor assembly and binning acheived for these data. We are interested in generating the coverage information for specific genes related to biogeochemical cycling that are contained in the assebmly of each metagenomic dataset. This is a little tricky because, by collecting the functinoal genes from each of the individual assemblies, we will undoubtedly end up with many duplicate sequences, I think this is OK for now.  During the creation of this git, I am working on the data here
  
    /scratch/vineis.j/NITROGEN_ENRICH/GLOBUS-DOWNLOAD
  
however, after a time, I may move the data to a more permanent storage. here

    /work/jennifer.bowen/

### Generate a contigs database for each of the assemblies in the dataset using ANVIO. The steps below will also run all the marker gene searches for key functional genes within fungene and custom CO2 fixation genes.
The assemblies are usually found within the directory.. something like this

    /scratch/vineis.j/NITROGEN_ENRICH/GLOBUS-DOWNLOAD/s_10CB15_MG/QC_and_Genome_Assembly/assembly.contigs.fasta

So to generate an anvio assembly, I use a slurm script that looks like the one below.  The paths will be something that you will need to pay attention to. 

    #!/bin/bash
    #
    #SBATCH --nodes=1
    #SBATCH --tasks-per-node=10
    #SBATCH --mem=100Gb
    #SBATCH --time=07:00:00
    #SBATCH --partition=short
    #SBATCH --array=1-62

    SAMPLE=$(sed -n "$SLURM_ARRAY_TASK_ID"p sample_names.txt)
    anvi-gen-contigs-database -f s_${SAMPLE}/QC_and_Genome_Assembly/assembly.contigs.fasta -o x_ANVIO-assembly-dbs/s_${SAMPLE}.db
    anvi-run-hmms -c x_ANVIO-assembly-dbs/s_${SAMPLE}.db -T 30
    anvi-run-hmms -c x_ANVIO-assembly-dbs/s_${SAMPLE}.db -H ~/scripts/databas/HMM_co2fix/ -T 30
    anvi-run-hmms -c x_ANVIO-assembly-dbs/s_${SAMPLE}.db -H ~/scripts/databas/all_fungene_anvio/ -T 30

### To export a fasta file of each of the functional genes, you can use the steps below. You will need to have a "x_gene-names.txt" file that contains all of the genes that you want to export from the anvio database. There is an example of that file contained in this repository. You will also need an "x-external-genomes.txt" file that is also contained in this repository. You have made a ton of these files in the past and this should be a piece of cake if you are an experienced Anvio user.  If you are not, you should learn more about Anvio from their amazing tutorials. Here is the script to export the genes.

    #!/bin/bash
    #
    #SBATCH --nodes=1
    #SBATCH --tasks-per-node=10
    #SBATCH --mem=100Gb
    #SBATCH --time=07:00:00
    #SBATCH --partition=short
    #SBATCH --array=1-92

    SAMPLE=$(sed -n "$SLURM_ARRAY_TASK_ID"p x_gene-names.txt)
    anvi-get-sequences-for-hmm-hits -e x-external-genomes.txt --get-aa-sequences -o x_${SAMPLE}-sequences.faa --gene-names ${SAMPLE}
    
anvio will leave a space in the export name and this needs to be fixed.. I use the following to fix it.

    for i in *.faa; do sed -i 's/ bin/_bin/g' $i; done
    
### Now for the mapping of each sample to each assembly. This is a monster task and you cannot achieve this on a laptop (at least I don't think so). You will need bbmap for this task and you will need to run it separately for each of the samples so that you don't steal all the resources. This is how I run it for one of the samples.  

    #!/bin/bash
    #
    #SBATCH --nodes=1
    #SBATCH --tasks-per-node=10
    #SBATCH --mem=200Gb
    #SBATCH --time=24:00:00
    #SBATCH --partition=short
    #SBATCH --array=1-62

    SAMPLE=$(sed -n "$SLURM_ARRAY_TASK_ID"p sample_names.txt)

    var=*
    echo "$var"
    var="$(echo *)"

    ref_file=s_10CB15_MT/QC_and_Genome_Assembly/assembly.contigs.fasta
    fastq_file=$( echo "s_${SAMPLE}/Filtered_Raw_Data/"*"fastq.gz")
    output_file=MAPPING/s_10CB15_MT-vs-${SAMPLE}.bam
    covstats_file=MAPPING/s_10CB15_MT-vs-${SAMPLE}-covstats.txt

    bbmap.sh threads=4 nodisk=true interleaved=true ambiguous=random in=${fastq_file} ref=${ref_file} out=${output_file} covstats=${covstats_file} bamscript=to_bam.sh
    
### Then you can use the resulting "covstats.txt" file to look at the coverage of each gene derived from a single sample across all samples. Friggen awesome! Right!?!?! Here is how you would run that analysis.
1. first you need to run a script that will generate the sbatch scripts that will collect the coverage of a given gene. You will need a file called "x_metagenomic-sample-names.txt" which will contains the list of metagenomic samples (there are transcriptome samples as well, and I don't want to use those assemblies for this part of the project) and in this case, each one has a "s_" prior to the sample name. This is the script that will create a sbatch script for each sample.
    
        for i in `cat x_metagenomic-sample-names.txt`; do python ~/scripts/create-tabulate-gene-coverage-script.py ${i}; done
       
2.  Now that you have a bunch of bash scripts in the directory, its time to run them. Its important to load them in batches if you have more than 25 samples so that you don't overload the system. You can simply use a couple of lists that contain subsets of your samples.  Get the first batch going, wait a bit, and then load the second batch.
  
        for i in `cat x_samples-1.txt`; do sbatch ${i}_tabulate-genecoverage.shx; done
       
### These bash scripts will generate a coverage file for each of the pairwise mapping covstats.txt files in your "MAPPING" directory. For example, there will be a ton of files named something like this s_5SB15_MG-vs-8NB15_MT-nirS.txt looking something like this.

    scaffold	MAPPING/s_5SB15_MG-vs-8CB15_MG-covstats.txt
    s_5SB15_MG_scaffold_3482_c1	12.3445
    s_5SB15_MG_scaffold_8419_c1	2.7756
    s_5SB15_MG_scaffold_10151_c1	7.5100
    s_5SB15_MG_scaffold_10327_c1	14.3237
    s_5SB15_MG_scaffold_11293_c1	14.6181
    s_5SB15_MG_scaffold_12271_c1	2.4394

This of course is the coverage of each nirS scaffold found in sample s_5SB15_MG by the short reads derived from s_8CB15_MG.  There are a ton of these and we need to put them all together.

### Lets put together all of the coverage information for a single gene of interest using another great little scripty and run it like this

    #!/bin/bash
    #
    #SBATCH --nodes=1
    #SBATCH --tasks-per-node=1
    #SBATCH --mem=100Gb
    #SBATCH --time=00:20:00
    #SBATCH --partition=express

    for i in `cat x_sample-names.txt`; do python ~/scripts/combine-coverage-from-hmms-and-covstats.py --gene nirS --path /scratch/vineis.j/NITROGEN_ENRICH/GLOBUS-DOWNLOAD/ --out ${i}-nirS.txt --sample ${i}-; done
    
This will create a file that contains each of the nirS sequences found within all scaffolds and the coverage of each of the scaffolds within each individual sample.




    
     
     
  

  
  
  
