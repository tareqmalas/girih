#!/usr/bin/env python
def main():
    import sys

    raw_data = load_csv(sys.argv[1])

 #   for ts in ['Naive', 'Dynamic-Intra-Diamond']  
    for k in [0, 1, 2]:
        for is_dp in [0,1]:
            plot_lines(raw_data, k, is_dp)

        
def plot_lines(raw_data, stencil_kernel, is_dp):
    from operator import itemgetter
    import matplotlib.pyplot as plt
    import pylab

    ts_l = set()
    for k in raw_data:
        ts_l.add(k['Time stepper orig name'])
    ts_l = list(ts_l)

    th = set()
    for k in raw_data:
        th.add(int(k['OpenMP Threads']))
    th = list(th)

    #tb_l = [3, 7]
    tb_l = set()
    for k in raw_data:
        tb_l.add(k['Time unroll'])
    tb_l = list(tb_l)
    tb_l = map(int,tb_l)
    tb_l.sort()
    #print tb_l
    
    req_fields = [('Time stepper orig name', 0), ('OpenMP Threads', 1), ('MStencil/s  MAX', 2), ('Time unroll',1)]
    req_fields = req_fields + [('Sustained Memory BW', 2)]
    data = []
    for k in raw_data:
        tup = []
        # add the general fileds
        for f in req_fields:
            v = k[f[0]]
            if f[1]==1: v = int(k[f[0]]) 
            if f[1]==2: v = float(k[f[0]]) 
            tup = tup + [v]

        # add the stencil operator
        if  int(k['Stencil Kernel semi-bandwidth'])==4:
            stencil = 0
        elif  k['Stencil Kernel coefficients'] in 'constant':
            stencil = 1
        else:
            stencil = 2
        tup = tup + [stencil]

        # add the precision information
        if k['Precision'] in 'DP':
            tup = tup + [1]
        else:
            tup = tup + [0]

        data.append(tuple(tup))

        
    data = sorted(data, key=itemgetter(0, 3, 1))
    #for i in data: print i

    max_single = 0
    fig, ax1 = plt.subplots()
    lns = []
    for ts in ts_l:
        if ts == 'Naive':
            tb_l2 = [3]
        else:
            tb_l2 = tb_l
        for tb in tb_l2:
#            if(ts == 'Naive' and tb == 3) or ts != 'Naive':
            x = []
            y = []
            y_m = []
            for k in data:
                if (('Diamond' in k[0] and k[3] == tb) or ('Naive' in k[0]) ) and (k[0]==ts) and (k[5]==stencil_kernel) and (k[6]==is_dp):
                    if k[1] == 1 and max_single < k[2]: max_single = k[2]
                    y_m.append(k[4])
                    x.append(k[1])
                    y.append(k[2])

            marker = 'o'
            if ts == 'Naive':
                col = 'g'
                marker = '*'
            elif tb == 1:
                col = 'b'
            elif tb == 3:
                col = 'c'
            elif tb == 7:
                col = 'k'
            elif tb == 15:
                col = 'm'

            if 'Naive' in ts: 
#                ts2 = ts + ' CB+Static,1 sched.'
                ts2 = ts
            elif 'Diamond' in ts:
#                ts2 = 'Wavefront-Diamond_TB'+str(tb)
                ts2 = 'WF-Diam'+str(tb)
            #print ts2, is_dp, stencil_kernel, tb, x, y
            if(x):
                lns = lns + ax1.plot(x, y, color=col, marker=marker, linestyle='-', label=ts2)
            if(y_m):
                ax2 = ax1.twinx()
                lns = lns + ax2.plot(x, y_m, color=col, marker=marker, linestyle='-.', label=ts2+'_m')



    # add limits
    mem_limit=0
#    sus_mem_bw = 36500 #SB
    sus_mem_bw = 40000 #IB

    if stencil_kernel == 0:
        mem_limit = sus_mem_bw/16
    elif stencil_kernel == 1:
        mem_limit = sus_mem_bw/12
    elif stencil_kernel == 2:
        mem_limit = sus_mem_bw/20
    if is_dp == 1: mem_limit = mem_limit / 2
    lns = lns + ax1.plot([1, len(th)], [mem_limit, mem_limit], color='g', linestyle='--', label='BW limit')


    # add ideal scaling
    ideal = [i*max_single for i in th]
    lns = lns + ax1.plot(th, ideal, color='r', linestyle='--', label='Ideal')

    title = 'Thread scaling of'
    if stencil_kernel == 0:
        title = title + ' 25_pt constant coeff. star stencil'
    elif stencil_kernel == 1:
        title = title + ' 7_pt constant coeff. star stencil'
    elif stencil_kernel == 2:
        title = title + ' 7_pt varialbe. coeff. star stencil'

    if is_dp == 1:
        title = title + ' in double precision'
    else:
        title = title + ' in single precision'

    f_name = title.replace(' ', '_') + '.png'

    ax1.set_xlabel('Threads #')
    ax1.set_ylabel('MStencils/s')
    ax2.set_ylabel('MBytes/s')
    plt.title(title)
 
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc='best')
#    ax1.legend(loc='best')
#    ax2.legend(loc='best')
    ax1.grid()
    pylab.savefig(f_name)

    #plt.show()     
    plt.clf()
        
def load_csv(data_file):
    from csv import DictReader
    with open(data_file, 'rb') as output_file:
        data = DictReader(output_file)
        data = [k for k in data]
    return data
    
    
if __name__ == "__main__":
    main()
