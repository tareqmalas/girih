#!/usr/bin/env python

def llsub_neser_experiment(npx, npy, npz, ppn, nx, ny, nz, nt, ts, t_dim, is_contig, outfile, target_dir):
    import os
    from string import Template
    from utils import ensure_dir    

    job_template=Template("""#!/bin/sh
#@ job_name         = stencil_scaling
#@ output           = $outfile.out
#@ error            = $outfile.err
#@ job_type         = parallel
#@ node             = $nn
#@ tasks_per_node   = $ppn
#@ wall_clock_limit = 29:00
#@ account_no = k156
#@ queue
source /etc/profile.d/modules.sh

#export TAU_METRICS=PAPI_L2_DCM
export TAU_METRICS=PAPI_TLB_DM:PAPI_L1_DCM
module switch openmpi/1.5.3-intel
module load intel-compilers/11.1
module load tau/2.21.4/intel 
cd $target_dir

$$MPIEXEC -np $np $exec_path --n-tests 2 --npx $npx --npy $npy --npz $npz --nx $nx --ny $ny --nz $nz --nt $nt --target-ts $ts --t-dim $t_dim --z-mpi-contig $is_contig""")

    target_dir = os.path.join(os.path.abspath("."),target_dir)
    ensure_dir(target_dir)
    outpath = os.path.join(target_dir,outfile)

    np = npx*npy*npz
    exec_path = os.path.join(os.path.abspath("."),"build/mwd_kernel")
    nn = np/ppn
    job_script = job_template.substitute(nn=nn, ppn=ppn, np=np, npx=npx, npy=npy, npz=npz, nx=nx, ny=ny, nz=nz, nt=nt, ts=ts, t_dim=t_dim, is_contig=is_contig, outfile=outpath, exec_path=exec_path, target_dir=target_dir)
    outscript = outpath+".ll"
    with open(outscript, 'w') as f:
        f.write(job_script)

    cmd_str = "llsubmit "+ outscript
    #os.system(cmd_str)
    print cmd_str

def main():

    from utils import create_project_tarball 
    exp_name = "neser_ppn_map_tau_papi_fp"  
    tarball_dir='results/'+exp_name
    create_project_tarball(tarball_dir, "project_"+exp_name)
 
    # Strong scaling study
    min_p = 8
    nnz = min_p*256
    npx=1
    npy=1
    nx=256
    ny=256
    nt=402
    npz= 8
    k = 2 # halo-first TS

    is_contig = 0
    for ppn in [1, 2, 4, 8]:
        target_dir='results/' + exp_name + '/ts%d_%d_%d_%dp_%dppn' % (k,npx,npy,npz,ppn)
        outfile=(exp_name + '_ts%d_%d_%d_%dp_%dppn' % (k,npx,npy,npz,ppn))
        llsub_neser_experiment(
                   npx = npx,
                   npy = npy,
                   npz = npz,
                   ppn = ppn,
                   nx = nx,
                   ny = ny,
                   nz = nnz,
                   nt = nt,
                   ts=k,
                   t_dim=0,
                   is_contig=is_contig,
                   outfile=outfile,
                   target_dir=target_dir)

if __name__ == "__main__":
    main()
