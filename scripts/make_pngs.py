from PIL import Image

img = Image.open(r'c:\Users\mguitter\Documents\NW kids wytop\img\europe.png')
print('Source size:', img.size)

# Southern Europe PNG – canvas region [0-700] x [150-616]
south = img.crop((180, 273, 1455, 1093))  # 1275x820
south = south.resize((2000, 1286), Image.LANCZOS)
south.save(r'c:\Users\mguitter\Documents\NW kids wytop\img\europe_south.png')
print('europe_south.png saved:', south.size)

# Scandinavia PNG – canvas region [0-600] x [0-400]
scand = img.crop((180, 0, 1273, 728))  # 1093x728
scand = scand.resize((2000, 1332), Image.LANCZOS)
scand.save(r'c:\Users\mguitter\Documents\NW kids wytop\img\scandinavia.png')
print('scandinavia.png saved:', scand.size)
