import cv2
import numpy as np
import mss

# top_left = [x, y]
# bottom_right = [x, y]
# screenshot( [100,200], [200,300] )
def screenshot(top_left, bottom_right):
    # extract coordinates
    left, top = top_left
    right, bottom = bottom_right
    
    # calculate width and height based on coordinates
    width = right - left
    height = bottom - top

    with mss.mss() as sct:
        # region to capture
        region = {
            "top": top,
            "left": left,
            "width": width,
            "height": height
        }
        
        # actually captures
        screenshot = sct.grab(region)
        
        # transforms from RGBA to BGR, because OpenCV works with BGR by default
        img = np.array(screenshot)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        return img_bgr

# screenshot is passed directly, base_image_path is the file path to the template
# TODO(adrian): make this deal with scaling issues. base images are on 1920x1080, but screenshots can be on different resolutions and match should account for that
def find_image_in_screenshot(screenshot, base_image_path, threshold=0.85):    
    # load img to be found
    base_image = cv2.imread(base_image_path)

    # grayscale both
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)  # screenshot is in RGB
    gray_base_image = cv2.cvtColor(base_image, cv2.COLOR_BGR2GRAY)  # base image is loaded in BGR by default

    # get dimensions of base img
    base_height, base_width = gray_base_image.shape

    # actually match with cv2
    result = cv2.matchTemplate(gray_screenshot, gray_base_image, cv2.TM_CCOEFF_NORMED)

    # get the best location that matched
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # highest confidence area
    top_left = max_loc
    bottom_right = (top_left[0] + base_width, top_left[1] + base_height)
    confidence = max_val
    coordinates = {
        'top_left': top_left,
        'bottom_right': bottom_right
    }

    # check if its above threshold
    if max_val >= threshold:
        return {
            'found': True,
            'confidence': confidence,
            'confidence_threshold': threshold,
            'coordinates': coordinates,
            'screenshot': screenshot
        }
    else:
        return {
            'found': False,
            'confidence': confidence,
            'confidence_threshold': threshold,
            'coordinates': coordinates,
            'screenshot': screenshot
        }
        
# function to display the match on the screenshot
def display_match_from_screenshot(result):
    screenshot = result['screenshot']
    top_left = result['coordinates']['top_left']
    bottom_right = result['coordinates']['bottom_right']
    
    # Draw a rectangle around the found template
    cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)  # Green rectangle with 2px thickness
    
    # Display the confidence level
    cv2.putText(screenshot, f"Confidence: {result['confidence']:.2f}", (top_left[0], top_left[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Show the result
    cv2.imshow("Matched Image", screenshot)
    cv2.waitKey(0)  # Wait for a key press
    cv2.destroyAllWindows()

# example usage: screenshot with hardcoded hp2 template
def find_hp2_inventory_icon_in_screenshot(screenshot):
    HEAVENLY_POTION = "src\\images\\match\\template_heavenly_potion_ii.png"
    THRESHOLD = 0.95 # we dont want any mishaps
    return find_image_in_screenshot(screenshot, HEAVENLY_POTION, THRESHOLD)

# example usage: screenshot with hardcoded strange controller template
def find_sc_inventory_icon_in_screenshot(screenshot):
    STRANGE_CONTROLLER = "src\\images\\match\\template_strange_controller.png"
    THRESHOLD = 0.95 # we dont want any mishaps
    return find_image_in_screenshot(screenshot, STRANGE_CONTROLLER, THRESHOLD)


sc = screenshot((0,0), (1920,1080)) # screenshot that part of the screen
result = find_hp2_inventory_icon_in_screenshot(sc) # reads that screenshot if theres anything that matches with our hp2 template. default confidence of 0.95
# display_match_from_screenshot(result) # displays the match on screen
if result['found']:
    display_match_from_screenshot(result)
else:
    print("No match found, wont display anything. (could display for debug purposes but img match returned found=False)")
print({key: value for key, value in result.items() if key != 'screenshot'}) # print the result, removing screenshot number arrays