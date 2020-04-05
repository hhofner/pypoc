'''
'''
__author__ = "Hans Hofner"

class EdgeHandler:
    '''
    Class responsible for handling `edges` of a networkX object based on a
    `foundation`, which is something that will define whether a link is 
    valid or not.
    '''
    valid_foundations = {'distance'}
    def __init__(self, edge_foundation):
        '''
        '''
        
        if not edge_foundation in EdgeHandler.valid_foundations:
            raise Exception(f'Incorrect edge foundation {edge_foundation}; '
                            f'must be one of {EdgeHandler.valid_foundations}')

        self.edge_foundation = edge_foundation

    # Main Entrance Method
    def handle_edges(self, networkx_object):
        if self.edge_foundation is 'distance':
            self._handle_edges_based_on_distance(networkx_object)
    
    def _handle_edges_based_on_distance(self, networkx_object):
        try:
            self.area
        except:
            raise Exception(f'To use distance foundation, please set the area with `set_area()`.')

        #TODO

    def set_area(self, area):
        try:
            self.area
        except:
            # Already exists, don't set again unless stated
            k = input(f'EdgeHandler.Area already set, set again? y/[n]')
            if k == 'y':
                self.area = area
            else:
                pass
        else:
            self.area = area

