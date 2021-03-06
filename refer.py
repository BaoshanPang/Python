# functions for reference file
import re

dctrl_c="/view/bpang.iter5.dctrl/vobs/rome_diab_tools/comp/src/drivers/dctrl.c"

# build the reference file in format:
# arch:target:Core/Processor
# for example:
# PowerPC VLE:PPCE200Z759N3V:Core

def build():
    f = open(dctrl_c, 'r')
    start=0
    a_tk = ''    
    for line in f:
        if(re.match('static TARGETDESCR ', line)):
            start=1
            arch = "NONE"
        elif(re.match('^\s+{ 0 }', line)):
            if a_tk != '':
                print a_tk
                a_tk = ''
            start=0
        elif start==1:
            if re.match("\s+/\*", line):
                continue;
            line = line.replace('{','').replace('}','').strip()
            td = re.split(',', line)
            if arch == "NONE":
                arch = td[0].strip('"')
                a_tk = arch
            else:
                target = td[0].strip('"')
                if (len(td) == 7) and (td[5].strip() == '1'):
                    a_tk = a_tk + ':' + target + ',' + 'Core'
                else:
                    a_tk = a_tk + ':' + target + ',' + 'Processor'
        else:
            pass
            
            
    


    
