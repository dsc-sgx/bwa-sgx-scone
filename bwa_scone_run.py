import sys
import os
import pathlib
import hostlist

def gen_bwamem_workers(nworker, hostdir, containerdir="/workdir", rundir="."):
    scripts = []
    script_env = '''#!/bin/bash
export SCONE_FSPF_KEY=$(cat ./data-original/keytag | awk '{print $11}')
export SCONE_FSPF_TAG=$(cat ./data-original/keytag | awk '{print $9}')
    '''
    for workeridx in range(nworker):
        script_template = f'''
time for i in $(seq {workeridx+1} {nworker} 80); do docker run -v {hostdir}/volume:/data -v {hostdir}/data-original:/data-original -v {hostdir}:{containerdir} --env SCONE_VERSION=1 --env SCONE_MODE=HW --env SCONE_HEAP=4G --env SCONE_FSPF_KEY=$SCONE_FSPF_KEY --env SCONE_FSPF_TAG=$SCONE_FSPF_TAG --env SCONE_FSPF=/data/fspf.pb --device=/dev/isgx --entrypoint /root/bwa/bwa kevinwangfg/scone_bwa:v1.3 mem -o /data/P{nworker}_aln-$i.sam /data/{rundir}/mref-$i.fa /data/{rundir}/mreads-$i.fastq; done
'''
    #scripts = [script_template.format(workeridx=workeridx+1,nworker=nworker,hostdir=hostdir,containerdir=containerdir,rundir=rundir) for workeridx in range(nworker)]
    #
        script = script_env + script_template.format(workeridx=workeridx,nworker=nworker,hostdir=hostdir,containerdir=containerdir,rundir=rundir)
        scripts.append(script)
    return scripts

def submit_bwamem_jobs(hosts, scripts, workdir=".", runname=".", dryrun=False):
    os.system("chmod go+w {workdir}/{runname}".format(workdir=workdir, runname=runname))
    for i in range(len(hosts)):
        job = "script_{runname}_{idx}.sh".format(runname=runname,idx=i+1)
        fname = "{workdir}/{runname}/{job}".format(workdir=workdir,runname=runname,job=job)
        with open(fname, "w") as f_script:
            f_script.write(scripts[i])
        os.system("chmod a+x {fname}".format(fname=fname))
        remoterun = """nohup stdbuf -oL ssh {host} {workdir}/{runname}/{job} > {workdir}/{runname}/{host}_{idx}.out &""".format(host=hosts[i],
                                                                                                            workdir=workdir,
                                                                                                            runname=runname,
                                                                                                            job=job,
                                                                                                            idx=i+1)
        if dryrun:
            print (remoterun)
        else:
            os.system(remoterun)
            print ("submitted {job} to {host}!".format(job=job,host=hosts[i]))

if __name__ == '__main__':
    #hosts = ["bio-sgx0{idx}".format(idx=idx+1) for idx in range(8)]
    #workdir = "/tmp/testbwa"
    #runname = "exp_run1"
    #hosts = hostlist.expand_host("bio-sgx0[1-4,6,8]")
    #workdir = "/nfs/bio-sgx/home/fuwang/wfcommon"
    if len(sys.argv) < 5:
        print ("Usage: bwa_par.py <nworker> <hosts> <workdir> <runname> <dryrun>")
        print ("\t<dryrun>=1 will show command to run only; =0 will actually run. Default is 1")
        exit(1)
    nworker = int(sys.argv[1])
    hosts = hostlist.expand_hostlist(sys.argv[2])
    #workdir = pathlib.Path(__file__).parent.absolute()
    workdir = str(pathlib.Path(sys.argv[3]).absolute())
    #workdir = "/nfs/bio-sgx/{workdir}".format(workdir=workdir)
    runname = sys.argv[4]
    dryrun = True
    if len(sys.argv) == 6:
        dryrun = (int(sys.argv[5]) == 1)
    #runname = "splitPTest2"
    runpath = pathlib.Path(workdir)/runname
    runpath.mkdir(parents=True, exist_ok=True)
    scripts = gen_bwamem_workers(nworker, workdir, rundir=runname)
    submit_bwamem_jobs(hosts,scripts,workdir,runname,dryrun=dryrun)

