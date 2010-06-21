##      dotgen.py
#       
#       Copyright 2009 Hugo Teso <hugo.teso@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import sys

def generate_dot(localip, gateway, targets=[], steps=[], locals=[], ASNs={}, ASDs={}, direction='TD', user_data=None):

    dotcode = "digraph G {\n\n\t"

#    # To be used with twopi layout
#    dotcode += 'overlap = "scale"\n'
#    dotcode += 'sep = 0.5\n'
#    dotcode += 'ranksep = "0.25 equally"\n'

    dotcode += 'rankdir="' + direction + '"\n'
    #dotcode += "bgcolor=grey0\n\n"
    dotcode += "bgcolor=\"#373D49\"\n\n"
    dotcode += 'root="' + localip + '";\n\n'
    dotcode += 'concentrate="true";\n\n'
    #dotcode += "\nnode [shape=record,color=azure3,style=filled fillcolor=skyazure3];\n"
    dotcode += "\nnode [shape=record,color=azure3, fontcolor=azure3, style=rounded];\n"

    #######################################
    #
    # Create ASN clusters
    #
    #######################################
    dotcode += "\n#ASN clustering\n"
    for asn in ASNs:
        dotcode += '\tsubgraph cluster_%s {\n' % asn
        if asn == 'local':
            dotcode += '\t\tcolor="mediumseagreen";'
            dotcode += '\t\tfontcolor="mediumseagreen";'
        else:
            dotcode += '\t\tcolor="#608686";'
            dotcode += '\t\tfontcolor="#608686";'
        dotcode += '\t\tnode [fillcolor="#60baba"];'
        #dotcode += '\t\tnode [fillcolor="#60baba",style=filled];'
        dotcode += '\t\tfontsize = 10;'
        dotcode += '\t\tlabel = "%s\\n[%s]"\n' % (asn,ASDs[asn])
        for ip in ASNs[asn]:

            dotcode += '\t\t"%s";\n'%ip
        dotcode += "\t}\n"

    #######################################
    #
    # Asign URLs
    #
    #######################################
    for target in targets:
        dotcode += '\t"' + target + '" [URL="' + target + '"]\n'
    for local in locals:
        dotcode += '\t"' + local + '" [URL="' + local + '"]\n'
    for step in steps:
        for node in step:
            dotcode += '\t"' + node + '" [URL="' + node + '"]\n'


    #######################################
    #
    # Targets with diferent color
    #
    #######################################
    if len(targets) != 0 or len(locals) != 0:
        for target in targets:

            # I don't like this code...
            try:
                # Get OS String
                target_os = target + '_os'
                target_os = user_data[target_os][0]
                target_os = target_os.split(' ')
                # Get just two words if OS name is too large
                if len(target_os) > 1:
                    target_os = ' '.join([target_os[0], target_os[1], '...'])
                else:
                    target_os = target_os[0]
                dotcode += '\t"' + target +  '"' + ' [shape=record,color=indianred3,fontcolor=indianred1,label="' + target + '\\n' + target_os + '"];' + "\n"
            except:
                dotcode += '\t"' + target +  '"' + ' [shape=record,color=indianred3,fontcolor=indianred1,label="' + target + '"];' + "\n"

            #dotcode += '\t"' + target +  '"' + ' [shape=record,color=indianred3,fontcolor=indianred1,label="' + target + '"];' + "\n"
            #dotcode += '\t"' + target +  '"' + ' [shape=record,color=red3,fillcolor=red1,style=filled,label="' + target + '"];' + "\n"
        dotcode += "\n"
    
        i = 0
        for target in targets:
            # If there are steps for that target
            try:
                for step in steps[i][0:-1]:
                    dotcode += '\t"' + step + '"->' + "\n"
            except:
                pass
            dotcode += '\t"' + target + '" [color="azure3"];' + "\n\n"
            i = i + 1
    
        for local in locals:
            dotcode += '\t"' + localip + '"->' + "\n"
            dotcode += '\t"' + local + '" [color="azure3"];' + "\n\n"

    dotcode += "}"

    return dotcode
