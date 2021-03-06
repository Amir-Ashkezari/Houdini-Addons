""" Speeds up node creation by assigning a
    shortcut for each custom function.
"""

import hou
import logging

logger = logging.getLogger('quicknodes')
logging.basicConfig(level=logging.WARNING, format='%(name)s:%(message)s')


context = {
    'Sop': ['attribwrangle', 'attribvop'],
    'Dop': ['popwrangle', 'popvop'], 'Cop2': ['vopcop2gen', 'vopcop2gen'],
    'Chop': ['channelwrangle', 'vopchop'], 'Lop': ['attribwrangle', 'attribvop']
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
        return getNetworkInfo(node_type)
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


def getNetworkInfo(node_type):
    """ Public function, find a node with display flag or just the context. """
    network = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    network_path = network.pwd()
    network_type = network_path.childTypeCategory()
    node_parent = hou.node(network_path.path())

    base_node = node_parent
    for node in node_parent.children():
        if (node.isDisplayFlagSet()):
            base_node = node
            break

    if isinstance(node_type, int):
        try:
            node_name = context[network_type.name()][node_type]
        except KeyError:
            return
        else:
            net_info = base_node, node_parent, node_name
            return net_info

    net_info = base_node, node_parent, node_type
    return net_info
# end getNetworkInfo


def getPosition(**kwargs):
    """ Public function, get a position for newly created node. """
    selected_nodes = kwargs.get('selNodes')
    node_parent = kwargs.get('parent')

    if isinstance(selected_nodes, tuple) or selected_nodes == node_parent:
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

    new_node_typename = new_node.type().category().name()
    base_node = selected_nodes[0] if isinstance(selected_nodes, tuple) else selected_nodes
    selected_nodes_typename = base_node.type().category().name()

    if isinstance(selected_nodes, tuple):
        for selected_node in selected_nodes:
            new_node.setNextInput(selected_node, output_index=0)
    elif new_node_typename == selected_nodes_typename:
        new_node.setFirstInput(selected_nodes, 0)

    if node_color:
        new_node.setColor(hou.Color(node_color))

    new_node.setCurrent(True, clear_all_selected=True)
    new_node.setGenericFlag(hou.nodeFlag.Display, True)
    new_node.setGenericFlag(hou.nodeFlag.Render, True)
# end networkSetup


###############################################################################
# Quick Node functions
###############################################################################

def customWrangle():
    """ Create a wrangle based on the current context. """
    node_items = getSelectedNodes(node_type=0)
    if not node_items:
        return
        
    selected_nodes, node_parent, node_type = node_items
    base_node = selected_nodes[0] if isinstance(selected_nodes, tuple) else selected_nodes
    node_position = getPosition(selNodes=base_node, parent=node_parent)

    new_node = node_parent.createNode(node_type)
    if node_type == 'vopcop2gen':
        for child in new_node.children():
            child.destroy(disable_safety_checks=True)
        new_node.createNode('snippet')

    new_node.setPosition(node_position)
    networkSetup(selNodes=base_node, node=new_node)
# end customWrangle


def customVop():
    """ Create a vop based on the current context. """
    node_items = getSelectedNodes(node_type=1)
    if not node_items:
        return

    selected_nodes, node_parent, node_type = node_items
    base_node = selected_nodes[0] if isinstance(selected_nodes, tuple) else selected_nodes
    node_position = getPosition(selNodes=base_node, parent=node_parent)

    new_node = node_parent.createNode(node_type)
    new_node.setPosition(node_position)
    node_color = (0.451, 0.369, 0.796)
    networkSetup(selNodes=base_node, node=new_node, nodeColor=node_color)

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
    if not node_items:
        return

    selected_nodes, node_parent, node_type = node_items
    base_node = selected_nodes[0] if isinstance(selected_nodes, tuple) else selected_nodes
    node_position = getPosition(selNodes=base_node, parent=node_parent)

    new_node = node_parent.createNode(node_type, 'OUT_%s' % node_parent)
    new_node.setPosition(node_position)
    node_color = (0.1, 0.1, 0.1)
    networkSetup(selNodes=base_node, node=new_node, nodeColor=node_color)
# end setOutput


def multiMerge():
    """ Create a merge and connect output connections to input slot. """
    node_items = getSelectedNodes(node_type='merge')
    if not node_items:
        return

    selected_nodes, node_parent, node_type = node_items
    node_position = getPosition(selNodes=selected_nodes, parent=node_parent)

    new_node = node_parent.createNode(node_type)
    new_node.setPosition(node_position)
    networkSetup(selNodes=selected_nodes, node=new_node)
# end multiMerge


def xform():
    """ Create a transform based on the current context. """
    node_items = getSelectedNodes(node_type='xform')
    if not node_items:
        return

    selected_nodes, node_parent, node_type = node_items
    base_node = selected_nodes[0] if isinstance(selected_nodes, tuple) else selected_nodes
    node_position = getPosition(selNodes=base_node, parent=node_parent)

    new_node = node_parent.createNode(node_type)
    new_node.setPosition(node_position)
    networkSetup(selNodes=base_node, node=new_node)
# end xform


def detach():
    """ Detach a node from it's input and output connections. """
    try:
        selected_nodes = hou.selectedNodes()
    except IndexError:
        logger.warning('Nothing selected!')
    else:
        for node in selected_nodes:
            for in_conn in node.inputConnections():
                for out_conn in node.outputConnections():
                    if in_conn.inputIndex() == out_conn.outputIndex():
                        output_idx = 0 if in_conn.inputItem().networkItemType() == hou.networkItemType.NetworkDot else in_conn.outputIndex()
                        out_conn.outputItem().setInput(out_conn.inputIndex(), in_conn.inputItem(), output_idx)
                node.setInput(in_conn.inputIndex(), None)

            for out_conn in node.outputConnections():
                out_conn.outputItem().setInput(out_conn.inputIndex(), None)

            pos = node.position()
            node.setPosition(pos + hou.Vector2(1.0, 0.0))
# end detach


def sopSolver(**kwargs):
    """ Place down a dop net with sop solver. """
    network = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    network_typename = network.pwd().childTypeCategory().name()

    if (network_typename != 'Sop'):
        return

    node_items = getSelectedNodes(node_type='dopnet')
    if not node_items:
        return

    selected_nodes, node_parent, node_type = node_items
    base_node = selected_nodes[0] if isinstance(selected_nodes, tuple) else selected_nodes
    node_position = getPosition(selNodes=base_node, parent=node_parent)

    new_node = node_parent.createNode(node_type, 'sopsolver')
    new_node.setPosition(node_position)
    networkSetup(selNodes=base_node, node=new_node)

    dopobj = new_node.createNode('emptyobject', 'object')
    dopobj.parm('objname').set('`opname(".")`')
    sopgeo = new_node.createNode('sopgeo')
    sopgeo.parm('soppath').set('`opinputpath( "..", 0 )`')
    sopgeo.setNextInput(dopobj)
    sopsolver = new_node.createNode('sopsolver::2.0')
    multisolver = new_node.createNode('multisolver')
    multisolver.setInput(0, sopgeo)
    multisolver.setInput(1, sopsolver)
    output = new_node.node(new_node.path() + '/output')
    output.setInput(0, multisolver)
    new_node.layoutChildren()
# end sopSolver
