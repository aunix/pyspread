import types
from itertools import izip
from struct import pack, unpack

import pysparse.pysparseMatrix as pysparseMatrix

from numpy import array as numarray

class obj_lil_matrix(pysparseMatrix.PysparseMatrix):
    """
    Generic object sparse array class
    
    This class provides a sparse array for generic objects.
    
    Limits:
    -------
    There can only be a limited number of different objects in the
    sparse array because lil_matrix automagically stores everything
    as float64. So float64 that cannot be mapped correctly to int and
    back will cause problems. Therefore, a memory error is raised at 
    2**32 different objects in the array.
    
    Attributes:
    -----------
    objectpool: List with all objects that the lil_matrix poingts to
    lil_matrix: Stores the objects' positions in objectpool
    
    """
    
    def __init__(self, A=None, shape=None, dtype=None):
        if dtype != "O":
            # Normal lil_matrix
            self.has_objectmatrix = False
            pysparseMatrix.PysparseMatrix.__init__(A, shape, dtype)
            
        else:
            self.objectpool_limit = 2 ** 32
            self.has_objectmatrix = True
            self.none_value = unpack("L", pack("f", 0.0))[0]
            self.__initobjects(A, shape)
    
    def __initobjects(self, A=None, shape=None):
        """Sets up the object data structure"""
        if A is not None and not hasattr(A, 'shape'):
            A = numarray(A)
        
        if A is not None and shape is None:
            shape = A.shape
        
        if len(shape) == 1:
            shape = tuple(list(shape) + [1])
            
        self.objectpool = objectpool = [None]
        lil_matrix = sparse.lil_matrix(shape=shape, dtype="l")
        
        if A is not None:
            for i, obj in enumerate(A.flat):
                objkey = self._register_obj(obj)
                lil_matrix.set_shape((sum(lil_matrix.shape), 1))
                lil_matrix[i, 0] = self.i2f(objkey)
                lil_matrix.set_shape(shape)
            
            if len(self.objectpool) >= self.objectpool_limit:
                raise MemoryError, "There may be only less than 2**32 " + \
                                   "different objects in the array"
        self.objectpool = objectpool
        self.lil_matrix = lil_matrix
    
    def _getsingleitem(self, objkey):
        """Returns a single object (no slices)"""
        
        if objkey == self.none_value:
            return None
        
        return self.objectpool[object_key]
    
    def __getitem__(self, key):
        if not self.has_objectmatrix:
            return super(obj_lil_matrix, self).__getitem__(key)
        
        f2i = self.f2i
        
        if any(type(k) is types.SliceType for k in key):
            object_keys_float = self.lil_matrix[slice(key[0]), slice(key[1])]
            shape = object_keys.shape
            objkeys = map(f2i, object_keys_float.reshape((sum(shape), 1)))
            
            g = self._getsingleitem
            
            objects = [g(objkey) for objkey in objkeys]
            
            return numarray(objects, dtype = "O").reshape(shape)
            
        else:
            object_key = f2i(self.lil_matrix[key])
            return _getsingleitem(object_key)

    def _register_obj(self, obj):
        """Registers an object in objpool and returns object key"""
        
        if type(obj) is types.StringType:
            obj = intern(obj)
        
        try:
            objkey = self.objectpool.index(obj)
        
        except ValueError:
            objkey = len(self.objectpool)
            
            if objkey == self.none_value:
                self.objectpool.append(None)
                objkey += 1
                
            self.objectpool.append(obj)
            
        return objkey
        
    def __setitem__(self, key, val):
        if not self.has_objectmatrix:
            return super(obj_lil_matrix, self).__setitem__(key, val)
        
        if any(type(k) is types.SliceType for k in key):
            object_keys = self.lil_matrix[key]
            shape = object_keys.shape
            object_keys_flat = object_keys.toarray().flatten()
            
            try:
                it = val.flat
            except AttributeError:
                it = iter(val)
            
            for i, obj in enumerate(it):
                objkey = self._register_obj(obj)
                object_keys_flat[i] = self.i2f(objkey)
            self.lil_matrix[key] = object_keys_flat.reshape(shape)
            
        else:
            objkey = self._register_obj(val)
            self.lil_matrix[key] = self.i2f(objkey)
    
    def i2f(self, i):
        """Bijective mapping from uint32 to float32"""
        
        return unpack("f", pack("L", i))[0]
    
    def f2i(self, f):
        """Bijective mapping from float32 to int32"""
        
        return unpack("L", pack("f", f))[0]
    
