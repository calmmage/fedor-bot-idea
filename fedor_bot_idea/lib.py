from bot_lib import App, Handler, HandlerDisplayMode
# import requests
from aiogram.types import Message
from aiogram import types
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random
from PIL import Image
import uuid
# GEOGEBRA_API_URL = 'https://www.geogebra.org/api/json.php'
import io
from langchain.prompts import ChatPromptTemplate

class MyPlugin: # langchain musi-shmusi, with ... tools and message history

    # todo: replace this sample system message with a specific command for generation
    SYSTEM_TEMPLATE = """
    This is a sample system message
    """
    # todo: polish the human template for ...
    HUMAN_TEMPLATE = """
    AVAILABLE COMMANDS:
    {commands_list}
    USER INPUT
    {user_input}
    """

    SAMPLE_MESSAGES = [
        {
            "commands_list": ...,
            "user_input": ...,
            "output": ...
        },
        {
            "commands_list": ...,
            "user_input": ...,
            "output": ...
        }]


    # def sample_prompt_constructor(self, commands_list, user_input):
    #     role_message = self.SYSTEM_TEMPLATE # .format something?
    #     human_template = self.HUMAN_TEMPLATE
    #     output_example = "output_example"
    #
    #     messages = [
    #         ("system", role_message),
    #         ("human", human_template.format(**input_example_data)),
    #         ("ai", output_example),
    #         ("human", human_template),
    #     ]
    #     messages = [(role, trim_extra_whitespace(message)) for role, message in
    #                 messages]
    #
    #     full_prompt = ChatPromptTemplate.from_messages(messages)
    #     return full_prompt
    #
    #     return self.HUMAN_TEMPLATE.format(commands_list=commands_list, user_input=user_input)





class MyApp(App):
    name = "Fedor Bot Idea"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-1, 11)
        self.ax.set_ylim(-1, 11)
        self.ax.set_aspect('equal')
        plt.grid(True)

    def generate_random_point(self, xmin, xmax, ymin, ymax):
        x = random.uniform(xmin, xmax)
        y = random.uniform(ymin, ymax)
        return np.array([x, y])

    def draw_point(self, x, y, label):
        self.ax.plot(x, y, 'o')
        self.ax.text(x, y, f' {label}', fontsize=12, ha='right')

    def draw_segment(self, x1, y1, x2, y2):
        self.ax.plot([x1, x2], [y1, y2], 'k-')

    def draw_triangle(self, points):
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]
        self.draw_segment(x1, y1, x2, y2)
        self.draw_segment(x2, y2, x3, y3)
        self.draw_segment(x3, y3, x1, y1)

    def draw_circle(self, center, radius, edge_color='b'):
        circle = patches.Circle(center, radius, edgecolor=edge_color, facecolor='none')
        self.ax.add_patch(circle)

    def find_incenter(self, a, b, c):
        a_len = np.linalg.norm(b - c)
        b_len = np.linalg.norm(a - c)
        c_len = np.linalg.norm(a - b)
        perimeter = a_len + b_len + c_len
        incenter = (a_len * a + b_len * b + c_len * c) / perimeter
        return incenter

    def find_excenter(self, a, b, c):
        a_len = np.linalg.norm(b - c)
        b_len = np.linalg.norm(a - c)
        c_len = np.linalg.norm(a - b)
        excenter = (-a_len * a + b_len * b + c_len * c) / (b_len + c_len - a_len)
        return excenter

    def calculate_incircle_radius(self, incenter, a, b, c):
        return np.linalg.norm(np.cross(b - c, b - incenter)) / np.linalg.norm(b - c)

    def calculate_excircle_radius(self, excenter, a, b, c):
        return np.linalg.norm(np.cross(b - c, b - excenter)) / np.linalg.norm(b - c)

    def save_plot(self, filepath=None):
        if filepath is None:
            filepath = self.data_dir / f"{uuid.uuid4().hex}.png"
        self.fig.savefig(filepath)
        plt.close(self.fig)
        # return Image.open(filepath)
        return filepath

    def draw_extended_line(self, point1, point2, linestyle='-', linewidth=1):
        """Draw a line through two points extending to the plot borders."""
        x1, y1 = point1
        x2, y2 = point2
        if x1 == x2:  # Vertical line case
            self.ax.plot([x1, x1], [self.ax.get_ylim()[0], self.ax.get_ylim()[1]],
                         linestyle, linewidth=linewidth)
        else:
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1

            x_vals = np.array(self.ax.get_xlim())
            y_vals = slope * x_vals + intercept
            self.ax.plot(x_vals, y_vals, linestyle, linewidth=linewidth)
    def generate_hardcode_image(self):

        # Hardcoded points
        # A = (0, 0)
        # B = (2, 3)
        # C = (5, 0)

        # Generate random points A, B, C
        A = self.generate_random_point(0, 10, 0, 10)
        B = self.generate_random_point(0, 10, 0, 10)
        C = self.generate_random_point(0, 10, 0, 10)

        # Draw points A, B, C
        self.draw_point(*A, 'A')
        self.draw_point(*B, 'B')
        self.draw_point(*C, 'C')

        # Draw triangle ABC
        self.draw_triangle([A, B, C])

        # Incenter and Excenter Calculation
        incenter = self.find_incenter(A, B, C)
        excenter = self.find_excenter(A, B, C)

        # Draw Incenter and Excenter
        self.draw_point(*incenter, 'Incenter')
        self.draw_point(*excenter, 'Excenter')

        # Calculate and Draw Circles
        incircle_radius = self.calculate_incircle_radius(incenter, A, B, C)
        excircle_radius = self.calculate_excircle_radius(excenter, A, B, C)

        self.draw_circle(incenter, incircle_radius, 'g')
        self.draw_circle(excenter, excircle_radius, 'r')

        # # Construct the angle bisector in GeoGebra
        # commands = [
        #     f'A = ({A[0]}, {A[1]})',
        #     f'B = ({B[0]}, {B[1]})',
        #     f'C = ({C[0]}, {C[1]})',
        #     'D = Point(PerpendicularBisector(A, B))',
        #     'E = Point(PerpendicularBisector(B, C))',
        #     'arc1 = Circle(D, Distance(D, B))',
        #     'arc2 = Circle(E, Distance(E, B))',
        #     'F = Intersect(Circle(D, Distance(D, B)), Circle(E, Distance(E, B)))',
        #     'bisector = Line(B, F)'
        # ]
        #
        # data = {
        #     'json': {
        #         'app': 'classic',
        #         'title': 'Angle Bisector',
        #         'commands': commands
        #     }
        # }
        #
        # response = requests.post(GEOGEBRA_API_URL, json=data)

        return self.save_plot()


# - 1) сделать чтобы хоть что-то работало
#     - a) сделать command handler /generate_hardcode_image
#     - b) в него написать код который через геогебру строит картинки
#     - c) исполнить + отправить картинку

class MyHandler(Handler):
    name = "main"
    display_mode = HandlerDisplayMode.FULL

    commands = {
            "generate_hardcode_image_handler": "generate_hardcode_image"
            # "description": "Generate an image of an angle bisector"
        }

    async def generate_hardcode_image_handler(self, message: Message, app: MyApp):
        # image_path = app.generate_hardcode_image()
        # with open(image_path, 'rb') as image:
        #     await message.reply_photo(image)

        # from aiogram.types import InputFile
        # import io
        #
        # image_path = app.generate_hardcode_image()
        # image = InputFile(image_path)
        # await message.reply_photo(image)
        import io
        from aiogram.types import BufferedInputFile

        # Generate the image
        image_path = app.generate_hardcode_image()

        # Read the image file into a BytesIO object
        with open(image_path, 'rb') as image_file:
            image_bytes = io.BytesIO(image_file.read())

        # Create a BufferedInputFile instance
        image = BufferedInputFile(image_bytes.getvalue(), filename='photo.jpg')

        # Send the photo
        await message.reply_photo(photo=image)

    #     # image = image_path.open('rb')
    #     # await message.reply_photo(image)
    #     # """ or upload a new photo using multipart/form-data. The photo must be at most 10 MB in size. The photo's width and height must not exceed 10000 in total. Width and height ratio must be at most 20. :ref:`More information on Sending Files » <sending-files>`"""
    # # @router.message(F.photo[-1].as_('photo'))
    # # async def photo_handler(message: types.Message, photo: types.PhotoSize):
    #     file = await message.bot.get_file(photo.file_id)
    #     photo = io.BytesIO()
    #     await message.bot.download_file(
    #         file_path=file.file_path,
    #         destination=photo
    #     )
    #     result: Image = func_with_pillow(photo, message.caption)
    #     photo = io.BytesIO()
    #     result.save(photo, 'JPEG')
    #     await message.answer_photo(
    #         photo=types.BufferedInputFile(photo.getvalue(), filename='photo.jpg'),
    #     )
        #
        # try:
        #     response = app.generate_hardcode_image()
        #     if response.status_code == 200:
        #         result = response.json()
        #         url = result.get('url')
        #         await self.send_safe(f'Here is your angle bisector: {url}', message.chat.id)
        #     else:
        #         await self.send_safe( f'There was an error with GeoGebra API: {response.status_code}', message.chat.id)
        #
        # except Exception as e:
        #     return e
        #     # update.message.reply_text(f'Error: {e}')


    # def tool_handler(self, message, app: App):
    #     text = self.get_message_text(message)
    #
    #     pass
