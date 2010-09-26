def DrawRecttoCell():
	"""Returns a Draw function that is executed by a cell and therefore allows drawing to a cell"""

	import wx
	def Draw(grid, attr, dc, rect):
		dc.SetBrush(wx.Brush(wx.Colour(15, 255, 127), wx.SOLID))
		dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
		dc.DrawRectangleRect(rect)
	return Draw
