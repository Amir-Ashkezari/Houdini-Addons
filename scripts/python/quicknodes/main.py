""" Speeds up node creation by assigning a
    shortcut for each custom function.
"""

import hou
import logging

logger = logging.getLogger('quicknodes')
logging.basicConfig(level=logging.WARNING, format='%(name)s:%(message)s')


context = {
    'Sop': ['attribwrangle', 'attribvop'], 'Dop': ['popwrangle', 'popvop'],
    'Cop2': ['vopcop2gen', 'vopcop2gen'], 'Chop': ['channelwrangle', 'vopchop'],
    'Lop': ['attribwrangle', 'attribvop']
}


###############################################################################
# Public functions
###############################################################################

def getSelectedNodes(node_type):
    """ Get selected nodes and the parent node. """
    try:
        selected_nodes = hou.selectedNodes()
        node_parent = selected_nodes[0].parent()
    except IndexError:
        logger.warning('Nothing selected!')
    else:
        def checkNodeType(node_type):
            """ Check if the given node type is available
                in the current network.
            """
            if isinstance(node_type, int):
                node_context = selected_nodes[0].type().category().name()
                try:
                    node_name = context[node_context][node_type]
                except KeyError:
                    return
                else:
                    node_items = selected_nodes, node_parent, node_name
                    return node_items
            child_category = node_parent.type().childTypeCategory()
            if child_category.nodeType(node_type):
                node_items = selected_nodes, node_parent, node_type
                return node_items
        # end checkNodeType
        return checkNodeType(node_type)
# end getSelectedNodes


def getPosition(selected_nodes):
    """ Public function, get a position for newly created node. """
    if isinstance(selected_nodes, tuple):
        network_pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        new_position = network_pane.selectPosition()
    else:
        get_node_position = selected_nodes.position()
        new_position = get_node_position + hou.Vector2([0, -1.125])
    return new_position
# end getPosition


def networkSetup(**kwargs):
    """ Public function, network organization. """
    new_node = kwargs.get('node')
    selected_nodes = kwargs.get('selNodes')
    node_color = kwargs.get('nodeColor')
    if isinstance(selected_nodes, tuple):
        for selected_node in selected_nodes:
            new_node.setNextInput(selected_node, output_index=0)
    else:
        new_node.setFirstInput(selected_nodes, 0)
    new_node.setCurrent(True, clear_all_selected=True)
    if node_color:
        new_node.setColor(hou.Color(node_color))
    new_node.setGenericFlag(hou.nodeFlag.Display, True)
    new_node.setGenericFlag(hou.nodeFlag.Render, True)
# end networkSetup


###############################################################################
# Quick Node functions
###############################################################################

def customWrangle():
    """ Create a wrangle based on the current context. """
    node_items = getSelectedNodes(node_type=0)
    if not node_items: return
    selected_nodes, node_parent, node_type = node_items
    new_node = node_parent.createNode(node_type)
    if node_type == 'vopcop2gen':
        for child in new_node.children():
            child.destroy(disable_safety_checks=True)
        new_node.createNode('snippet')
    node_position = getPosition(selected_nodes[0])
    new_node.setPosition(node_position)
    networkSetup(selNodes=selected_nodes[0], node=new_node)
# end customWrangle


def customVop():
    """ Create a vop based on the current context. """
    node_items = getSelectedNodes(node_type=1)
    if not node_items: return
    selected_nodes, node_parent, node_type = node_items
    new_node = node_parent.createNode(node_type)
    node_position = getPosition(selected_nodes[0])
    new_node.setPosition(node_position)
    node_color = (0.451, 0.369, 0.796)
    networkSetup(selNodes=selected_nodes[0], node=new_node, nodeColor=node_color)
    for child in new_node.children():
        child.destroy()
    parm_names = ['P', 'v', 'ptnum', 'primnum', 'Time', 'TimeInc', 'OpInput1']
    parm_types = [6, 6, 1, 1, 0, 0, 15]
    for parm_name, parm_type in zip(parm_names, parm_types):
        new_parm = new_node.createNode('parameter', '%s_parm' % parm_name)
        new_parm.parm('invisible').set(True)
        new_parm.parm('exportparm').set(2)
        new_parm.parm('parmname').set(parm_name)
        new_parm.parm('parmtype').set(parm_type)
        new_parm.setColor(hou.Color(1.0, 0.976, 0.666))
    new_node.layoutChildren()
# end customVop


def setOutput():
    """ Create an output null based on the current context. """
    node_items = getSelectedNodes(node_type='null')
    if not node_items: return
    selected_nodes, node_parent, node_type = node_items
    new_node = node_parent.createNode(node_type, 'OUT_%s' % node_parent)
    node_position = getPosition(selected_nodes[0])
    new_node.setPosition(node_position)
    node_color = (0.1, 0.1, 0.1)
    networkSetup(selNodes=selected_nodes[0], node=new_node, nodeColor=node_color)
# end setOutput


def multiMerge():
    """ Create a merge and connect output connections to input slot. """
    node_items = getSelectedNodes(node_type='merge')
    if not node_items: return
    selected_nodes, node_parent, node_type = node_items
    node_position = getPosition(selected_nodes)
    new_node = node_parent.createNode(node_type)
    new_node.setPosition(node_position)
    networkSetup(selNodes=selected_nodes, node=new_node)
# end multiMerge


def xform():
    """ Create a transform based on the current context. """
    node_items = getSelectedNodes(node_type='xform')
    if not node_items: return
    selected_nodes, node_parent, node_type = node_items
    new_node = node_parent.createNode(node_type)
    node_position = getPosition(selected_nodes[0])
    new_node.setPosition(node_position)
    networkSetup(selNodes=selected_nodes[0], node=new_node)
# end xform