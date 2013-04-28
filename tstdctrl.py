#
import re
import pexpect

def get_arch_no(arch, strs):
    no = 0
    for line in strs.splitlines():
        if re.match('\s+\d+\) '+arch, line):
            no = line[:line.find(')')].strip()
            break
    return no

def start_dctrl():
    return pexpect.spawn('dctrl -t')

def select_arch(dctrl, arch):
#    print arch
    dctrl.expect('Select default architecture')
    no = get_arch_no(arch, dctrl.before)
    if no != 0:
        dctrl.send(str(no)+'\n')
    else:
        dctrl.send('1\n')
    return no
#    print dctrl.before
#    print arch,str(no)
def get_proc_no(proc, strs):
    procs = re.split('Possible cores', strs)[0]
    proc = re.findall('\d+\) '+proc, procs)
    return re.sub('\) .*', '', proc[0])

def get_core_no(core, strs):
    cores = re.split('Possible cores', strs)[1]
#    print cores, core
    core = re.findall('\d+\) '+core, cores)
    return re.sub('\) .*', '', core[0])

def select_proc(dctrl, proc):
    dctrl.expect('Select processor or core')
    no = get_proc_no(proc, dctrl.before)
    if no != 0:
        dctrl.send(str(no)+'\n')
    else:
        dctrl.send('1\n')
    return no

def select_core(dctrl, core):
    dctrl.expect('Select processor or core')
    no = get_core_no(core, dctrl.before)
    if no != 0:
        dctrl.send(str(no)+'\n')
    else:
        dctrl.send('1\n')
    return no

def select_mcore(dctrl, core):
    dctrl.expect('Select core')
    core = re.findall('\d+\) '+core, dctrl.before)
    no = re.sub('\) .*', '', core[0])
    dctrl.send(no+'\n')


def get_cores(dctrl):
    dctrl.expect('Select core')
    return re.findall('\d+\) \w+', dctrl.before)


def get_tks(dctrl):
        dctrl.expect('Select processor or core')
        dctrl.send('1\n')
        return dctrl.before

def check_kind(dctrl, target, kind):
    dctrl.expect('Select processor or core')
    find = 0
    in_core_part = 0
    for line in dctrl.before.splitlines():
        if re.match('Possible cores:', line):
            in_core_part = 1
        elif re.search('\s+'+target+'\s+', line):
            if kind == 'Core':
                if in_core_part == 1:
                    find = 1
                else:
                    find = 0
            else:
                if in_core_part == 0:
                    find = 1
                else:
                    find = 0
        else:
            pass
    if find == 0:
        print target, kind, in_core_part
    dctrl.send('1\n')
    return find

def select_object(dctrl, no):
    dctrl.expect('Select object format')
    dctrl.send(str(no)+'\n')

def select_fpmode(dctrl, no):
    dctrl.expect('Select float point mode')
    dctrl.send(str(no)+'\n')

def select_env(dctrl, no):
    dctrl.expect('Select environment')
    dctrl.send(str(no)+'\n')

def skip(dctrl):
    end = 0
    while end == 0:
        i = dctrl.expect(['Select ', 'Selected'])
        if i == 0:
            dctrl.send('1\n')
        else:
            end = 1

def get_mode(dctrl):
    end = 0
    while end == 0:
        i = dctrl.expect(['Select ', 'Selected[^\n]*'])
        if i == 0:
            dctrl.send('1\n')
        else:
            end = 1
            mode = re.findall('-t\w+:\w+', dctrl.after)
    return mode[0]

##Check if processors are showed as processors and cores are showed as cores
## ref: the reference file contains the expected result in the formal: arch:target,kind:target,kind:...
def layout(ref):
    f = open(ref, 'r');
    for line in f:
         lst = re.split(':', line)
         arch = lst[0]
         print "Checking", arch 
         if arch == 'PAsemi' or arch == 'Pentium' or arch == 'MCS':
             print "No process or core to choose for", arch
             continue
         dctrl = start_dctrl()         
         no = select_arch(dctrl, arch)         
         if no == 0:
             skip(dctrl)
             continue
         t_k = get_tks(dctrl)
         skip(dctrl)
         [procs, cores] = re.split('Possible cores', t_k)
         for x in lst[1:]:
             [target, kind] = re.split(',', x)
             kind = kind.strip()
             if kind == 'Core':
                 if re.search(' '+target, cores):
                     print target, kind, "PASS"
                 else:
                     print target, kind, "FAIL"
             else:
                 if re.search(' '+target, procs):
                     print target, kind, "PASS"
                 else:
                     print target, kind, "FAIL"



#Check for heterogeneous multicore
#ref: the reference file which is in format: arch:target:core1,core2,...
def hm(ref):
    f = open(ref, 'r');
    for line in f:
        line = line.strip()
        print "Checking", line
        lst = re.split(':', line)
        arch = lst[0]
        dctrl = start_dctrl()
        no = select_arch(dctrl, arch)
        if no == 0:
            print 'Unsupported arch', arch
            continue
        proc = lst[1]
        no = select_proc(dctrl, proc)
        cores = get_cores(dctrl)
        cs = re.split(',', lst[2])
        if len(cores) != len(cs):
            print "FAIL: the core number should be ", len(cs), "but there is", len(cores)
            continue
        if not all(x in str(cores) for x in cs):
            print "FAIL: unmatched core name"
            print cores
            print cs
            continue
        for core in cs:
            dctrl = start_dctrl()
            select_arch(dctrl, arch)
            select_proc(dctrl, proc)
            select_mcore(dctrl, core)
            mode1 = get_mode(dctrl)
            dctrl = start_dctrl()
            select_arch(dctrl, arch)
            select_core(dctrl, core)
            mode2 = get_mode(dctrl)
            if mode1 != mode2:
                print "FAIL: unmatched mode", mode1, mode2
                continue
        print "PASS"
