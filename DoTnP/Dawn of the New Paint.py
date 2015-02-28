from pygame import *
from random import *
from math import *
from colours import *
import time
from glob import *

"""
Python: Version 2.7.2
The following is a paint program made by Shiyang Han or Sean.
This is a graphics program that allows one to design and draw, then save
a picture using tools included within. It utilizes layers to a decent extent.
All tools have been customized to work with layers."""

font.init()
comicFont = font.SysFont("Comic Sans MS", 16)
screen = display.set_mode((1023,751))
display.set_caption("Dawn of the New Paint~")
tool = "Pencil" #Default
running = True
scroll = Rect(910,200,100,300)
Change_In_Canvas = False
tempText = "Pencil Tool. Click anywhere on the canvas to draw."
back_save = False #Used for icons
mouseicons = [image.load("Images\MouseIcons\\"+str(i)+".png") for i in [0,1,2,3,8,9]]
mousenames = ["Pencil","Eraser","Brush","Spray","Bucket","Dropper"]

count = 0 #The current number of layers made. A default name if we must for now
rects = [[Rect(910,200,100,50),orange,200,"Background"]]

position = 0
selected = 1
colour = (0,0,0)
size = 1

#Preparing background~~~~~
background_image = image.load("Images\Wall_Paper2.png")

scroll_back = image.load("Images\Layers.png")
scroll_back_rect = Surface((100,300))
scroll_back_rect.set_alpha(128)
scroll_back_rect.fill((255,255,255))
background_image.blit(scroll_back_rect,(910,200))

canvas = Surface((800,500))
canvasRect = Rect(100,100,800,500)
canvas.set_alpha(128)
canvas.fill((255,255,255))
background_image.blit(canvas,(100,100))

stamp_menu = image.load("Images\Stamps.png")
stamp_rects = [Rect(301,627,53,100),Rect(353,627,42,100),Rect(394,627,30,100),Rect(423,627,40,100),Rect(462,627,40,100),Rect(501,627,47,100),Rect(547,627,40,100),Rect(586,627,37,100),Rect(622,627,47,100),Rect(668,627,33,100)]
stamp_ids = [str(i) for i in range(10)]
stamp_swap = Rect(382,600,85,20)
stamp_pictures = [image.load("Images\Stamps\\"+str(i)+".png") for i in range(10)]

colour_select = image.load("Images\Palette.png")
colourRect = Rect(300,620,403,119)
background_image.blit(colour_select,(297,600))
colour_swap = Rect(297,600,85,20)

screen.blit(background_image,(0,0))

toolbar = image.load("Images\Tools\Toolbar.png")

#Let's load the toolbar
#Start off with a list of all possible tools
all_toolnames = ["Pencil","Eraser","Brush","Spray","Rect","Ellipse","Line","Polygon","Bucket","Dropper"]
tool_states = ["_Selected","_Hover",""]
tool_images = [[],[],[]]
#Also, we need the rects (or squares in our case lolol)
tool_rects = [Rect(16+36*j,250+34*i,36,36) for i in range(5) for j in range(2)]
for i in range(3):
    for each_tool in all_toolnames:
            #Explanation: each tool has 3 separate "state" pictures. I've loaded them with this
            tool_images[i].append(image.load("Images\Tools\\"+each_tool+tool_states[i]+".png"))


toolbar_pos = [16,250] #The change in x and y when toolbar moves around
dragrect = [0,0,85,20] #Just a list for now. Alterations later on in code
moving_tool = False #Flag for moving toolbar
toolbar_copy = False #Initialize variable

#Text responses go here:
txt_response = ["Pencil Tool. Click anywhere on the canvas to draw.",
                "Eraser Tool. Click anywhere on the canvas to erase.",
                "Brush Tool. Scroll up and down within the canvas to change size.",
                "Spray Can. Change size with the mouse scroll within the canvas.",
                "Rectangle Tool. Drag to draw. Scroll to change Size. Right-Click fill",
                "Ellipse Tool. Drag to draw. Scroll to change Size. Right-Click fill",
                "Line Tool. Drag to draw. Scroll to change Size.",
                "Polygon Tool. Right click to add a node, Left click to set shape, ESCP to quit.",
                "Fill Bucket. Fills an area clicked with a colour.",
                "Dropper. Gets the colour at a selected area on canvas."]
txt_cover = background_image.subsurface(Rect(0,0,1023,100)).copy()
txt_response2 = ["Layers: A green stub means it's transparent."]

#Initialize layers
layers = [[Surface((800,500)),Surface((800,500))]]
layers[-1][0].set_colorkey((0,0,0))
layers[-1][1].set_colorkey((255,255,255))
layers[-1][1].fill((255,255,255))

#Clean canvas to work layers with. Yes, I did play cheap. ^u^
back_fore_default = image.load("Images\clean_canvas.png")

#Deepcopy. Most annoying thing ever
#Explanation: Apparently, copy.deepcopy likes to call pygame.display.quit()
#In other words, all my surfaces become DEAD. -n- So I made this.

def copy_deepcopy(item,_type):
    copied = []
    if _type == "surface":
        for each in item:
            copied.append([])
            for image in each:
                copied[-1].append(image.copy())
    if _type == "rects":
        for each in item:
            copied.append([])
            copied[-1].append(each[0].copy())
            for items in each[1:]:
                copied[-1].append(items)
    return copied

#Forces an undo frame to be saved. Useful for tools like shift layer
def make_undo_frame():
    global Change_In_Canvas,undolist,redolist,layers,rects,selected
    Change_In_Canvas = False
    undolist.append([copy_deepcopy(layers,"surface"),copy_deepcopy(rects,"rects"),selected])
    
    redolist = []

undolist = [[copy_deepcopy(layers,"surface"),copy_deepcopy(rects,"rects"),selected]]
redolist = []

def return_message_action(title,msg):
    arialFont = font.SysFont("Times New Roman", 16)
    back = screen.copy()        # copy screen so we can replace it when done
    draw.rect(screen,lightblue,(300,244,450,200))
    draw.rect(screen,black,(300,244,450,200),1)
    save_txt = arialFont.render(title,True,(0,0,0))
    screen.blit(save_txt,(450,245))
    save_txt = arialFont.render(msg,True,(0,0,0))
    screen.blit(save_txt,(320,270))
    save_txt = arialFont.render("Please click or push any key to continue.",True,(0,0,0))
    screen.blit(save_txt,(320,290))
    waiting = True
    while waiting:
        for e in event.get():
            if e.type == QUIT:
                event.post(e)   # puts QUIT back in event list so main quits
                return ""
            if e.type == KEYDOWN:
                waiting = False
            if e.type == MOUSEBUTTONDOWN:
                waiting = False
        display.flip()
    screen.blit(back,(0,0))
    
def getSave_Load(state): #This is the GetName 2 Example thing. Literally copy pasted
    ans = ""                    # final answer will be built one letter at a time.
    arialFont = font.SysFont("Times New Roman", 16)
    back = screen.copy()        # copy screen so we can replace it when done
    textArea = Rect(412,300,200,25) # make changes here.
    draw.rect(screen,lightblue,(300,244,450,200))
    draw.rect(screen,black,(300,244,450,200),1)
    mouse.set_visible(True)
    if state == "save":
        save_txt = arialFont.render("Save File Window:",True,(0,0,0))
        screen.blit(save_txt,(455,245))
    if state == "open":
        save_txt = arialFont.render("Open File Window:",True,(0,0,0))
        screen.blit(save_txt,(455,245))
    save_txt = arialFont.render("Type the file's name. Don't forget extensions! ESCP to return.",True,(0,0,0))
    screen.blit(save_txt,(320,270))
    pics = glob("*.bmp")+glob("*.jpg")+glob("*.png")
    n = len(pics)
    choiceArea = Rect(textArea.x,textArea.y+textArea.height,textArea.width,n*textArea.height)
    draw.rect(screen,(220,220,220),choiceArea)        # draw the text window and the text.
    draw.rect(screen,(0,0,0),choiceArea,1)        # draw the text window and the text.
    for i in range(n):
        txtPic = arialFont.render(pics[i], True, (0,111,0))   #
        screen.blit(txtPic,(textArea.x+3,textArea.height*i+choiceArea.y))
        
    typing = True
    
    while typing:
        for e in event.get():
            if e.type == QUIT:
                event.post(e)   # puts QUIT back in event list so main quits
                return ""
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    screen.blit(back,(0,0))
                    return ""
                if e.key == K_BACKSPACE:    # remove last letter
                    if len(ans)>0:
                        ans = ans[:-1]
                elif e.key == K_KP_ENTER or e.key == K_RETURN : 
                    typing = False
                elif e.key < 256:
                    if len(ans) < 16:
                        ans += e.unicode       # add character to ans
                    else:
                        ans = ans[:-1]+e.unicode
                    
        txtPic = arialFont.render(ans, True, (0,0,0))   #
        draw.rect(screen,(220,255,220),textArea)        # draw the text window and the text.
        draw.rect(screen,(0,0,0),textArea,2)            #
        screen.blit(txtPic,(textArea.x+3,textArea.y+2))
        
        display.flip()
        
    screen.blit(back,(0,0))
    if state== "open":
        return ans, pics
    else:
        return ans

#Insert get name function (A bit optimized.)
def getName(rect,texts):
    ans = texts
    if len(texts) == 12:
        ans = ans.replace("...","",-1)
    back = screen.copy()        
    textArea = rect    
    typing = True
    while typing:
        for e in event.get():
            if e.type == QUIT:
                event.post(e)   # puts QUIT back in event list so main quits
                return ""
            if e.type == KEYDOWN:
                if e.key == K_BACKSPACE:    # remove last letter
                    if len(ans)>0:
                        ans = ans[:-1]
                elif e.key == K_KP_ENTER or e.key == K_RETURN : 
                    typing = False
                elif e.key == K_ESCAPE:
                    return ""
                elif e.key < 256:
                    ans += e.unicode       # add character to ans
            if e.type == MOUSEBUTTONDOWN and rect.collidepoint(e.pos) == False and e.button == 1:
                return ""
        txtPic = comicFont.render(ans, False, blue)
        screen.set_clip(scroll) #Note: I've clipped twice to clip the textbox when renaming
        draw.rect(screen,lightblue,rect)
        draw.rect(screen,black,rect,1) #Lets keep the individual layer rect
        screen.set_clip(Rect(915,200,90,300))
        draw.rect(screen,white,(rect[0],rect[1]+25-txtPic.get_height()/2,rect[2],txtPic.get_height()))
        draw.rect(screen,black,(rect[0],rect[1]+25-txtPic.get_height()/2,rect[2],txtPic.get_height()),1)
        screen.blit(txtPic,(960-txtPic.get_width()/2,rect[1]+25-txtPic.get_height()/2))
        screen.set_clip(None)
        screen.blit(scroll_back,(907,185))
        display.flip()
    return ans

def doubleclick():
    global startTime
    #Checks for double clicks based on time of click, pretty self explanatory
    testing = time.clock()-startTime
    if testing < 0.20:
        startTime = time.clock()-0.5
        return True
    else:
        startTime = time.clock()
        return False

#Backfore:
#This is pretty much our major lagg preventer due to the extreme amount of blitting
def create_back_fore(layer_list,currentid):
    background = back_fore_default.copy() #Start with a transparent back
    for each in layer_list[:currentid]: #Let's blit the colour and white
        background.blit(each[0],(0,0)) #Handler for every layer infront of
        background.blit(each[1],(0,0)) #Our current layer to create a fore
    foreground = back_fore_default.copy()
    for each in layer_list[currentid+1:]: #Same thing, but for ever thing
        foreground.blit(each[0],(0,0))     #Behind it.
        foreground.blit(each[1],(0,0))
    return (background,foreground)
    #Other notes: This reduces blitting to 3 layers at a time at most and with
    #Clipping too. Lagg reduced. I win.

backfore = create_back_fore(layers,selected-1)

def refresh_layers(): #Procedure for refreshing layers. Used when order changes
    global layers,selected,backfore
    backfore = create_back_fore(layers,selected-1)
    screen.set_clip(canvasRect)
    screen.blit(background_image, (0,0))
    screen.blit(backfore[0],(100,100))
    screen.blit(layers[selected-1][0],(100,100))
    screen.blit(layers[selected-1][1],(100,100))
    screen.blit(backfore[1],(100,100))
    screen.set_clip(None) 

#Notes: Undo and Redo - 2 lists, we interchange between items
def undo():
    global layers,rects,selected,backfore 
    redolist.append(undolist.pop())
    layers = copy_deepcopy(undolist[-1][0],"surface")
    rects = copy_deepcopy(undolist[-1][1],"rects")
    selected = undolist[-1][2]

def redo():
    global layers,rects,selected,backfore
    undolist.append(redolist.pop())
    layers = copy_deepcopy(undolist[-1][0],"surface")
    rects = copy_deepcopy(undolist[-1][1],"rects")
    selected = undolist[-1][2]

#If the toolbar is moved
def moving_toolbar():
        global toolbar_pos,mx,my,locatex,locatey
        screen.set_clip(Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,289))
        screen.blit(background_image,(0,0))
        screen.blit(backfore[0],(100,100))
        screen.blit(layers[selected-1][0],(100,100))
        screen.blit(layers[selected-1][1],(100,100))
        screen.blit(backfore[1],(100,100))
        screen.set_clip(None)
        toolbar_pos = [mx-locatex,my-locatey]
        #Restrictions so the computer doesn't get angry at me lol. (subsurface out of canvas error)
        if toolbar_pos[0] + 85 > 915:
            toolbar_pos[0] = 915-85
        if toolbar_pos[0] < 10:
            toolbar_pos[0] = 10
        if toolbar_pos[1] < 55:
            toolbar_pos[1] = 55
        if toolbar_pos[1]+289 > 796:
            toolbar_pos[1] = 796-289
        screen.blit(toolbar_copy,(toolbar_pos[0]-8,toolbar_pos[1]-50))

def display_scroll():
    global selected,layers,backfore
    #Display the scrollbar
    screen.set_clip(scroll)
    screen.blit(background_image,(0,0))
    draw.rect(screen,(lightblue),rects[selected-1][0])
    rectName = comicFont.render(rects[selected-1][3], False, blue)
    screen.blit(rectName, (960-rectName.get_width()/2,rects[selected-1][0][1]+25-rectName.get_height()/2))
    for each in rects:
        if rects.index(each) == selected-1: #Continue's if we've already drawn this rect
            draw.rect(screen,black,each[0],1)
            continue
        draw.rect(screen,each[1],each[0])
        if each[0].collidepoint(mx,my) and scroll.collidepoint(mx,my):
            draw.rect(screen,DarkOrange2,each[0])
            #Notes: The mouse only selects what it clicks, not what it "holds down" -> Why I'm using evt
            if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                selected = rects.index(each)+1
                backfore = create_back_fore(layers,selected-1)
                screen.set_clip(canvasRect)
                screen.blit(background_image,(0,0))
                screen.blit(backfore[0],(100,100))
                screen.blit(layers[selected-1][0],(100,100))
                screen.blit(layers[selected-1][1],(100,100))
                screen.blit(backfore[1],(100,100))
        draw.rect(screen,black,each[0],2)
        rectName = comicFont.render(each[3], False, blue)
        screen.blit(rectName, (915+46-rectName.get_width()/2,each[0][1]+5+rectName.get_height()/2))
    screen.set_clip(None)
    screen.blit(scroll_back,(907,185))

def display_tools():
    global toolbar_pos,tool,tempText,colour,stamp_or_colour
    #Toolbar Display~~~
    #Other Notes: A variable to count our loop is needed since
    #I'm working with a grid of tools.
    screen.blit(toolbar,(toolbar_pos[0]-8,toolbar_pos[1]-50))
    toolcount = 0
    if tool == "stamp": #More notes. There IS an exception to stamps
        for i in range(5): #in which case, we just draw the untouched state
            for j in range(2):
                if Rect(tool_rects[toolcount][0]+toolbar_pos[0]-16,tool_rects[toolcount][1]-250+toolbar_pos[1],*tool_rects[toolcount][2:]).collidepoint(mx,my):
                    screen.blit(tool_images[1][toolcount],(j*36+toolbar_pos[0],i*34+toolbar_pos[1]))
                    if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                        tool = all_toolnames[toolcount]
                        tempText = txt_response[all_toolnames.index(tool)]
                        screen.blit(colour_select,(297,600))
                        background_image.blit(colour_select,(297,600))
                        stamp_or_colour = "colour"
                else:
                    screen.blit(tool_images[2][toolcount],(j*36+toolbar_pos[0],i*34+toolbar_pos[1]))
                toolcount+=1
        #Current colour
        draw.rect(screen,colour,(toolbar_pos[0]+10,toolbar_pos[1]+174,49,29))
        draw.rect(screen,black,(toolbar_pos[0]+10,toolbar_pos[1]+174,49,29),1)   
        return
    for i in range(5):
        for j in range(2):
            if all_toolnames.index(tool) == toolcount:
                screen.blit(tool_images[0][toolcount],(j*36+toolbar_pos[0],i*34+toolbar_pos[1]))
                tempText = txt_response[all_toolnames.index(tool)]
            elif Rect(tool_rects[toolcount][0]+toolbar_pos[0]-16,tool_rects[toolcount][1]-250+toolbar_pos[1],*tool_rects[toolcount][2:]).collidepoint(mx,my):
                screen.blit(tool_images[1][toolcount],(j*36+toolbar_pos[0],i*34+toolbar_pos[1]))
                tempText = txt_response[all_toolnames.index(tool)]
                if evt.type == MOUSEBUTTONDOWN and evt.button == 1:
                    tool = all_toolnames[toolcount]
            else:
                screen.blit(tool_images[2][toolcount],(j*36+toolbar_pos[0],i*34+toolbar_pos[1]))
            toolcount+=1
    #Current colour
    draw.rect(screen,colour,(toolbar_pos[0]+10,toolbar_pos[1]+174,49,29))
    draw.rect(screen,black,(toolbar_pos[0]+10,toolbar_pos[1]+174,49,29),1)

def drawz(_type,params):
    #Explanation of code:
    #I've decided to make each drawing of shape their own thing,
    #since I'm drawing onto 3 surfaces at a time. The params variable
    #represents all arguements that would normally go into a draw method
    #Note: If you see a -100, know that it means I'm fixing an offset of surfaces
    if _type == "circle":
        draw.circle(screen,params[0],params[1],params[2],params[3])
        draw.circle(layers[selected-1][1],params[0],(params[1][0]-100,params[1][1]-100),params[2],params[3])
        if params[0] == (255,255,255):
            draw.circle(layers[selected-1][0],params[0],(params[1][0]-100,params[1][1]-100),params[2],params[3])
    elif _type == "line":
        draw.line(screen,params[0],(params[1],params[2]),(params[3],params[4]),params[5])
        draw.line(layers[selected-1][1],params[0],(params[1]-100,params[2]-100),(params[3]-100,params[4]-100),params[5])
        #if params[0] == (255,255,255):
        draw.line(layers[selected-1][0],params[0],(params[1]-100,params[2]-100),(params[3]-100,params[4]-100),params[5])
    elif _type == "dot":
        screen.set_at((params[1],params[2]),params[0])
        layers[selected-1][1].set_at((params[1]-100,params[2]-100),params[0])
        if params[0] == (255,255,255):
            layers[selected-1][0].set_at((params[1]-100,params[2]-100),params[0])
    elif _type == "rect":
        draw.rect(screen,params[0],(params[1],params[2],params[3],params[4]),params[5])
        draw.rect(layers[selected-1][1],params[0],(params[1]-100,params[2]-100,params[3],params[4]),params[5])
        if params[0] == (255,255,255):
            draw.rect(layers[selected-1][0],params[0],(params[1]-100,params[2]-100,params[3],params[4]),params[5])
    elif _type == "ellipse":
        draw.ellipse(screen,params[0],params[1],params[2])
        draw.ellipse(layers[selected-1][1],params[0],[params[1][0]-100]+[params[1][1]-100]+params[1][2:],params[2])
        if params[0] == (255,255,255):
            draw.ellipse(layers[selected-1][0],params[0],[params[1][0]-100]+[params[1][1]-100]+params[1][2:],params[2])
            
def brush_stroke(mx,my,mxn,myn,size): #Brush
    global layers,backfore
    distance = ((mx-mxn)**2+(my-myn)**2)**0.5
    if distance == 0:
        distance = 1
    for i in range(int(distance)+1):
        x = mx+round((mxn-mx)/distance*i) #We draw circles at increments of 1 on
        y = my+round((myn-my)/distance*i) #The distance line
        drawz("circle",(colour,(int(x),int(y)),size,0)) #This is repeated for
    screen.blit(backfore[1],(100,100))     #Eraser
    screen.set_clip(None)

def eraser_stroke(mx,my,mxn,myn,size):
    global layers,backfore
    distance = ((mx-mxn)**2+(my-myn)**2)**0.5
    if distance == 0:
        distance = 1
    for i in range(int(distance)+1):
        x = mx+round((mxn-mx)/distance*i)
        y = my+round((myn-my)/distance*i)
        screen.set_clip((x-size,y-size,size*2,size*2))
        screen.blit(background_image, (0,0))
        screen.blit(backfore[0],(100,100))
        screen.blit(layers[selected-1][0],(100,100))
        screen.blit(layers[selected-1][1],(100,100))
        screen.blit(backfore[1],(100,100))
        screen.set_clip(None)
        draw.circle(layers[selected-1][1],(255,255,255),(int(x)-100,int(y)-100),size)
        draw.circle(layers[selected-1][0],(0,0,0),(int(x)-100,int(y)-100),size)

def spray_stroke(mx,my):
    global layers,backfore
    for i in range(25):
        sprayx = randint(mx-size*2,mx+size*2) #Pick some points
        sprayy = randint(my-size*2,my+size*2)
        if (mx-sprayx)**2 + (my-sprayy)**2 <= (size*2)**2: #If the point
            drawz("dot",(colour,sprayx,sprayy)) #Satisfies equation, draw it
    
def rect_stroke(mx,my,mxn,myn,size):
    if mb[2] == 1:
        size = 0
    global layers,backfore,start_pos
    screen.set_clip(canvasRect)           #Same concept as normally drawing a rect
    screen.blit(background_back[0],(0,0)) #This time, we're dealing with 3
    layers[selected-1][0] = background_back[1].copy() #Surfaces at a time
    layers[selected-1][1] = background_back[2].copy() #Same for line, ellipse
    drawz("rect",(colour,mx,my,mxn,myn,size))
    screen.blit(backfore[0],(100,100))
    screen.blit(layers[selected-1][0],(100,100))
    screen.blit(layers[selected-1][1],(100,100))
    screen.blit(backfore[1],(100,100))

def ellipse_stroke(mx,my,mxn,myn,size):
    if mb[2] == 1:
        size = 0
    global layers,backfore,start_pos
    ellipse_rect = Rect(mx,my,mxn,myn)
    ellipse_rect.normalize() #Cheapest function ever... >__<' fixes all negatives
    if size < min(ellipse_rect[2],ellipse_rect[3])/2: #Only draws if width is less than radius
        screen.set_clip(canvasRect)
        screen.blit(background_back[0],(0,0))
        layers[selected-1][0] = background_back[1].copy()
        layers[selected-1][1] = background_back[2].copy()
        drawz("ellipse",(colour,ellipse_rect,size))
        screen.blit(backfore[0],(100,100))
        screen.blit(layers[selected-1][0],(100,100))
        screen.blit(layers[selected-1][1],(100,100))
        screen.blit(backfore[1],(100,100))

def line_stroke(mx,my,mxn,myn,size):
    global layers,backfore,start_pos
    screen.set_clip(canvasRect)
    screen.blit(background_back[0],(0,0))
    layers[selected-1][0] = background_back[1].copy()
    layers[selected-1][1] = background_back[2].copy()
    drawz("line",(colour,mx,my,mxn,myn,size))
    screen.blit(backfore[0],(100,100))
    screen.blit(layers[selected-1][0],(100,100))
    screen.blit(layers[selected-1][1],(100,100))
    screen.blit(backfore[1],(100,100))

def bucket_fill(mx,my):
    #Alterations:
    #I'll bit the 2 surfaces of a singular layer together and use this
    #As my flood map
    global layers,backfore,colour,selected
    #The line below works because we are comparing white with alpha 255
    #to white with alpha 0 C:<
    flood_back = back_fore_default.copy()
    flood_back.blit(layers[selected-1][0],(0,0))
    flood_back.blit(layers[selected-1][1],(0,0))
    old_colour = flood_back.get_at((mx-100,my-100))
    if (colour[0],colour[1],colour[2],255) != old_colour:
        points=[(mx-100,my-100)]
        while len(points)>0: #Keep going until no more points left -yes, it laggs T.T
            pt=points.pop()
            if canvasRect.collidepoint((pt[0]+100,pt[1]+100)) and flood_back.get_at(pt)==old_colour:
                layers[selected-1][1].set_at(pt,colour)
                if colour == (255,255,255):
                    layers[selected-1][0].set_at(pt,colour)
                flood_back.set_at(pt,colour)
                points+=[(pt[0]+1,pt[1]),(pt[0]-1,pt[1]),(pt[0],pt[1]+1),(pt[0],pt[1]-1)]
    screen.blit(flood_back,(100,100))
    screen.blit(backfore[1],(100,100))

def polygon_stroke(mx,my):
    global colour
    back = screen.copy()
    txtcover = back.subsurface(Rect(0,0,1023,100))
    txtcover.blit(background_image.subsurface(Rect(0,52,1023,21)),(0,52)) #Covers previous xy
    stroke_pattern = [(mx,my)]
    secondary_stroke = [(mx-100,my-100)]
    polygon_ing = True
    quit_polygon = False
    while polygon_ing: #While drawing, get more points at each mouse click
        mx,my = mouse.get_pos()
        for each_event in event.get(): #Until they exit.
            if each_event.type == QUIT:
                polygon_ing = False
                quit_polygon = True
            if each_event.type == MOUSEBUTTONDOWN:
                if each_event.button == 1 and canvasRect.collidepoint(each_event.pos):
                    stroke_pattern.append(each_event.pos)
                    secondary_stroke.append([each_event.pos[0]-100,each_event.pos[1]-100])
                elif each_event.button == 3:
                    polygon_ing = False
            if each_event.type == KEYDOWN:
                if each_event.key == K_ESCAPE:
                    polygon_ing = False
                    quit_polygon = True
        if len(stroke_pattern) > 1:
            draw.lines(screen,colour,False,stroke_pattern,1)
        screen.blit(backfore[1],(100,100))
        if canvasRect.collidepoint(mx,my) and (Rect(toolbar_pos[0]-8-size,toolbar_pos[1]-50-size,85+size*2,289+size*2).collidepoint(mx,my))==False:
            mx_my = comicFont.render("(x: "+str(mx)+", y: "+str(my)+")",True,(255,255,255))
            screen.set_clip(None)
            screen.blit(txtcover,(0,0))
            screen.blit(mx_my,(100,50))
            screen.set_clip(canvasRect)
        display.flip()
    screen.blit(back,(0,0))
    if quit_polygon == False and len(stroke_pattern)>2:
        return [stroke_pattern,secondary_stroke] #Recall secondary is for layers offset
    else: #If we quit without proper use don't draw anything
        return False

def stamper(mx,my):
    global stamp,layers,backfore,start_pos    
    picture = stamp_pictures[int(stamp)].copy()
    if mx == start_pos[0] or my == start_pos[1]:
        return
    angle = -degrees(atan(abs(float(my-start_pos[1])/(mx-start_pos[0]))))
    if mx -start_pos[0] < 0 and my-start_pos[1] > 0: #4 different cases for
        angle = 180-angle #Each quadrant's rotation. We base this off of arctan
    elif mx -start_pos[0] < 0 and my-start_pos[1] < 0:
        angle = 180+angle
    elif mx -start_pos[0] > 0 and my-start_pos[1] < 0:
        angle = 360-angle
    screen.blit(background_back[0],(0,0))
    layers[selected-1][0] = background_back[1].copy()
    layers[selected-1][0].blit(transform.rotate(picture, angle),(start_pos[0]-100-transform.rotate(picture, angle).get_width()/2,start_pos[1]-100-transform.rotate(picture, angle).get_height()/2))
    screen.blit(layers[selected-1][0],(100,100))
    screen.blit(layers[selected-1][1],(100,100))
    layers[selected-1][0].set_colorkey((0,0,0,255))
    screen.blit(backfore[1],(100,100))
    #Other fun notes: Troll factor. I've not included a secondary handler, so that
    #The characters seem to be hiding behind everything except for white
    #lolololol xD
    
startTime = time.clock() #Initialize time count
start_pos = False
stamp_or_colour = "colour"

while running:
    mx_my = False
    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()
    keys = key.get_pressed()
    for evt in event.get():
        if evt.type == QUIT:
            running = False
        if evt.type == MOUSEBUTTONDOWN:
            #Notes: scrolling in the scrollbar and in the canvas do 2 different things, js
            if scroll.collidepoint(mx,my):
                if evt.button == 5 and position > 300-50*len(rects):
                    position -=10
                    for i in range(len(rects)):
                        rects[i][0][1]= rects[i][2]+position
                elif evt.button ==4 and position < 0:
                    position +=10
                    for i in range(len(rects)):
                        rects[i][0][1]=rects[i][2]+position
             #Below, Scrolling changes size. Above, scrolling scrolls layers
            if canvasRect.collidepoint(mx,my):
                if evt.button == 4 and size < 31:
                    size+=1
                elif evt.button ==5 and size  > 1:
                    size-=1
            
            if Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,25).collidepoint(mx,my):
                if evt.button == 1:
                    initialpos = evt.pos
                    #Locate x and y tell us how far our cursor is within the toolbar
                    locatex = initialpos[0]-toolbar_pos[0]
                    locatey = initialpos[1]-toolbar_pos[1]
                    toolbar_copy = screen.subsurface(Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,289)).copy()
                    moving_tool = True
            if (tool in ["Dropper","Marquee"]) == False: #Dropper technically does nothing
                if canvasRect.collidepoint(mx,my) and (Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,289).collidepoint(mx,my))==False:
                    Change_In_Canvas = True
            #Background copy for tools that need it
            if evt.button == 1 and canvasRect.collidepoint(mx,my):
                background_back = [screen.copy(),layers[selected-1][0].copy(),layers[selected-1][1].copy()]
                start_pos = evt.pos
            #Swaping between stamps panel and palette
            if evt.button == 1 and colour_swap.collidepoint(mx,my) and stamp_or_colour == "stamp":
                background_image.blit(colour_select,(297,600))
                screen.blit(colour_select,(297,600))
                stamp_or_colour = "colour"
                tool = "Pencil"
            if evt.button == 1 and stamp_swap.collidepoint(mx,my) and stamp_or_colour == "colour":
                background_image.blit(stamp_menu,(297,600))
                screen.blit(stamp_menu,(297,600))
                stamp_or_colour = "stamp"
                tool =  "stamp"
                stamp = "0"
                draw.rect(screen,(255,0,0),stamp_rects[0],1)
                
        if evt.type == MOUSEBUTTONUP:
            if evt.button == 1 and moving_tool:
                moving_tool = False
                #Let's make an overlay copy to blit at the end of code
                toolbar_copy = screen.subsurface(Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,289)).copy()
            if evt.button == 1 and Change_In_Canvas:
                make_undo_frame()
                start_pos = False
            #^Also acts as a flag to make sure they clicked on the canvas to draw
            
        if evt.type == KEYDOWN:
            #New Layer
            if evt.key == K_n:
                count+=1
                rects.append([Rect(910,rects[-1][0][1]+50,100,50),orange,rects[-1][0][1]+50-position,"Layer "+str(count)])
                #Adds a new layer with black and white handlers
                layers.append([Surface((800,500)),Surface((800,500))])
                layers[-1][0].set_colorkey((0,0,0))
                layers[-1][1].set_colorkey((255,255,255))
                layers[-1][1].fill((255,255,255))
                selected = len(rects)
                backfore = create_back_fore(layers,selected-1)
                
                #More visual appeal. If new layers added exceed scrollbar height, the list is bumped up
                if rects[-1][0][1] > 450:
                    for each in rects:
                        rects[rects.index(each)][0][1]-=50
                    position -= 50
                make_undo_frame()
                
            #Delete Layer
            elif evt.key == K_d and len(rects) >1:
                del(rects[selected-1])
                del(layers[selected-1])
                #After deleting a layer, all the pos of the other rects will be offset
                #This pushes them back 50 (the size of 1 rect)
                for each in rects[selected-1:]:
                    rects[rects.index(each)][0][1]-=50
                    rects[rects.index(each)][2]-=50
                
                #While deleting, if the first rect is above the scrollbar, it pushes the rect back down
                #^ in other words, yes. Visual appeal
                if rects[0][0][1] <200:
                    while rects[0][0][1]+50 >200:
                        for each in rects:
                            rects[rects.index(each)][0][1] -=1
                        position -=1
                    for each in rects:
                        rects[rects.index(each)][0][1]+=50
                    position += 50
                if selected > 1:
                    selected -=1
                refresh_layers()
                make_undo_frame()
                
            elif evt.key == K_o and selected >1: #shift layer up
                layers[selected-1],layers[selected-2] = layers[selected-2],layers[selected-1]
                rects[selected-1][3],rects[selected-2][3] = rects[selected-2][3],rects[selected-1][3]
                selected -=1
                refresh_layers()
                make_undo_frame()
                
            elif evt.key == K_p and selected < len(layers): #shift layer down
                layers[selected],layers[selected-1] = layers[selected-1],layers[selected]
                rects[selected][3],rects[selected-1][3] = rects[selected-1][3],rects[selected][3]
                selected +=1
                refresh_layers()
                make_undo_frame()

            #Undo and redo                
            if evt.key == K_z and (keys[K_RCTRL] or keys[K_LCTRL]):
                if len(undolist) > 1: 
                    undo()
                    refresh_layers()
            elif evt.key == K_y and (keys[K_RCTRL] or keys[K_LCTRL]):
                if len(redolist) > 0:
                    redo()
                    refresh_layers()
            if evt.key == K_s and (keys[K_RCTRL] or keys[K_LCTRL]):
                name = getSave_Load("save")
                if name: #Let's save if there was a name given
                    savefile = back_fore_default.copy()
                    savefile.blit(backfore[0],(0,0))
                    savefile.blit(layers[selected-1][0],(0,0))
                    savefile.blit(layers[selected-1][1],(0,0))
                    savefile.blit(backfore[1],(0,0))
                    image.save(savefile,name)
                    return_message_action("Successful Save!","Your image has been saved.")
                else:
                    return_message_action("Action Cancelled:","Please Enter a File Name")
            if evt.key == K_o and (keys[K_RCTRL] or keys[K_LCTRL]):
                openName = getSave_Load("open")
                if openName: #Clear all layers and rects and start all over
                    if openName[0] in openName[1]:
                        myfile = image.load(openName[0])
                        count = 0
                        rects = [[Rect(910,200,100,50),orange,200,"Background"]]
                        selected = 1
                        layers = [[Surface((800,500)),Surface((800,500))]]
                        layers[-1][0].set_colorkey((0,0,0))
                        layers[-1][1].set_colorkey((255,255,255))
                        layers[-1][1].fill((255,255,255))
                        layers[-1][0].blit(myfile,(0,0))
                        layers[-1][1].blit(myfile,(0,0))
                        create_back_fore(layers,selected-1)
                        refresh_layers()
                        display_scroll()
                        make_undo_frame()
                        return_message_action("Successful Open!","Your image has been loaded.")
                    else: #Gives error message
                        return_message_action("Failed to Open:","This file doesn't exist, or you typed it wrong.")
            #New Screen :D
            if evt.key == K_n and (keys[K_RCTRL] or keys[K_LCTRL]):
                #Notes: Pretty much the exact thing as load cept no blitting images
                #This IS undo-able :D
                count = 0
                rects = [[Rect(910,200,100,50),orange,200,"Background"]]
                selected = 1
                layers = [[Surface((800,500)),Surface((800,500))]]
                layers[-1][0].set_colorkey((0,0,0))
                layers[-1][1].set_colorkey((255,255,255))
                layers[-1][1].fill((255,255,255))
                create_back_fore(layers,selected-1)
                refresh_layers()
                display_scroll()
                make_undo_frame()
        #Renaming a Layer
        for each in rects:
            if rects.index(each) == selected-1:
                if evt.type == MOUSEBUTTONDOWN and evt.button == 1 and each[0].collidepoint(mx,my) and scroll.collidepoint(mx,my):
                    if doubleclick():
                        rename = getName(each[0],each[3])
                        if rename != "":
                            if len(rename) > 9:
                                rename = rename[:9]+"..."
                            rects[rects.index(each)][3] = rename
                else:
                    continue
        #Stamp Selection
        if stamp_or_colour == "stamp":
            for selection in stamp_rects:
                if evt.type == MOUSEBUTTONDOWN and evt.button == 1 and selection.collidepoint(mx,my) and (Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,289).collidepoint(mx,my))==False:
                    screen.blit(stamp_menu,(297,600))
                    draw.rect(screen,(255,0,0),selection,1)
                    tool = "stamp"
                    stamp = stamp_ids[stamp_rects.index(selection)]
#Begin paint~===========================================================================>
#Start Canvas interaction

    if mb[0] == 1:
        if moving_tool:
            moving_toolbar()
        elif start_pos and (canvasRect.collidepoint(mx,my) and (Rect(toolbar_pos[0]-8-size,toolbar_pos[1]-50-size,85+size*2,289+size*2).collidepoint(mx,my))==False or (tool == "Pencil" and (Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,289).collidepoint(mx,my))==False)):
            screen.set_clip(canvasRect)
            mxn,myn = mouse.get_pos()
            if tool == "Pencil":
                drawz("line",(colour,mx,my,mxn,myn,1))
            elif tool == "Eraser":
                eraser_stroke(mx,my,mxn,myn,size)
            elif tool == "Brush":
                brush_stroke(mx,my,mxn,myn,size)
            elif tool == "Spray":
                spray_stroke(mx,my)
            elif tool == "Rect":
                rect_stroke(start_pos[0],start_pos[1],mxn-start_pos[0],myn-start_pos[1],size)
            elif tool == "Ellipse":
                ellipse_stroke(start_pos[0],start_pos[1],mxn-start_pos[0],myn-start_pos[1],size)
            elif tool == "Line":
                line_stroke(start_pos[0],start_pos[1],mxn,myn,size)
            elif tool == "Polygon":
                polystroke = polygon_stroke(mx,my)
                if polystroke:
                    draw.lines(screen,colour,True,polystroke[0],1)
                    draw.lines(layers[selected-1][1],colour,True,polystroke[1],1)
                    if colour == (255,255,255):
                        draw.lines(layers[selected-1][0],colour,True,polystroke[1],1)
                    screen.blit(backfore[1],(100,100))
                    make_undo_frame()
                    #May as well add a frame since program can't detect it at this line
            elif tool == "Bucket":
                txt = comicFont.render("Our heroes are off doing a Katz Guild Quest. Please wait...",True,(255,255,255))
                screen.set_clip(None)
                screen.blit(txt_cover,(0,0))
                screen.blit(txt,(100,70))
                display.flip()
                bucket_fill(mx,my)
            elif tool == "Dropper":
                colour = screen.get_at((mx,my))
            elif tool == "stamp":
                stamper(mx,my)
        if colourRect.collidepoint(mx,my) and (Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,289).collidepoint(mx,my))==False and tool != "stamp":
            colour = screen.get_at((mx,my))
            
    txt = comicFont.render(tempText,True,(255,255,255))
    screen.set_clip(None)
    screen.blit(txt_cover,(0,0))
    size_display = comicFont.render("(Size: "+str(size)+")",True,(255,255,255))
    screen.blit(size_display,(100,30))
    #Mouse position only if inside canvas and not touching toolbar
    if canvasRect.collidepoint(mx,my) and (Rect(toolbar_pos[0]-8-size,toolbar_pos[1]-50-size,85+size*2,289+size*2).collidepoint(mx,my))==False:
        mx_my = comicFont.render("(x: "+str(mx)+", y: "+str(my)+")",True,(255,255,255))
        screen.blit(mx_my,(100,50))
    screen.blit(txt,(100,70))
    display_scroll()
    display_tools()
    back_save = screen.copy()
    if canvasRect.collidepoint(mx,my) and (Rect(toolbar_pos[0]-8,toolbar_pos[1]-50,85,289).collidepoint(mx,my))==False:
        mouse.set_visible(False) #sets to false initially
        if (tool in ["stamp","Ellipse","Rect","Line","Polygon"]) == False:
            if tool == "Brush" or tool == "Eraser": #Brush and eraser directly use size
                draw.circle(screen,(0,0,0),(mx,my),size,1)
            elif tool == "Spray": #Spray is actually size *2
                draw.circle(screen,(0,0,0),(mx,my),size*2,1)
            screen.blit(mouseicons[mousenames.index(tool)],(mx,my-24))
        else: #If we're on a tool without an icon, reshow the mouse
            mouse.set_visible(True)
    else:
        mouse.set_visible(True) #Initial Visible mouse      
    display.flip()
    if back_save:
        screen.blit(back_save,(0,0))
    
quit()
