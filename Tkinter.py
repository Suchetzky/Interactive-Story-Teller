import tkinter as tk
import urllib.request
from openai import OpenAI
from PIL import ImageTk, Image
import random
import string
import os

class PokemonGameApp(tk.Tk):
    photoX = 187
    photoY = 169

    generateImgButtonX = 255
    generateImgButtonY = 375
    resetButtonX = 315
    resetButtonY = 345
    shuffle1ButtonX = 53
    shuffle1ButtonY = 370
    shuffle2ButtonX = 110
    shuffle2ButtonY = 370

    def __init__(self):
        self.response_counter = 0
        self.client = OpenAI(
            api_key=open("API_KEY", "r").read(), )
        self.imgPrompt = ""

        self.assistant = self.client.beta.assistants.create(
            name="Pokemon Storyteller",
            instructions="Write up to 10 words response!"
                         "1. Act as a storyteller that assists a player in their Pokemon game journey."
                         "2. The player begins at an Israeli Air Force base, a small base with only two "
                         "buildings: one is an F-35 squadron, and the other is the Shekem, "
                         "where you can find only food and drinks. There is "
                         "also a grassy area."
                         "3. The player can move around the base,in the "
                         "grass and buildings."
                         "4. The player can catch 1 Pokemon from Generation 1."
                         "5. The player can only battle the Pokemon Squadron Leader."
                         "6. The player can encounter Pokemon in the grass."
                         "7. Continue the game until the player reaches the "
                         "squadron, wins the battle against the Squadron Leader with a Pokemon fight, "
                         "and becomes the champion. The player can only fight if they have caught "
                         "a Pokemon first."
                         "8. Respond with a maximum of 10 words. no more than 10 words."
                         "9. Guide the player to the end of the game, where they "
                         "catch a Pokemon, go to the squadron, "
                         "fight the Squadron Leader, win a Pokemon match, and become the champion. "
                         "The player can enter the squadron only if they have already caught a "
                         "Pokemon."
                         "10. After the player becomes champion, they can't do anything "
                         "else; the game is over."
                         "11. The Squadron Leader has one rare Pokemon, an F-35 plane "
                         "that has fire and air attacks.",

            tools=[{"type": "code_interpreter"}],
            model="gpt-3.5-turbo-1106"
        )

        self.thread = self.client.beta.threads.create()

        super().__init__()
        self.title("Pokémon Game Terminal")
        self.geometry("400x646")  # Adjust the window size as needed

        # Load and display the background image
        self.background_image = ImageTk.PhotoImage(Image.open(
            "GameBoyBack1.png"))
        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.resizable(False, False)

        # Create a scrolled text box for terminal-like interaction
        self.terminal = tk.Text(self, undo=True, height=7, wrap='word',
                                font=("MS Serif", 12), borderwidth=3,
                                relief="groove")

        self.terminal.pack(side=tk.BOTTOM, expand=False, fill=tk.Y,
                           padx=33, pady=56)

        self.terminal.tag_configure("Start",
                                    foreground="purple",
                                    font=("MS Serif", 12))
        self.terminal.insert(tk.END,
                             "Embark on a journey as a Pokémon "
                             "trainer.\n"
                             "Capture your first Pokémon, and face the\n"
                             "ultimate challenge!\na Squadron pokemon "
                             "battle.\n", "Start")
        self.terminal.tag_configure("YoungTrainer", foreground="black",
                                    font=("MS Serif", 12))

        self.terminal.insert(tk.END,
                             "young trainer, type your next move: \n",
                             "YoungTrainer")
        self.terminal.bind("<Return>", self.process_command)
        img = Image.open("green.png")
        img = img.resize((self.photoX, self.photoY), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.image_label = tk.Label(self, image=img)
        self.image_label.pack()
        self.image_label.place(x=105, y=100)
        self.image_label.image = img

        # Add a button with specific coordinates
        self.add_button(x=self.generateImgButtonX,
                        y=self.generateImgButtonY,
                        function=self.add_image_button_clicked)
        self.add_button(x=self.resetButtonX, y=self.resetButtonY,
                        function=self.reset_button_clicked)
        self.add_shuffle_button(x=self.shuffle1ButtonX,
                                y=self.shuffle1ButtonY,
                        function=self.shuffle_button_clicked)
        self.add_shuffle_button(x=self.shuffle2ButtonX,
                                y=self.shuffle2ButtonY,
                                function=self.shuffle_button_clicked)

    def process_command(self, event):
        self.terminal.mark_set(tk.INSERT, self.terminal.index(tk.INSERT))
        # Get the full text in the terminal
        full_text = self.terminal.get("1.0", tk.END)
        # Define the prompt text to be removed
        prompt_text = "young trainer, type your next move: \n"
        # Remove the prompt text from the full text to isolate the command
        command = full_text.split(prompt_text)[-1].strip()
        # This will remove any leading/trailing whitespace that might have been accidentally inserted

        self.terminal.see(tk.END)  # Auto-scroll to the bottom
        self.handle_command(command)
        return "break"  # Prevents the default text insertion behavior

    def handle_command(self, command):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=command,
        )

        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )

        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id)
            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id)
                self.terminal.insert(tk.END, "\n\nProf.Oak" + ": " +
                                     messages.data[0].content[
                                         0].text.value + "\n\n",
                                     "prof_oak_thinks")
                self.imgPrompt += " " + messages.data[0].content[0].text.value
                if self.response_counter == 0:
                    self.display_image("firstBasePic.jpg")
                    self.imgPrompt = ""
                if self.response_counter % 4 == 0 and self.response_counter != 0:
                    response = self.image_response()

                    image_url = response.data[0].url

                    # Download the image from the URL using urllib
                    with urllib.request.urlopen(image_url) as url:
                        img_data = url.read()
                        # Save the image data to a file
                        name = ''.join(
                            random.choices(string.ascii_lowercase, k=5))

                        filename = name + '.jpg'
                        with open(filename, 'wb') as f:
                            f.write(img_data)

                    # Open and display the image using PIL
                    self.display_image(filename)
                    self.imgPrompt = ""
                self.response_counter += 1
                self.terminal.insert(tk.END,
                                     "young trainer, type your next move: \n",
                                     "YoungTrainer")
                self.terminal.see(tk.END)
                self.terminal.mark_set(tk.INSERT, tk.END)
                break

    def image_response(self):
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt="make a photo in the style of "
                       "pokemon Fire Red game, pixel art, "
                       "non realistic out of "
                       "this "
                       "sentence with no text in the photo: " +
                       self.imgPrompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
        except:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt="make a photo in the style of "
                       "pokemon Fire Red game, pixel art, "
                       "non realistic, game boy style game, out of "
                       "this "
                       "sentence with no text in the photo: " +
                       "green background like old game boy "
                       "screen with pokemons",
                size="1024x1024",
                quality="standard",
                n=1,
            )
        return response

    def display_image(self, image_path):
        img = Image.open(image_path)
        img = img.resize((self.photoX, self.photoY), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        if not self.image_label:
            self.image_label = tk.Label(self, image=img)
            self.image_label.pack(side="top", pady=50)
            self.image_label.image = img
        else:
            self.image_label.configure(image=img)
            self.image_label.image = img

    def add_button(self, x, y, function):
        rgb_color = f'#{170:02x}{33:02x}{105:02x}'
        button_canvas = tk.Canvas(self, width=31, height=31, bg=rgb_color,
                                  bd=0,
                                  highlightthickness=0)
        button_canvas.pack()
        button_canvas.place(x=x, y=y)
        button_canvas.bind("<Button-1>", function)

    def add_shuffle_button(self, x, y, function):
        rgb_color = f'#{99:02x}{99:02x}{99:02x}'
        button_canvas = tk.Canvas(self, width=20, height=20, bg=rgb_color,
                                  bd=0,
                                  highlightthickness=0)
        button_canvas.pack()
        button_canvas.place(x=x, y=y)
        button_canvas.bind("<Button-1>", function)

    def add_image_button_clicked(self,
                                 event=None):  # event parameter is optional here; it gets passed by the bind method
        self.terminal.insert(tk.END, "Image Generated!\n", "YoungTrainer")
        response = self.image_response()

        image_url = response.data[0].url

        # Download the image from the URL using urllib
        with urllib.request.urlopen(image_url) as url:
            img_data = url.read()
            # Save the image data to a file
            filename = image_url[0] + '.jpg'
            with open(filename, 'wb') as f:
                f.write(img_data)

        # Open and display the image using PIL
        self.display_image(filename)

    def reset_button_clicked(self, event=None):
        # Reset game state variables
        self.response_counter = 0
        self.imgPrompt = ""

        # Clear the terminal
        self.terminal.delete('1.0', tk.END)

        # Insert the initial game instructions or welcome message again
        self.terminal.insert(tk.END,
                             "Embark on a journey as a Pokémon "
                             "trainer.\n"
                             "Capture your first Pokémon, and face the\n"
                             "ultimate challenge!\na Squadron pokemon "
                             "battle.\n", "Start")
        self.terminal.insert(tk.END,
                             "young trainer, type your next move: \n",
                             "YoungTrainer")

        default_image = Image.open(
            "green.png")
        default_image = default_image.resize((self.photoX, self.photoY),
                                             Image.ANTIALIAS)
        default_img = ImageTk.PhotoImage(default_image)
        self.image_label.configure(image=default_img)
        self.image_label.image = default_img

    def shuffle_button_clicked(self, event=None):
        # Define the directory to search for images
        directory = (r"C:\Users\talsu\Desktop\UNIVERSITY\HUJI\year_3"
                     r"\TellingStories\InteractiveStoryTeller")  # Update this path to your actual image directory
        # Find all files in the directory that end with .jpg
        jpg_files = [os.path.join(directory, file) for file in
                     os.listdir(directory) if file.endswith('.jpg')]

        # Select a random image file from the list
        random_image_path = random.choice(jpg_files)

        # Load the image using PIL
        image = Image.open(random_image_path)
        image = image.resize((self.photoX, self.photoY),
                             Image.ANTIALIAS)  # Resize if necessary
        photo_image = ImageTk.PhotoImage(image)

        # Update the image widget with the new image
        # Assuming self.image_label is the Label widget where images are displayed
        self.image_label.configure(image=photo_image)
        self.image_label.image = photo_image  # Keep a reference!


if __name__ == "__main__":
    app = PokemonGameApp()
    app.mainloop()
