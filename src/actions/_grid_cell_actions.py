
## GETTERS!

class CellTextActions(object):
    """Cell text controller prototype"""
    
    def __init__(self):
        pass
    
    def set_text_font(self, key, font):
        """Sets text font for key cell"""
        
        raise NotImplementedError
        
    def set_text_size(self, key, size):
        """Sets text font for key cell"""
        
        raise NotImplementedError
        
    def set_text_align(self, key, align):
        """Sets text font for key cell"""
        
        raise NotImplementedError    
    
    def set_text_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    def set_text_style(self,  key, style):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    def set_text_frozenstate(self, key, frozenstate):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
class CellBackgroundActions(object):
    """Cell background controller prototype"""

    def __init__(self):
        pass

    def set_background_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
    
    
class CellBorderActions(object):
    """Cell border controller prototype"""

    def __init__(self):
        pass

    def set_cell_border_color(self, key, color):
        """Sets text font for key cell"""
        
        raise NotImplementedError
        
    def set_cell_right_border_width(self, key, width):
        """Sets text font for key cell"""
        
        raise NotImplementedError

    def set_cell_lower_border_width(self, key, width):
        """Sets text font for key cell"""
        
        raise NotImplementedError


class CellAttributeActions(CellTextActions, CellBackgroundActions, 
                              CellBorderActions):
    """Cell attribute controller prototype"""

    def __init__(self):
        pass

class CellActions(CellAttributeActions):
    """Cell controller prototype"""

    def __init__(self):
        pass

    def get_cell_code(self):
        """Gets code for key cell"""
        
        pass

    def set_cell_code(self,  key,  code):
        """Sets code for key cell"""
        
        raise NotImplementedError
        
    def delete_cell(self,  key):
        """Deletes key cell"""
        
        raise NotImplementedError
    
