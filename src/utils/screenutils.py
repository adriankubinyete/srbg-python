
import logging
# screenshot
import cv2
import numpy as np
import mss
# ocr
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(f"srbg.{__name__}")

class Screenshot:
    def __init__(self, image: np.array, region: dict):
        self.image = image
        self.region = region
        
    # HELPER: Prepare for .show as if its a findimage return
    def _prep_image(self, data, text):
        IMAGE_COPY = self.image.copy()
        TEXT_OFFSET = 20  # Espaço para o texto
        TEXT_SIZE=0.8
        TEXT_COLOR = (0, 255, 0)  # Cor do texto
        BOX_COLOR = (0, 255, 0)  # Cor da caixa
        DRAW_TEXT_BACKGROUND=True

        # Quebrar o texto em linhas
        text_lines = text.split('\n')
        
        # Calcular a altura necessária para o texto
        text_height = len(text_lines) * 20  # Aproximadamente 20px por linha (ajustável)
        max_text_width = max([cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, TEXT_SIZE, 1)[0][0] for line in text_lines])

        # Calcular as novas dimensões da imagem se o texto exceder a altura
        new_height = self.image.shape[0]
        new_width = self.image.shape[1]
        
        # Se o texto ultrapassar a altura da imagem
        if (data['coordinates']['y'] + data['coordinates']['height'] + text_height) > new_height:
            new_height = data['coordinates']['y'] + data['coordinates']['height'] + text_height + TEXT_OFFSET

        # Se o texto ultrapassar a largura da imagem
        if (data['coordinates']['x'] + max_text_width) > new_width:
            new_width = data['coordinates']['x'] + max_text_width + 20  # Adicionar um pouco de espaço extra

        # Se necessário, adicionar espaço preto nas bordas
        if new_height != self.image.shape[0] or new_width != self.image.shape[1]:
            # Criar uma imagem preta com o novo tamanho
            black_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
            
            # Colocar a imagem original no canto superior esquerdo da nova imagem preta
            black_image[:self.image.shape[0], :self.image.shape[1]] = self.image

            IMAGE_COPY = black_image

        # Posicionar o texto e desenhar as linhas
        y_offset = data['coordinates']['y'] + data['coordinates']['height'] + TEXT_OFFSET  # Posição inicial do texto
        # for line in text_lines:
        #     cv2.putText(IMAGE_COPY, line, (data['coordinates']['x'], y_offset), 
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1)
        #     y_offset += 20  # Deslocamento para a próxima linha
        for line in text_lines:
            (text_width, text_height), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, TEXT_SIZE, 1)
            
            if DRAW_TEXT_BACKGROUND:
                # Desenhar o fundo preto por trás do texto
                cv2.rectangle(IMAGE_COPY, (data['coordinates']['x'], y_offset - text_height), 
                            (data['coordinates']['x'] + text_width, y_offset + text_height), 
                            (0,0,0), -1)  # Retângulo preto, preenchido
            
            # Desenhar o texto sobre o fundo preto
            cv2.putText(IMAGE_COPY, line, (data['coordinates']['x'], y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, TEXT_SIZE, TEXT_COLOR, 1)
            y_offset += text_height + 5  # Deslocamento para a próxima linha

        # Desenhar a caixa verde
        cv2.rectangle(IMAGE_COPY, (data['coordinates']['x'], data['coordinates']['y']),
                    (data['coordinates']['x'] + data['coordinates']['width'], data['coordinates']['y'] + data['coordinates']['height']),
                    BOX_COLOR, 2)

        return IMAGE_COPY
        
    def read(self):
        return pytesseract.image_to_string(self.image) # get this from somewhere else, pytesseract isnt native from Screenshot class
        
    def show(self, data=None, title='Screenshot'):
        """
        Mostra a screenshot com opções adicionais de visualização.

        Args:
            data (None, str, dict): 
                - None: Exibe a screenshot simples.
                - str: Exibe a screenshot com texto adicional abaixo.
                - dict: Exibe a screenshot destacando os resultados de `find_image`.
        """
        # Copiar a imagem para evitar alterações na original
        image_to_show = self.image.copy()

        if data is None:
            pass

        elif isinstance(data, str):
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 1
            color = (255, 255, 255) # text color

            # break text by lines
            lines = data.split('\n')
            text_size = [cv2.getTextSize(line, font, font_scale, thickness)[0] for line in lines]
            max_text_width = max(size[0] for size in text_size)
            text_height = sum(size[1] + 5 for size in text_size)  # y-spacing between lines

            # calc new dimensions to fit text
            new_width = max(image_to_show.shape[1], max_text_width + 20)
            new_height = image_to_show.shape[0] + text_height + 20

            # redim entire image to fit text
            output_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
            output_image[:image_to_show.shape[0], :image_to_show.shape[1], :] = image_to_show

            # add text below image
            y_offset = image_to_show.shape[0] + 20
            for line, size in zip(lines, text_size):
                x_offset = (new_width - size[0]) // 2  # center horizontally
                cv2.putText(output_image, line, (x_offset, y_offset), font, font_scale, color, thickness)
                y_offset += size[1] + 5

            image_to_show = output_image

        elif isinstance(data, dict) and 'coordinates' in data:
            text='match'
            if 'displaytext' in data and data['displaytext']:
                text = data['displaytext']
            image_to_show = self._prep_image(data, text=text)
        else:
            raise ValueError("Invalid data type for `show`. Must be None, str, or a dict with 'found' key.")

        # await interaction and close
        cv2.imshow(title, image_to_show)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    def colorCount(self, color: tuple, highlight_color: tuple = (0, 255, 0), show: bool = False):
        """
        Count the number of pixels that match the color and optionally display the highlighted image.

        Args:
            color (tuple): The color to search for (e.g., (255, 255, 255)).
            highlight_color (tuple): The color used to highlight matching pixels (default: green (0, 255, 0)).
            show (bool): If True, display the image with highlighted pixels.

        Returns:
            int: Quantity of pixels that match the color.
        """
        # Convert to expected format if necessary
        if self.image.shape[-1] == 3:  # Check if has 3 channels (RGB or BGR)
            # OpenCV generally is BGR, so we invert to RGB
            image_rgb = self.image[..., ::-1]
        else:
            image_rgb = self.image

        # Create a mask to identify where pixels match the provided color
        mask = np.all(image_rgb == color, axis=-1)

        # Count the number of matching pixels
        count = np.sum(mask)

        if show:
            # Create a copy of the original image to avoid modifying it
            highlighted_image = self.image.copy()

            # Apply the highlight color where the mask is True
            highlighted_image[mask] = highlight_color

            # Show the highlighted image
            cv2.imshow('Highlighted Pixels', highlighted_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return count
    
    def findHighestColorDensity(self, color: tuple):
        """
        TODO(adrian) average this out?
        Find the region with the highest density of a specific color, using the region size defined in `self.region`.

        Args:
            color (tuple): The color to search for (e.g., (255, 255, 255)).
            show (bool): If True, display the image with the highlighted region.

        Returns:
            tuple: (x, y, w, h) bounding box of the region with the highest density.
        """
        
        # convert to expected format if necessary
        if self.image.shape[-1] == 3:  # check if has 3 channels (RGB or BGR)
            image_rgb = self.image[..., ::-1] # opencv is generally bgr, so we must invert to rgb
        else:
            image_rgb = self.image

        # create a mask where colors match
        mask = np.all(image_rgb == color, axis=-1).astype(np.uint8)

        # find contour of the matching pixels
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # find largest contour by area
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
        else:
            x = y = w = h = 0 # no pixels found


        return {
            'type': 'FIND_COLOR',
            'found': bool(contours),
            'coordinates': {
                'x': x,
                'y': y,
                'width': w,
                'height': h
            }
        }

    def find_image(self, template=None, template_path=None, threshold=0.81):
        """
        Localize a posição de uma imagem (template) dentro da imagem base (self.image).

        Args:
            template (np.array, optional): Imagem já carregada como array numpy.
            template_path (str, optional): Caminho para o arquivo da imagem template.
            threshold (float): Confiança mínima para considerar o match.

        Returns:
            dict: Resultado contendo informações do match.
        """
        if template is None and template_path is None:
            raise ValueError("You must provide either a `template` or `template_path`.")
        if template is not None and template_path is not None:
            raise ValueError("Provide either `template` or `template_path`, not both.")

        # Carregar template se for passado o caminho
        if template_path:
            template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
            if template is None:
                raise ValueError(f"Failed to load template from: {template_path}")

        # Garantir que a imagem base está presente
        if self.image is None:
            raise ValueError("Base image (self.image) is not defined.")

        def resize_to_target(image, original_size, target_size):
            """
            Redimensiona a imagem template para respeitar as dimensões alvo.
            """
            original_ratio = original_size['width'] / original_size['height']
            target_ratio = target_size['width'] / target_size['height']

            if target_ratio > original_ratio:
                scale_factor = target_size['height'] / original_size['height']
            else:
                scale_factor = target_size['width'] / original_size['width']

            new_width = int(image.shape[1] * scale_factor)
            new_height = int(image.shape[0] * scale_factor)
            return cv2.resize(image, (new_width, new_height))

        # Assumir resolução padrão 1920x1080
        respect = {'width': 1920, 'height': 1080}
        template_resized = resize_to_target(
            template,
            original_size={"width": 1920, "height": 1080},
            target_size=respect
        )

        # Converter ambas as imagens para escala de cinza
        gray_base = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template_resized, cv2.COLOR_BGR2GRAY)

        # Executar correspondência
        result = cv2.matchTemplate(gray_base, gray_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Coordenadas do match
        x, y = max_loc
        w, h = gray_template.shape[1], gray_template.shape[0]

        # Retornar o resultado
        found = max_val >= threshold
        return {
            'type': 'FIND_IMAGE',
            'found': found,
            'confidence': max_val,
            'threshold': threshold,
            'displaytext': f"Found: {found}\n(c:{max_val:.2f} > t:{threshold})",
            'coordinates': {  # Representa a posição e tamanho absolutos
                'x': x,
                'y': y,
                'width': w,
                'height': h
            }
        }       

class ScreenUtils:
    def __init__(self) -> None:
        self.TESSERACT_INSTALL_PATH = r'C:\Program Files\Tesseract-OCR'
        self.TESSERACT_COMMAND = self.TESSERACT_INSTALL_PATH + r'\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.TESSERACT_COMMAND
        pass
    
    # take screenshot
    # xy defines starting point
    # wh defines size of screenshot "box" (right and down from point, respectively)
    # https://i.imgur.com/c61v5eL.png
    def screenshot(self, x: int, y: int, w: int, h: int):
        region = {
            "left": x,
            "top": y,
            "width": w,
            "height": h
        }
        
        with mss.mss() as sct:
            
            # capture
            screenshot = sct.grab(region)
            
            # transform to np.array
            img = np.array(screenshot)
            
            if img.size == 0: # out of bounds, most likely
                return False
            
            # transforming to RGB for opencv
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
            
            return Screenshot(img_bgr, region)
    