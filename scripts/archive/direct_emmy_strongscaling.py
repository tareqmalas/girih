#!/usr/bin/env python

def submit_emmy_experiment(perf_ctr, nx, ny, nz, nt, is_dp, outfile, target_dir):
    import os
    import subprocess
    from string import Template
    from utils import ensure_dir    

    job_template=Template(
"""export OMP_NUM_THREADS=1; likwid-perfctr -c 0 -g $perf_ctr $exec_path --n-tests 3 --disable-source-point --npx 1 --npy 1 --npz 1 --nx $nx --ny $ny --nz $nz  --verbose 1 --target-ts 0 --nt $nt --target-kernel $kernel --cache-size 0  | tee $outfile""")


    target_dir = os.path.join(os.path.abspath("."),target_dir)
    ensure_dir(target_dir)
    outpath = os.path.join(target_dir,outfile)

    if(is_dp==1):
        exec_path = os.path.join(os.path.abspath("."),"build_dp/mwd_kernel")
    else:
        exec_path = os.path.join(os.path.abspath("."),"build/mwd_kernel")


    job_cmd = job_template.substitute(perf_ctr=perf_ctr, nx=nx, ny=ny, nz=nz, nt=nt, kernel=1, outfile=outpath, exec_path=exec_path, target_dir=target_dir)

    sts = subprocess.call(job_cmd, shell=True)
    #print job_cmd

def main():

    from utils import create_project_tarball 

    import socket
    hostname = socket.gethostname()

    exp_name = "emmy_1thread_strongscaling_fixed_x_fixed_size_f2p2GHz_at_%s" % (hostname)  
    tarball_dir='results/'+exp_name
    create_project_tarball(tarball_dir, "project_"+exp_name)
 

    target_dir='results/' + exp_name 

    nx=512


    perf_ctr = 'L3'
    for ny in range(8, 257, 4):
        nz = 512*512/ny
        outfile=(exp_name + '_perfctr_%s_ny_%d' % (perf_ctr,ny))
        nt = 50 
        submit_emmy_experiment(perf_ctr=perf_ctr, nx=nx, ny=ny, nz=nz, nt=nt, is_dp=0, outfile=outfile, target_dir=target_dir)


#    perf_ctr = 'L2'
#    for ny in range(8, 257, 4):
#        nz = 512*512/ny
#        outfile=(exp_name + '_perfctr_%s_ny_%d' % (perf_ctr,ny))
#        nt = 50 
#        submit_emmy_experiment(perf_ctr=perf_ctr, nx=nx, ny=ny, nz=nz, nt=nt, is_dp=0, outfile=outfile, target_dir=target_dir)


#    perf_ctr = 'MEM'
#    for ny in range(2784, 5000, 16):
#        nz = 512*512/ny
#        outfile=(exp_name + '_perfctr_%s_ny_%d' % (perf_ctr,ny))
#        nt = 50 
#        submit_emmy_experiment(perf_ctr=perf_ctr, nx=nx, ny=ny, nz=nz, nt=nt, is_dp=0, outfile=outfile, target_dir=target_dir)

if __name__ == "__main__":
    main()
