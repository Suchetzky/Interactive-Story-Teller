import tkinter as tk
from tkinter import scrolledtext
from PIL import ImageTk
from PIL import Image
import urllib.request
from openai import OpenAI


class PokemonGameApp(tk.Tk):
    photoX = 187
    photoY = 169
    def __init__(self):
        self.client = OpenAI(
            api_key=open("API_KEY", "r").read(), )

        self.assistant = self.client.beta.assistants.create(
            name="Pokemon Storyteller",
            instructions="Write up to 10 words response!"
                         "1. Act as a storyteller that assists a player in their Pokemon game journey."
                         "2. The player begins at an Israeli Air Force base, a small base with only two "
                         "buildings: one is an F-35 squadron, and the other is the Shekem, "
                         "where you can find only food and drinks. There is "
                         "also a grassy area."
                         "3. The player can move in four directions."
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
            "GameBoyBack.png"))
        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.resizable(False, False)

        # Create a scrolled text box for terminal-like interaction
        self.terminal = scrolledtext.ScrolledText(self, undo=True, height=10)
        self.terminal.pack(side=tk.BOTTOM, expand=False, fill=tk.Y,
                           padx=28, pady=40)

        self.terminal.tag_configure("Start",
                                    foreground="purple",font=("Arial", 12, "bold"))
        self.terminal.insert(tk.END,
                             "Embark on a journey as a Pokémon "
                             "trainer.\n"
                             "Capture your first Pokémon, and face the\n"
                             "ultimate challenge!\n – a Squadron pokemon "
                             "battle.\n","Start")
        self.terminal.tag_configure("YoungTrainer",foreground="blue",font=("Arial", 12))
        self.terminal.insert(tk.END,
                             "young trainer, type your next move: \n",
                             "YoungTrainer")
        self.terminal.bind("<Return>", self.process_command)
        img = Image.open("green.png")
        img = img.resize((self.photoX,self.photoY), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.image_label = tk.Label(self, image=img)
        self.image_label.pack()
        self.image_label.place(x=105, y=100)
        self.image_label.image = img
    def process_command(self, event):
        # Prevent the default newline character insertion on Return key press
        self.terminal.mark_set(tk.INSERT, self.terminal.index(tk.INSERT))
        command = self.terminal.get("end-2l",
                                    "end-1c")  # Get the last line input
        self.terminal.see(tk.END)  # Auto-scroll to the bottom

        self.handle_command(command)
        return "break"  # Prevents the default text insertion behavior

    def handle_command(self, command):
        self.terminal.tag_configure("prof_oak_thinks",
                                    foreground="purple")
        self.terminal.insert(tk.END, "\nProfessor Oak is thinking...\n","prof_oak_thinks")

        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        while True:
            run = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id,
                                                    run_id=run.id)

            if run.status == "completed":
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id)
                self.terminal.insert(tk.END,"Prof.Oak" + ": " + messages.data[0].content[
                    0].text.value + "\n","prof_oak_thinks")

                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt="make a photo in the concept of "
                           "pokemon Fire Red game out of this "
                           "sentence with no text in the photo: " +
                           messages.data[0].content[0].text.value,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )

                image_url = response.data[0].url

                # Download the image from the URL using urllib
                with urllib.request.urlopen(image_url) as url:
                    img_data = url.read()
                    # Save the image data to a file
                    filename = 'response.data[0].jpg'
                    with open(filename, 'wb') as f:
                        f.write(img_data)

                # Open and display the image using PIL
                self.display_image(filename)
                self.terminal.insert(tk.END,
                                     "young trainer, type your next move: \n",
                                     "YoungTrainer")
                self.terminal.see(tk.END)
                self.terminal.mark_set(tk.INSERT, tk.END)
                break


    def display_image(self, image_path):
        img = Image.open(image_path)
        img = img.resize((self.photoX,self.photoY), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        if not self.image_label:
            self.image_label = tk.Label(self, image=img)
            self.image_label.pack(side="top", pady=50)
            self.image_label.image = img
        else:
            self.image_label.configure(image=img)
            self.image_label.image = img


if __name__ == "__main__":
    app = PokemonGameApp()
    app.mainloop()
