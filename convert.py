import hou

def convert_hda(node_hda=None, copy_parm_values=1):
        if not node_hda:
                node_hda = hou.selectedNodes()[0]
        source_name = node_hda.name()
        source_pos = node_hda.position()
        fdatype = utils.getfdatype()

        # CHECK IF WE NEED A GEO OBJ INSTEAD OF SUBNET, BECAUSECHILDEN ARE SOP BUT PARENT IS OBJECT
        if fdatype == "Sop" and node_hda.parent().childTypeCategory().name() == "Object":
            my_node = node_hda.parent().createNode("geo", source_name + "_UNLOCKED",True)
        else:
            my_node = node_hda.parent().createNode("subnet",source_name + "_UNLOCKED",True)

        node_copy = hou.copyNodesTo(node_hda.children(),my_node)[0]
        hda_parms = node_hda.parmTemplateGroup()
        my_node.setParmTemplateGroup(hda_parms)

        if copy_parm_values == 1:
                source_parms = node_hda.parms()
                new_parms = my_node.parms()
                # FINDS CORRESPONDING PARAMETERS
                for new_parm in new_parms:
                    for source_parm in source_parms:
                        if new_parm.name() == source_parm.name():
                            if source_parm.keyframes():
                                try:
                                    my_node.parm(new_parm.name()).setExpression(source_parm.rawValue())
                                except:
                                    my_node.parm(new_parm.name()).set(source_parm.eval())
                            else:
                                try:
                                    my_node.parm(new_parm.name()).set(source_parm.rawValue())
                                except:
                                    my_node.parm(new_parm.name()).set(source_parm.eval())

        # SHIFT NEW NODETO THE RIGHT
        new_pos = pos = (source_pos[0] +2, source_pos[1])
        my_node.setPosition(new_pos)

