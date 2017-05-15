# -*- coding: utf-8 -*-  # Définition l'encodage des caractères

from Tkinter import *

import tkFont
import sys,time
import tkFileDialog
from functools import partial

import os


import time


from gomill import sgf, sgf_moves
import goban

bg='silver' #background color, where the coordinates are displayed

def common_draw_color(self):
	dim=self.dim
	new_network=[[0 for row in range(dim)] for col in range(dim)]
	
	for i in range(dim):
		for j in range(dim):
			if self.grid[i][j]==1 or self.network[i][j]==1:
				new_network[i][j]=1
			if self.grid[i][j]==2 or self.network[i][j]==2:
				new_network[i][j]=2
	
	#looking for new color controled points
	for i in range(dim):
		for j in range(dim):
			if self.network[i][j] in [0] and self.grid[i][j] in [0,-1,-2]: #empty point (not a stone)
				neighbors=goban.neighborhood(i,j,dim)
				count=0
				for u,v in neighbors:
					if self.links[p2l(i,j,u,v,dim)]==1: #black colored link
						count+=1
					elif self.links[p2l(i,j,u,v,dim)]==2: #white colored link
						count-=1
	
				if count>=len(neighbors)-1:
					new_network[i][j]=1 #enough black links (and no white link) to become black color controlled
				elif count<=-(len(neighbors)-1):
					new_network[i][j]=2 #enough white links (and no black link) to become white color controlled

	
	self.network=new_network
	#looking for new links
	links=[0]*2*dim*dim
	for i in range(dim):
		for j in range(dim):
			neighbors=goban.neighborhood(i,j,dim)
			if self.network[i][j]==1:
				for u,v in neighbors:
					if links[p2l(i,j,u,v,dim)]==0:
						links[p2l(i,j,u,v,dim)]=1 #a color controled point color its links to its empty neighbours
					elif links[p2l(i,j,u,v,dim)]!=1:
						links[p2l(i,j,u,v,dim)]=1.5 #link between two color controled point of opposite colors
					
			elif self.network[i][j]==2:
				for u,v in neighbors:
					if links[p2l(i,j,u,v,dim)]==0:
						links[p2l(i,j,u,v,dim)]=2 #a color controled point color its links to its empty neighbours
					elif links[p2l(i,j,u,v,dim)]!=2:
						links[p2l(i,j,u,v,dim)]=1.5 #link between two color controled point of opposite colors
	
	
	
	

	for i,j in [[1,j] for j in range(1,dim-2)] + [[dim-2,j] for j in range(1,dim-2)] + [[i,1] for i in range(1,dim-2)] + [[i,dim-2] for i in range(1,dim-2)]:
			#empty point on the 2nd line, having at least one of its links colored and none opposite-colored, colors its link to the edge
			if self.network[i][j]==0:
				neighbors=goban.neighborhood(i,j,dim)
				count_black=0
				count_white=0
				for u,v in neighbors:
					if self.links[p2l(i,j,u,v,dim)]==1: #black colored link
						count_black+=1
					elif self.links[p2l(i,j,u,v,dim)]==2: #white colored link
						count_white+=1
				if count_black>0 and count_white==0:
					if i==1:
						links[p2l(i,j,0,j,dim)]=1
					if i==dim-2:
						links[p2l(i,j,dim-1,j,dim)]=1
					if j==1:
						links[p2l(i,j,i,0,dim)]=1
					if j==dim-2:
						links[p2l(i,j,i,dim-1,dim)]=1
				elif count_black==0 and count_white>0:
					if i==1:
						links[p2l(i,j,0,j,dim)]=2
					if i==dim-2:
						links[p2l(i,j,dim-1,j,dim)]=2
					if j==1:
						links[p2l(i,j,i,0,dim)]=2
					if j==dim-2:
						links[p2l(i,j,i,dim-1,dim)]=2

	
	#a link between two empty points, each of which has at least one same-coloured link and no opposite-coloured links, is coloured.
	for i in range(dim):
		for j in range(dim):
			neighbors=goban.neighborhood(i,j,dim)
			if self.network[i][j]==0: #an empty point
				for u,v in neighbors:
					if self.network[u][v]==0: #another empty point
						if links[p2l(i,j,u,v,dim)]==0: #link between both points is not already colored
							count_black1=0
							count_white1=0
							count_black2=0
							count_white2=0
							for ii,jj in neighbors: #how many colored links has the first point?
								if self.links[p2l(i,j,ii,jj,dim)]==1: #black colored link
									count_black1+=1
								elif self.links[p2l(i,j,ii,jj,dim)]==2: #white colored link
									count_white1+=1
							if count_black1>0 and count_white1==0: #that first point has only black links
								for uu,vv in goban.neighborhood(u,v,dim): #how many colored links has the second point?
									if self.links[p2l(u,v,uu,vv,dim)]==1: #black colored link
										count_black2+=1
									elif self.links[p2l(u,v,uu,vv,dim)]==2: #white colored link
										count_white2+=1
								if count_black2>0 and count_white2==0: #that second point has only black links as well
									links[p2l(i,j,u,v,dim)]=1 #so link should be colored in black
							elif count_black1==0 and count_white1>0: #that first point has only white links
								for uu,vv in goban.neighborhood(u,v,dim):  #how many colored links has the second point?
									if self.links[p2l(u,v,uu,vv,dim)]==1: #black colored link
										count_black2+=1
									elif self.links[p2l(u,v,uu,vv,dim)]==2: #white colored link
										count_white2+=1
								if count_black2==0 and count_white2>0: #that second point has only white links as well
									links[p2l(i,j,u,v,dim)]=2 #so link should be colored in white
	self.network=new_network
	self.links=links
	self.goban.display(self.grid,self.markup,self.network,self.links)
	



from goban import *

def get_node_number(node):
	k=0
	while node:
		node=node[0]
		k+=1
	return k

def get_node(root,number=0):
	if number==0:return root
	node=root
	k=0
	while k!=number:
		#print node.get_move()
		if not node:
			return False
		node=node[0]
		k+=1
	return node



def gtp2ij(move):
	#print "gtp2ij("+move+")"
	# a18 => (17,0)
	letters=['a','b','c','d','e','f','g','h','j','k','l','m','n','o','p','q','r','s','t']
	return int(move[1:])-1,letters.index(move[0].lower())


def ij2gtp(m):
	#print "ij2gtp("+str(m)+")"
	# (17,0) => a18
	
	if m==None:
		return "pass"
	i,j=m
	letters=['a','b','c','d','e','f','g','h','j','k','l','m','n','o','p','q','r','s','t']
	return letters[j]+str(i+1)



def alert(text_to_display):
	popup=Toplevel()
	label= Label(popup,text=text_to_display)
	label.pack()
	ok_button = Button(popup, text="OK", command=popup.destroy)
	ok_button.pack()
	#popup.mainloop()





class OpenMove():
	def __init__(self,parent,move,dim,sgf,goban_size=200):
		self.parent=parent
		self.move=move
		self.dim=dim
		self.sgf=sgf
		self.goban_size=goban_size
		self.initialize()
		self.calculate_color=common_draw_color
		self.frame=0
		
	def lock(self):
		self.locked=True

	def unlock(self,after=False):
		if after:
			print "unlocking 2/2"
			self.locked=False
		else:
			print "unlocking 1/2"
			self.popup.after(100,lambda: self.unlock(True))
	
	def close(self):
		if self.locked:
			return
		print "closing popup"
		self.popup.destroy()

		self.parent.all_popups.remove(self)
		
		print "done"
	
	def undo(self,event=None):
		print "UNDO"
		if self.locked:
			print "failed!"
			return

		if len(self.history)<1:
			return
		popup=self.popup
		self.grid,self.markup=self.history.pop()
		self.next_color=3-self.next_color
		self.network=[[0 for row in range(self.dim)] for col in range(self.dim)]
		self.links=[0]*2*self.dim*self.dim
		self.goban.display(self.grid,self.markup,self.network,self.links)
		self.frame=0



	def click(self,event):
		dim=self.dim
		print "dim:::",dim
		#add/remove black stone
		#check pointer location
		i,j=self.goban.xy2ij(event.x,event.y)
		color=self.next_color
		if 0 <= i <= dim-1 and 0 <= j <= dim-1:
			#inside the grid
			#what is under the pointer ?
			
			if self.grid[i][j] not in (-1,-2,1,2):
				#nothing, so we add a black stone			
				
				for ii in range(dim):
					for jj in range(dim):
						self.grid[ii][jj]=abs(self.grid[ii][jj])
						
				self.history.append([copy(self.grid),copy(self.markup)])
					
				place(self.grid,i,j,color)
				self.grid[i][j]=color
					
				self.markup=[["" for row in range(dim)] for col in range(dim)]
				self.markup[i][j]=0
				
				self.network=[[0 for row in range(dim)] for col in range(dim)]
				self.links=[0]*2*dim*dim
				self.goban.display(self.grid,self.markup,self.network,self.links)
				self.next_color=3-color
				self.frame=0
			elif self.grid[i][j] in (1,2):
				#there is a stone, so we mark it (and it's group) as dead
				print "dead group"
				mark_dead_group(self.grid,i,j)
				self.links=[0]*2*dim*dim
				self.network=[[0 for row in range(dim)] for col in range(dim)]
				self.goban.display(self.grid,self.markup,self.network,self.links)
			elif self.grid[i][j] in (-1,-2):
				#there is a (dead) stone, so we mark it (and it's group) as (un)dead
				print "undead group"
				mark_dead_group(self.grid,i,j)
				self.links=[0]*2*dim*dim
				self.network=[[0 for row in range(dim)] for col in range(dim)]
				self.goban.display(self.grid,self.markup,self.network,self.links)

	def color_map(self):
		self.calculate_color(self)
		self.frame+=1
		
	def initialize(self):
		
		self

		
		sgf=self.sgf
		komi=self.sgf.get_komi()
		gameroot=self.sgf.get_root()
		
		self.popup=Toplevel()
		popup=self.popup
		
		dim=self.dim
		move=self.move
		
		popup.configure(background=bg)
		self.locked=False
		panel=Frame(popup)
		panel.configure(background=bg)
		
		#Button(panel, text='undo',command=lambda :click_on_undo(self)).grid(column=0,row=1)
		Button(panel, text='undo',command=self.undo).grid(column=0,row=1)
		Button(panel, text=' Color ',command=self.color_map).grid(column=0,row=2)
		#Button(panel, text='Cluster').grid(column=0,row=3)
		#Button(panel, text='Shadow ').grid(column=0,row=4)
		Button(panel, text='Export',command=self.save_as_ps).grid(column=0,row=5)
		
		panel.grid(column=0,row=1,sticky=N)
		
		goban3 = Goban(dim,master=popup, width=10, height=10,bg=bg,bd=0, borderwidth=0)
		goban3.space=self.goban_size/(dim+1+1)
		goban3.grid(column=1,row=1)
		
		
		
		grid3=[[0 for row in range(dim)] for col in range(dim)]
		markup3=[["" for row in range(dim)] for col in range(dim)]
		network3=[[0 for row in range(dim)] for col in range(dim)]
		links3=[0]*2*dim*dim
		
		print "========================"
		print "opening move",move
		

			
		
		board, _ = sgf_moves.get_setup_and_moves(self.sgf)
		for colour, move0 in board.list_occupied_points():
			if move0 is None:
				continue
			row, col = move0
			if colour=='b':
				place(grid3,row,col,1)
			else:
				place(grid3,row,col,2)

				
		m=0
		for m in range(1,move):
			one_move=get_node(gameroot,m)
			#if one_move==False:
			#	print "(0)leaving because one_move==False"
			#	return
			if one_move!=False:
				ij=one_move.get_move()[1]
				
				print ij
				
				if one_move.get_move()[0]=='b':
					color=1
				else:
					color=2
						
				if ij==None:
					print "(0)skipping because ij==None",ij
					continue

				i,j=ij
				place(grid3,i,j,color)
		try:
			if m>0:
				markup3[i][j]=0
		except:
			print "No move on goban?"
		try:
			if get_node(gameroot,move).get_move()[0].lower()=="w":
				self.next_color=2
			else:
				self.next_color=1
		except:
			print "error when trying to figure out next color to play, so black is selected"
			self.next_color=1
		goban3.display(grid3,markup3,network3,links3)
		
		self.goban=goban3
		self.grid=grid3
		self.markup=markup3
		self.network=network3
		self.links=links3
		
		popup.protocol("WM_DELETE_WINDOW", self.close)
		goban3.bind("<Button-1>",self.click)
		goban3.bind("<Button-2>",self.undo)
		goban3.bind("<Button-3>",lambda event: click_on_undo(popup))
		
		self.history=[]

	def save_as_ps(self):
		filename = tkFileDialog.asksaveasfilename(parent=self.parent,title='Choose a filename',filetypes = [('Postscript', '.ps')],initialfile=("%03d"%self.frame)+'.ps') 
		self.goban.postscript(file=filename, colormode='color')
		pass


def p2l(i,j,u,v,dim):
	if i==u:
		k=0
	else:
		k=1

	return dim*min([i,j],[u,v])[0]+min([i,j],[u,v])[1]+k*dim*dim


	

class DualView(Frame):
	def __init__(self,parent,filename,goban_size=200):
		#Tk.__init__(self,parent)
		
		Frame.__init__(self,parent)
		
		self.parent=parent
		self.filename=filename
		self.goban_size=goban_size
		
		self.calculate_color=common_draw_color
		self.initialize()
		
		self.current_move=1
		self.display_move(self.current_move)
		
		#self.after(100,self.center)
		
		self.pressed=0

		self.disable_color=False
		self.disable_cluster=False
		self.disable_shadow=False
		
		self.frame=0
		
	def color_map(self):
		common_draw_color(self)
		self.frame+=1
		
	def close_app(self):
		for popup in self.all_popups[:]:
			popup.close()

		self.destroy()
		self.parent.destroy()

	
	def prev_10_move(self,event=None):
		self.current_move=max(1,self.current_move-10)
		self.pressed=time.time()
		pf=partial(self.goto_move,move_number=self.current_move,pressed=self.pressed)
		self.parent.after(0,lambda: pf())

	def prev_move(self,event=None):
		if self.current_move>1:
			self.pressed=time.time()
			self.current_move-=1
			pf=partial(self.goto_move,move_number=self.current_move,pressed=self.pressed)
			self.parent.after(0,lambda: pf())
	
	def next_10_move(self,event=None):
		self.current_move=min(get_node_number(self.gameroot),self.current_move+10)
		self.pressed=time.time()
		pf=partial(self.goto_move,move_number=self.current_move,pressed=self.pressed)
		self.parent.after(0,lambda: pf())
	
	def next_move(self,event=None):
		if self.current_move<get_node_number(self.gameroot):
			self.pressed=time.time()
			self.current_move+=1
			pf=partial(self.goto_move,move_number=self.current_move,pressed=self.pressed)
			self.parent.after(0,lambda: pf())


	def goto_move(self,move_number,pressed):
		self.move_number.config(text=str(move_number)+'/'+str(get_node_number(self.gameroot)))
		if self.pressed==pressed:
			self.display_move(self.current_move)
			


	def display_move(self,move=1):
		self.frame=0
		dim=self.dim
		goban=self.goban

		self.move_number.config(text=str(move)+'/'+str(get_node_number(self.gameroot)))
		print "========================"
		print "displaying move",move
		grid=[[0 for row in range(dim)] for col in range(dim)]
		markup=[["" for row in range(dim)] for col in range(dim)]
		network=[[0 for row in range(dim)] for col in range(dim)]
		links=[0]*2*dim*dim
		
		board, _ = sgf_moves.get_setup_and_moves(self.sgf)

		for colour, move0 in board.list_occupied_points():
			if move0 is None:
				continue
			row, col = move0
			if colour=='b':
				place(grid,row,col,1)
			else:
				place(grid,row,col,2)

		
		m=0
		for m in range(1,move+1):
			one_move=get_node(self.gameroot,m)
			#if one_move==False:
			#	print "(0)leaving because one_move==False"
			#	return
			
			if one_move!=False:
				ij=one_move.get_move()[1]
				
				if ij==None:
					print "(0)skipping because ij==None",ij
					continue

				
				if one_move.get_move()[0]=='b':color=1
				else:color=2
				i,j=ij
				place(grid,i,j,color)

			
				if len(one_move)==0:
					print "(0)leaving because len(one_move)==0"
					goban.display(grid,markup,network,links)
					self.grid=grid
					self.markup=markup
					self.network=network
					return
		
		
		
		#indicating last play with delta
		try:
			if m>0:
				place(grid,i,j,color)
				markup[i][j]=0
		except:
			print "no move on goban?"
		goban.display(grid,markup,network,links)
		self.grid=grid
		self.markup=markup
		self.network=network
		self.links=links

	def open_move(self):
		print "Opening move",self.current_move
		new_popup=OpenMove(self,self.current_move+1,self.dim,self.sgf,self.goban_size)
		
		self.all_popups.append(new_popup)
		
	def initialize(self):
				
		txt = open(self.filename)
		self.sgf = sgf.Sgf_game.from_string(txt.read())
		txt.close()
		
		self.dim=self.sgf.get_size()
		self.komi=self.sgf.get_komi()
		
		print "boardsize:",self.dim
		#goban.dim=size
		
		#goban.prepare_mesh()
		self.gameroot=self.sgf.get_root()
		

		self.parent.title('GoReviewPartner')
		self.parent.protocol("WM_DELETE_WINDOW", self.close_app)
		
		
		self.all_popups=[]
		
		self.configure(background=bg)
		
		Label(self,text='   ',background=bg).grid(column=0,row=0)
		
		buttons_bar=Frame(self,background=bg)
		buttons_bar.grid(column=1,row=1,columnspan=3)
		
		Button(buttons_bar, text=' << ',command=self.prev_10_move).grid(column=9,row=1)
		Button(buttons_bar, text='prev',command=self.prev_move).grid(column=10,row=1)
		Label(buttons_bar,text='          ',background=bg).grid(column=19,row=1)
		
		Button(buttons_bar, text='open',command=self.open_move).grid(column=20,row=1)
		
		Label(buttons_bar,text='          ',background=bg).grid(column=29,row=1)
		Button(buttons_bar, text='next',command=self.next_move).grid(column=30,row=1)
		Button(buttons_bar, text=' >> ',command=self.next_10_move).grid(column=31,row=1)
		
		self.move_number=Label(buttons_bar,text='   ',background=bg)
		self.move_number.grid(column=20,row=3)
		
		Button(buttons_bar, text=' Color ',command=self.color_map).grid(column=19,row=4)
		#Button(buttons_bar, text='Cluster').grid(column=20,row=4)
		#Button(buttons_bar, text='Shadow ').grid(column=21,row=4)
		
		Button(buttons_bar, text='Export',command=self.save_as_ps).grid(column=21,row=4)
		
		
		self.parent.bind('<Left>', self.prev_move)
		self.parent.bind('<Right>', self.next_move)

		#Label(app,background=bg).grid(column=1,row=2)

		row=10
		Label(self,background=bg).grid(column=1,row=row-1)

		self.goban = Goban(self.dim,master=self, width=10, height=10,bg=bg,bd=0, borderwidth=0)
		
		self.goban.grid(column=1,row=row)
		Label(self, text='            ',background=bg).grid(column=2,row=row)

		self.goban.space=self.goban_size/(self.dim+1+1)

		Label(self,text='   ',background=bg).grid(column=4,row=row+1)
		
		self.goban.bind("<Button-1>",self.click)


	def click(self,event):
		dim=self.dim
		print "dim:::",dim
		#add/remove black stone
		#check pointer location
		i,j=self.goban.xy2ij(event.x,event.y)
		if 0 <= i <= dim-1 and 0 <= j <= dim-1:
			#inside the grid
			#what is under the pointer ?
			
			if self.grid[i][j] in (1,2):
				#there is a stone, so we mark it (and it's group) as dead
				print "dead group"
				mark_dead_group(self.grid,i,j)
				self.links=[0]*2*dim*dim
				self.network=[[0 for row in range(dim)] for col in range(dim)]
				self.goban.display(self.grid,self.markup,self.network,self.links)
			elif self.grid[i][j] in (-1,-2):
				#there is a (dead) stone, so we mark it (and it's group) as (un)dead
				print "undead group"
				mark_dead_group(self.grid,i,j)
				self.links=[0]*2*dim*dim
				self.network=[[0 for row in range(dim)] for col in range(dim)]
				self.goban.display(self.grid,self.markup,self.network,self.links)


	def save_as_ps(self):
		filename = tkFileDialog.asksaveasfilename(parent=self.parent,title='Choose a filename',filetypes = [('Postscript', '.ps')],initialfile=("%03d"%self.frame)+'.ps') 
		self.goban.postscript(file=filename, colormode='color')
		pass



if __name__ == "__main__":

	if len(sys.argv)==1:
		temp_root = Tk()
		filename = tkFileDialog.askopenfilename(parent=temp_root,title='Choose a file',filetypes = [('sgf file', '.sgf')])
		temp_root.destroy()
		print filename

		if not filename:
			sys.exit()
	else:
		filename=sys.argv[1]
	
	top = Tk()
	
	display_factor=.5
	
	screen_width = top.winfo_screenwidth()
	screen_height = top.winfo_screenheight()
	
	width=int(display_factor*screen_width)
	height=int(display_factor*screen_height)

	DualView(top,filename,min(width,height)).pack(fill=BOTH,expand=1)
	top.mainloop()

	
	
