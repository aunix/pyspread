# -*- coding: utf-8 -*-
from types import SliceType

class D(dict):
    def __missing__(self, value):
        return None
    
    def cell_array_generator(self, key):
        """Generator traversing cells specified in key
        
        Parameters
        ----------
        key: Iterable of Integer or slice
        \tThe key specifies the cell keys of the generator
        
        """
        
        for i, key_ele in enumerate(key):
            
            # Get first element of key that is a slice
            
            if type(key_ele) is SliceType:
                # Use slicerange here
                slc_keys = xrange(key_ele.start, key_ele.stop)
                
                key_list = list(key)
                
                key_list[i] = None
                
                has_subslice = any(type(ele) is SliceType for ele in key_list)
                                            
                for slc_key in slc_keys:
                    key_list[i] = slc_key
                    
                    if has_subslice:
                        # If there is a slice left yield generator
                        yield self.cell_array_generator(key_list)
                        
                    else:
                        # No slices? Yield value
                        yield self[tuple(key_list)]
                    
                break

d = D()

d[2,3] = 3

cell_gen = d.cell_array_generator((slice(1, 300000), slice(0, 70)))

for row in cell_gen:
    [cell for cell in row]
