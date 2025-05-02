from psychopy import core, visual, event, data
from PIL import Image
import random
import copy

def load_images(ref=None):
    '''
    returns a dictionary of the needed images for our experiment
    '''
    bg = [None]*8
    for i in range(8):
        s = str(i)
        bg[i] = Image.open('backgrounds/0'+s+'.jpg')
        if ref!=None:
            bg[i] = resize_image(bg[i], ref)
    obj = Image.open('beerus.png')
    cross = Image.open('arrows&cross/cross.png')
    left = Image.open('arrows&cross/left.png')
    right = Image.open('arrows&cross/right.png')
    up = Image.open('arrows&cross/up.png')
    down = Image.open('arrows&cross/down.png')
    # define a dictionary to acess images
    loaded_images = {"object":obj, "cross":cross, "left":left, "right":right, "up":up, "down":down}
    if ref!=None:
        for key in loaded_images.keys():
            loaded_images[key] = resize_image(loaded_images[key], ref)
    loaded_images["backgrounds"] = bg
    
    return loaded_images

def resize_image(img, ref):
    '''
    resizes image img to fit the resolution of the window
    '''
    img_w, img_h = img.size
    new_w = int(ref)
    new_h = int(new_w * img_h/img_w)
    return img.resize((new_w, new_h))
    
    
def place_obj (obj, bg, location="anywhere", seed=None, resize_percent=0.1):
    ''' This fucntion resizes an object image and places it in a random location (see location arg) on a background image.
        This function assumes that the images are read by Image.open() method from the pillow library
        arguments:
            obj : image of the object to be resized and placed on the background image.
            bg : background image.
            location: there are 5 possible choices here:
                "down_right" for random placement in the down_right quarter of the image.
                "down_left" for random placement in the down_left quarter of the image.
                "up_right" for random placement in the up_right quarter of the image.
                "up_left" for random placement in the up_left quarter of the image.
                "anywhere" for random placement anywhere on the image.
            seed: use in case you want to set a seed for randomization.
            resize_percent: how much should the object image be resized relative to the background image; defualt is 0.1 which hides the object; usee 0.2 to make when testing to make it easier to find the object.
        returns:
            bg: the background image with the object placed on int
            (x,y): the coordinates of where the obbject is placed
            '''
    #get background width 'bg_w', height 'bg_h' and center coordinates 'bg_cx' and 'bg_cy' 
    bg_w, bg_h = bg.size
    bg_cx, bg_cy = bg_w//2, bg_h//2
    orig_w, orig_h = obj.size
    #get object width and height 'obj_w' and 'obj_h' respectively, and then resizing it. 
    percent = resize_percent
    obj_w = int(bg_w * percent)
    obj_h = int(obj_w * orig_h / orig_w) # maintain aspect ratio
    #Resize explicitly (returns a new Image) :contentReference[oaicite:1]{index=1}
    obj_resized = obj.resize((obj_w, obj_h))

    # defining our direction (possible locations) dictionary
    # the main idea heree is that images usualy start indexing at (0,0) on the left upper corner of the images
    # so our full range is from 0 to bg_w for the x and from 0 to bg_h for the y
    # we will subtract the object width and height from bg_w and bg_h respectively to ensure that the object is not placed outside the image
    # each direction indicates a quarter of the image and thus we can constrain our random selection of the location to a specific quarter by introducing the center coordinates
    # i.e. left: x goes from the center to the end, while right: goes from zero to the center
    W, H = (bg_w - obj_w, bg_h - obj_h)
    directions = {  "down_right"   : [[bg_cx, W], [bg_cy, H]],
                    "down_left"    : [[0, W - bg_cx], [bg_cy, H]],
                    "up_right"     : [[bg_cx, W], [0, H - bg_cy]],
                    "up_left"      : [[0, W - bg_cx], [0, H - bg_cy]],
                    "anywhere"     : [[0, W], [0, H]]
                    }
    loc = location
    if seed: random.seed(seed)
    x = random.randint(directions[loc][0][0], directions[loc][0][1]) 
    y = random.randint(directions[loc][1][0], directions[loc][1][1])
    new_bg = copy.deepcopy(bg)
    new_bg.paste(obj_resized, (x, y), mask=obj_resized)
    #bg.save('trial_image.png')
    return new_bg, (x,y)

def test_place_obj (pic_id=0, seed=None, percent=0.1):
    win_x, win_y = 1200, 800
    win = visual.Window([win_x, win_y], color='white')
    # load images
    loaded_imgs = load_images(win_x)
    obj = loaded_imgs["object"]
    bg = loaded_imgs["backgrounds"][pic_id]
    directions = ["down_right","down_left", "up_right", "up_left", "anywhere"]
    for i,s in enumerate(directions):
        img, coordinates = place_obj(obj, bg, location=s ,seed=seed, resize_percent=percent)
        print(coordinates)
        create_task_comp(win, img, Mode='keypress')
    win.close()
    core.quit()

def create_task_comp (window, img, Mode="time",time=0.1):
    '''
    one task consists of 4 main components: 1.fixation cross -> 2. leff/right arrows -> 3. up/down arrows -> 4. background with object to find placed accordingly
    this function helps with creating one specific component (slide)
    args:
        window: visual.Window object
        img: image object to be presented
        Keypress: set to True to wait for a keypress instead of waiting for the specified time
        time: seconds to wait while presenting the component
    '''
    
    # Define timage object
    image = visual.ImageStim(
        window,
        image= img, 
        pos=(0, 0),
    )
    # Draw the arrow image and flip the window
    image.draw()
    window.flip()
    # Wait for a key press/or t seconds to close the window
    if Mode=='keypress':
        event.waitKeys(maxWait=30, keyList='space')
    elif Mode=='time':
        core.wait(time)
    
    
def test_images():
    '''function to test image loading and window preview'''
    # Create a window based on preset pixel width and height.
    # A further improvement is to capture the hosting device's monitor resolution (in case of online; captur browser's resolution).
    win_x, win_y = 1200, 800
    win = visual.Window([win_x, win_y], color='white')
    # load images
    loaded_imgs = load_images(win_x)
    # create a simple task to test the follow of the experiment
    # 1. preseent all backgrounds and switch using keypress
    for i in range(8):
        create_task_comp(win, loaded_imgs["backgrounds"][i], Mode='keypress')
    # 2. present thee rest of the images with time interval between them; try different values
    create_task_comp(win, loaded_imgs["object"], time=3)
    create_task_comp(win, loaded_imgs["cross"], time=0.5)
    create_task_comp(win, loaded_imgs["left"], time=0.1)
    create_task_comp(win, loaded_imgs["right"], time=0.1)
    create_task_comp(win, loaded_imgs["up"], time=0.1)
    create_task_comp(win, loaded_imgs["down"], time=0.1)
    
    win.close()
    core.quit()
    
def task_design(seed=None):
    '''
    This function designs a task
    A task consists of a cross for 0.5 seconds, then a combination of right/left then up/down primes for 0.1 seconds, then the image with the object placed according to the prime whether it is congruent or incongruent
    Congruent means the object is placed in complete accordence to the primes
    Incongruent means the oobject is place in complete accordence to the opposits of the primes (up becomes down, right becomes left, and vice versa)
    args:
        seed: controls the random generator (used for testing)
    returns:
        returns bg_indx, a tuple of chosen primes and a string for the location of the object dependeg if it is congruent or not
    '''
    if seed!=None: random.seed(seed)
    # randomly select a background
    bg_idx = random.randint(0,7)
    # randomly select a direction
    primes = [("down", "right"),("down", "left"), ("up", "left"), ("up", "right")]
    primes_idx = random.randint(0,3)
    # randomly select congruencey
    iscong = bool(random.randint(0,1))
    if iscong:
        location = primes[primes_idx][0] + "_" + primes[primes_idx][1]
    else:
        location = primes[primes_idx+2][0] + "_" + primes[primes_idx+2][1]
    return bg_idx, primes[primes_idx], location
    

def main(num_tasks=10):
    win_x, win_y = 1440, 900
    win = visual.Window([win_x, win_y], color='black')
    # load images
    loaded_imgs = load_images(win_x)
    obj = loaded_imgs["object"]
    cross = loaded_imgs["cross"]
    #Welcome message
    Welcome = '''
    Welcome to the priming task!
    
    You are about to be presented with an object of which you need too memorize.
    
    The object will be hidden in a series of images and your task is to find the object.
    
    Each image will be presented for 30 seconds, if you find the object during that time frame press the SPACE bar key.
    
    If you did not find the object do not worry about it.
    
    Between each task you will be presented with a cross that you need to focus your gaze on.
    
    Thank you very much for participating. Enjoy!
    
    Press the SPACE bar key to continue.
    '''
    instructions = visual.TextStim(win, color='white', text=Welcome, units='pix', height=25)
    instructions.draw()
    win.flip()
    event.waitKeys(keyList='space')
    # another message
    object_view = '''Press SPACE to view the object and then press SPACE again once you are ready to start'''
    instructions = visual.TextStim(win, color='white', text=object_view, units='pix', height=25)
    instructions.draw()
    win.flip()
    event.waitKeys(keyList='space')
    # preview object
    image = visual.ImageStim(win, image=obj, pos=(0, 0), size=(0.6, 0.8))
    image.draw()
    win.flip()
    event.waitKeys(keyList='space')
    
    count = 0
    for n in range(num_tasks):
        # randomise design and extract chosen images
        bg_idx, primes, location = task_design()
        bg = loaded_imgs['backgrounds'][bg_idx]
        LR = loaded_imgs[primes[0]]
        UD = loaded_imgs[primes[1]]
        bg_obj = place_obj(obj, bg, location=loc)
        
        # present each image accordingly
        create_task_comp(win, cross, Mode="time", time=0.5)
        create_task_comp(win, LR, Mode="time", time=0.1)
        create_task_comp(win, UD, Mode="time", time=0.1)
        create_task_comp(win, bg_obj, Mode="keypress")
        
        #count+1 if space is pressed
        if event.getKeys(): count+=1
    print(count)
        
        
if __name__ == "__main__":
    ###### a solution I found online for the following warning ###############################
    ###### WARNING: Secure coding is not enabled for restorable state! #######################
    ###### Enable secure coding by implementing NSApplicationDelegate. #######################
    ###### applicationSupportsSecureRestorableState: and returning YES.#######################
    ###### unless it gives you thee same error you do not have to uncommeent the following. ##
    import os
    import sys
    # Redirect stderr to /dev/null to suppress macOS specific warnings
    sys.stderr = open(os.devnull, 'w')
    ############################################################################################
    from psychopy import monitors
    #monitors.Monitor_loadAll()
    #mon.save()
    
    
    main()
    
    
    ###uncomment to test random placement of object; choose a number from 0 to 7 to test different backgrounds###
    #test_place_obj (pic_id=6, seed=None, percent=0.08)
    ###uncomment to test images###
    #test_images()
