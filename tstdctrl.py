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


