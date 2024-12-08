# import screenutils
from src.utils.screenutils import ScreenUtils

su = ScreenUtils()




# STORAGE MENU 1920x1080
# top = 200
# left = 260
# width = 1440-480
# height = 800-260

top = 350
left = 0
width = 100
height = 350

ss = su.screenshot(left, top, width, height)
print('CLEAN SHOW')
ss.show()
print('TEXTED SHOW')
ss.show(data='test')
# ss.show()
res = ss.find_image(template_path=r"C:\Users\adriankubinyete\Desktop\coding\srbg-python\src\utils\collection.png", threshold=0.8)
print('SHOW WITH FIND_IMAGE RESULT')
print('RESULT: ', res)
ss.show(data=res)


HEAVENLY_POTION=(255,152,220)
OBLIVION_POTION=(119,64,214)
ITEM_TO_SEARCH=HEAVENLY_POTION







# ss.colorCount(ITEM_TO_SEARCH,highlight_color=(255,255,255),show=True)
# ss.findHighestColorDensity(ITEM_TO_SEARCH,show=True)

# print(ss.colorCount(((255,152,220))))
# val = int(ss.colorCount((255,152,220)))
# ss.show(data=val, title="Color count")

# result = ss.read()

# print(result)