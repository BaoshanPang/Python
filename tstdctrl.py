#
import re
import pexpect

def get_arch_no(arch, strs):
    no = 0
    for line in strs.splitlines():
        if re.match('\s+\d\) '+arch, line):
            no = line[:line.find(')')].strip()
            break
    return no

def check_arch(arch):
         dctrl = pexpect.spawn('dctrl -t')
         dctrl.expect('Select default architecture')
         no = get_arch_no(arch, dctrl.before)
         dctrl.send(str(no))
         print dctrl.before
         print arch,str(no)

def layout(ref):
    f = open(ref, 'r');
    for line in f:
         lst = re.split(':', line)
         arch = lst[0]
         target = lst[1]
         kind = lst[2]
         check_arch(arch)
         break
#         print arch, target, kind
         
