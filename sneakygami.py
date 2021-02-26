import numpy as np
from tkinter import *
from threading import *
import time
import random


#Var
width=1240
height=720

forms_size = 32

start_length = 6
gamespeed = 8

min_mouth_number = 2
popping_rate = 10
unpopping_rate = popping_rate*1.5

show_tutorial = 0
show_hitbox = 0
toric_space = 1

#Var text
welcome_message = ["Welcome to Sneakygami !","You can left your keyboard at the door","Here you'll only need one pointer and two clicks", "[left-click]"]
starting_congrates = ["Good !", "Let me introduce you the snake", "Or the turtle, or whatever you want"]
starting_instructions = ["Just [left-click] somewhere on the screen to make it follow your [pointer]", "[left-click] again to pause the game"]
starting_encouragements = ["Again to play, and again to pause","And again to    ", "Ok maybe you shall start ?"]
forgotten_message = ["Oh and it's [right-click] to reset ! Kiss"]

losing_list = ["R.I.P"]



'''
             Utils
'''      

#Math functions
def euclid(a,b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
    
def asvec(a,b):
    return np.array((a[0]-b[0], a[1]-b[1]))

def find_coords(form, n=0):
    return canvas.coords(canvas.find_withtag(form)[n])

def pretty_coords(coords):
    return [(coords[n], coords[n+1]) for n in range(0,5,2)]

def farest(clic, coords):
    return sorted(pretty_coords(coords), key = lambda x: euclid(clic, x), reverse=True)

def coord_diff(form1, form2):
    return sum([min(map(lambda x: euclid(a,x), form2)) for a in form1])/100

def toric(a):
    return (a[0]%width, a[1]%height)
    


#Draw Functions    
def line_vec(a, vec, tags=None):
    canvas.create_line(a,tuple(a + vec), tags = tags)
    
def triangle(pos, forms_size, tags=None):
    #Un triangle équilatéral est une jonction symmétrique de deux triangles rectangles tel que a***2 + b**2 = c**2 et 2a = c
    #Donc a**2 + b**2 = 4a**2 donc b**2 = 3a**2
    a = pos[0], (pos[1]+forms_size)
    b = (pos[0]+forms_size/np.sqrt(3)), pos[1]
    c = (pos[0]-forms_size/np.sqrt(3)), pos[1]
    
    canvas.create_polygon(a, b, c, fill ='', outline='#000000', tags=tags)

def snake_tongue(a, vec1, vec2):
    b = tuple(a + 0.2*(vec1-vec2))
    
    canvas.create_line(a,b,tags='tongue')
    line_vec(b, 0.25*vec1, tags='tongue')
    line_vec(b, -0.25*vec2, tags='tongue')
    
def mouth(x, y):
    triangle((x,y), forms_size*1/2, tags='mouth')


#Text functions
def centered(sentences):
    ref = len(sorted(sentences, key=len, reverse=True)[0])
    for n in range(len(sentences)):
        sentences[n] = (int(ref-len(sentences[n]))*' ')+sentences[n]
    return '\n\n'.join(sentences)

def text_in_motion(x, y, sentences, tags, speed=2):
    for sentence in sentences:
            canvas.create_text(x, y, text = sentence, tags = tags)
            time.sleep(speed)
            unpopping(tags, 0)

def defeat():
    defeat_message = random.choice(losing_list)
    canvas.create_text(width/2, height/2, text = defeat_message)



#Game functions
def popping(func):
    x = random.random()*width
    y = random.random()*height

    while len(canvas.find_overlapping(x-forms_size/np.sqrt(3),y+forms_size,x+forms_size/np.sqrt(3),y)) > 0:
        x = random.random()*width
        y = random.random()*height
    
    func(x,y)

def unpopping(tag, keepalive = 1):
    if len(canvas.find_withtag(tag)) > keepalive:
        canvas.delete(canvas.find_withtag(tag)[0])    

'''
            Game
'''

#Main events
'Tutorial'
def intro():
    triangle((width/2, height/2), forms_size, tags = 'snake')
            
    text_in_motion(width/2, height*2/5, sentences=starting_congrates, tags = 'text')
    text_in_motion(width/2, height*3/5, sentences=starting_instructions, tags = 'text', speed=3.5)
    if canvas.play == 0:
        text_in_motion(width/2, height*3/5, sentences=starting_encouragements, tags = 'text', speed=3.5)
    
    while canvas.play == 0:
        pass
    time.sleep(3.5)
    
    canvas.create_text(width/3, height/3, text=forgotten_message, tags = 'text')
    time.sleep(3.5)
    canvas.delete('text')

'Game'
def game():
    iteration = 0
    canvas.create_text(25,15, text='Score :', tags = 'score')
    score = canvas.create_text(50, 15, text='0', tags = 'score')
    
    while canvas.running_game == 1:  
        if canvas.defeat == 0:
            x = canvas.winfo_pointerx()-window.winfo_rootx()
            y = canvas.winfo_pointery()-window.winfo_rooty()
            pointer = (x,y)

            'Tolerance 2'
            if canvas.find_withtag('snake')[-1] in canvas.find_overlapping(x,y,x,y):
                canvas.play = 0
            
            'Core'
            if canvas.play == 1:
                
                iteration += 1
                
                if iteration > 1:
                    canvas.delete('tongue')
                    
                    #Mouth popping
                    if iteration%popping_rate == 0:
                        popping(mouth)
                        
                    if iteration%unpopping_rate == 0:
                        unpopping('mouth', min_mouth_number)

                    #Snake moving
                    'Because of Tolerance 1'                      
                    if 1 > coord_diff([canvas.new, canvas.other1, canvas.other2], pretty_coords(find_coords('snake',-1))) > 0.5:
                        canvas.delete(canvas.find_withtag('snake')[-1])
                    
                    'Classical move'
                    canvas.create_polygon(canvas.other1, canvas.other2, canvas.new, fill ='', outline='#000000', tags = 'snake')
                    unpopping('snake', canvas.snake_length)
                
                

                #Next move
                ordered_points = farest(pointer, find_coords('snake', -1))
                
                'Tolerance 1'
                if ordered_points[0] == canvas.new:
                    ordered_points = farest(pointer, find_coords('snake', -2))
                
                
                far = ordered_points[0]
                canvas.other1 = ordered_points[1]
                canvas.other2 = ordered_points[2]
                
                u = 0.5*asvec(canvas.other1,canvas.other2) + asvec(canvas.other2,far)
                canvas.new = tuple(far + 2*u)
                
                'Toric space (or not)'
                if canvas.new != toric(canvas.new):
                    if toric_space == 1:
                        canvas.create_polygon(canvas.other1, canvas.other2, canvas.new, fill ='', outline='#000000', tags = 'snake')
                        canvas.other1 = tuple(toric(canvas.new) - asvec(canvas.new, canvas.other1))
                        canvas.other2 = tuple(toric(canvas.new) - asvec(canvas.new, canvas.other2))
                        canvas.new = toric(canvas.new)
                        
                    else:
                        canvas.defeat = 1
                        
                
                #Collision
                scope = forms_size/np.sqrt(3)
                hitbox = tuple(canvas.new+asvec(far, canvas.other1))
                    
                hit = canvas.find_overlapping(hitbox[0]-scope, hitbox[1]-scope, hitbox[0]+scope, hitbox[1]+scope)
                
                'Hitbox visual'
                if show_hitbox == 1:
                    canvas.create_rectangle(hitbox[0]-scope, hitbox[1]-scope, hitbox[0]+scope, hitbox[1]+scope, fill ='', outline='#ff0000', tags = 'hitbox')
                    unpopping('hitbox')
                
                if len(hit) > 0:     
                    for item in hit:
                        if 'snake' in canvas.gettags(item):
                            if coord_diff([canvas.new, canvas.other1, canvas.other2], pretty_coords(find_coords(item))) == 0:
                                canvas.defeat = 1
                            
                        elif 'mouth' in canvas.gettags(item):
                            snake_tongue(hitbox, u, asvec(canvas.other1, canvas.other2))
                            canvas.delete(item)
                            canvas.snake_length += 1 
                            canvas.itemconfigure(score, text=canvas.snake_length-start_length)                            
                            
                time.sleep(1/gamespeed)
                    
        else:
            defeat()
            break
                 
    canvas.show_tutorial = 0


'''
            Events
'''              

def game_on(event=None):
    canvas.play = 1

def game_off(event=None):
    canvas.play = 0
    
def game_switch(event=None):
    canvas.play = (canvas.play+1)%2 

def start(event):
    if canvas.find_withtag('snake')==():
        canvas.delete('text')
        
        canvas.play = 0
        canvas.defeat = 0
        canvas.snake_length = start_length

        if canvas.show_tutorial == 1:
            i = Thread(target=intro, daemon=True) 
            i.start()
        
        else:
            triangle((event.x, event.y), forms_size, tags = 'snake')
        
        canvas.new = None
        canvas.running_game = 1
        
        g = Thread(target=game, daemon=True)
        g.start()

    else:
        game_switch()               

              
def reset(event):
    if canvas.find_withtag('snake')!=():
        canvas.running_game = 0
        canvas.delete(ALL)


'''
            Setup
'''
#Window init
window = Tk()
window.geometry(''.join([str(width),'x', str(height)]))
frame = Frame(window)
frame.pack()

#Background init
canvas = Canvas(frame,bg='#84dba4', width=width, height=height)
canvas.show_tutorial = show_tutorial
canvas.create_text(width/2, height/3, text = centered(welcome_message), tags = 'text')

#Commands
'Pause'
#Can pause with lef-click while game is running
# window.bind("<space>", game_switch)

'Start'
canvas.bind("<Button-1>", start)

'Reset'
canvas.bind("<Button-3>", reset)


#Packing
canvas.pack(expand = True, fill = BOTH)

#Launching
window.title("Sneakygami")
window.mainloop()



