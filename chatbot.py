import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ollama import Client
import threading
import sys
import os
from gtts import gTTS
import playsound  # Para reproduzir o áudio


class Model:
    def __init__(self, host, model_name):
        self.client = Client(host=f'http://{host}')
        self.model = model_name
        self.stop_stream = False

    def send_to_ollama(self, user_text):
        try:
            self.stop_stream = False
            stream = self.client.chat(model=self.model, stream=True, messages=[{'role': 'user', 'content': user_text}])
            for chunk in stream:
                if self.stop_stream:
                    break
                yield chunk['message']['content']
        except Exception as e:
            print("Erro:", e)
            yield "Erro ao conectar ao servidor Ollama"

    def stop_response(self):
        self.stop_stream = True

class View(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("ChatBot")
        self.setup_ui()

    def setup_ui(self):
        self.configure(bg="#212121")  # Cor de fundo escura

        conversation_frame = tk.Frame(self, bg="#424242")  # Cor de fundo escura
        conversation_frame.pack(fill=tk.BOTH, expand=True)

        self.conversation = tk.Text(conversation_frame, wrap=tk.WORD, font=("Helvetica", 14), bg="#424242", fg="#FFFFFF")  # Cor de fundo escura, texto branco
        self.conversation.pack(fill=tk.BOTH, expand=True)
        self.conversation.insert(tk.END, 'Como posso lhe ajudar hoje?\n\n')

        input_frame = tk.Frame(self, bg="#212121")  # Cor de fundo escura
        input_frame.pack(fill=tk.X)

        self.user_input = tk.Entry(input_frame, font=("Helvetica", 14), bg="#424242", fg="#FFFFFF")  # Cor de fundo escura, texto branco
        self.user_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.user_input.bind("<Return>", lambda event: self.controller.handle_send_message())

        send_button = tk.Button(input_frame, text="Enviar", command=self.controller.handle_send_message, bg="#007bff", fg="#FFFFFF")  # Botão azul com texto branco
        send_button.pack(side=tk.RIGHT, padx=5, pady=5)

        button_frame = tk.Frame(self, bg="#212121")  # Cor de fundo escura
        button_frame.pack(fill=tk.X)

        stop_button = tk.Button(button_frame, text="Interromper", command=self.controller.handle_stop_response, bg="#dc3545", fg="#FFFFFF")  # Botão vermelho com texto branco
        stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        copy_button = tk.Button(button_frame, text="Copiar Resposta", command=self.controller.copy_response, bg="#28a745", fg="#FFFFFF")  # Botão verde com texto branco
        copy_button.pack(side=tk.LEFT, padx=10, pady=10)

        clear_button = tk.Button(button_frame, text="Limpar Conversa", command=self.controller.clear_conversation, bg="#ffc107", fg="#212121")  # Botão amarelo com texto escuro
        clear_button.pack(side=tk.LEFT, padx=10, pady=10)

        close_button = tk.Button(button_frame, text="Fechar Programa", command=self.controller.ask_to_close_program, bg="#6c757d", fg="#FFFFFF")  # Botão cinza com texto branco
        close_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Adicionando o botão "Ler o Texto"
        speak_button = tk.Button(button_frame, text="Ler o Texto", command=self.controller.handle_speak_text, bg="#6610f2", fg="#FFFFFF")  # Botão roxo com texto branco
        speak_button.pack(side=tk.LEFT, padx=10, pady=10)

    def copy_response(self):
        response_text = self.conversation.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(response_text)

    def clear_conversation(self):
        self.conversation.delete("1.0", tk.END)

    def update_conversation(self, response):
        if response.startswith('Você: '):
            self.conversation.insert(tk.END, f'\n{response}', "user")
        else:
            self.conversation.insert(tk.END, response, "bot")
        self.conversation.see(tk.END)

    def show_processing_message(self):
        self.conversation.insert(tk.END, "\nProcessando...\n")
        self.conversation.see(tk.END)

    def display_bot_image(self):
        # Carregar a imagem
        image = Image.open("bot.png")
        image = image.resize((150, 150), Image.LANCZOS)  # Redimensionar a imagem
        photo = ImageTk.PhotoImage(image)

        # Adicionar a imagem ao canto superior esquerdo da janela
        label = tk.Label(self, image=photo, bg="#212121")
        label.image = photo  # Manter uma referência para evitar a coleta de lixo
        label.pack(side=tk.LEFT, padx=10, pady=10)


class Controller:
    def __init__(self, host, model):
        self.model = Model(host, model)
        self.view = View(self)

    def handle_send_message(self):
        user_text = self.view.user_input.get()
        self.view.update_conversation(f'Você: {user_text}')  # Exibir a mensagem do usuário na conversa
        threading.Thread(target=self.send_message, args=(user_text,)).start()
        self.view.user_input.delete(0, tk.END)
        self.view.show_processing_message()

    def send_message(self, user_text):
        for response in self.model.send_to_ollama(user_text):
            self.view.update_conversation(response)

    def handle_stop_response(self):
        self.model.stop_response()

    def copy_response(self):
        self.view.copy_response()

    def clear_conversation(self):
        self.view.clear_conversation()

    def ask_to_close_program(self):
        if messagebox.askokcancel("Fechar Programa", "Deseja fechar o programa?"):
            self.view.destroy()

    def handle_speak_text(self):
        response_text = self.view.conversation.get("1.0", tk.END)
        self.speak(response_text)

    def speak(self, text):
        # Reproduzir o áudio usando gTTS
        try:
            tts = gTTS(text=text, lang='pt', slow=False)  # Estou assumindo que o texto está em português
            tts.save("spoken_text.mp3")
            playsound.playsound("spoken_text.mp3", True)
            os.remove("spoken_text.mp3")  # Remover o arquivo de áudio após reprodução
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao reproduzir o áudio: {str(e)}")

if __name__ == "__main__":
    # Verifica se o número correto de argumentos foi fornecido
    if len(sys.argv) != 2:
        os.system("clear")
        print('-' * 80)
        print("Você precisa fornecer como parâmetro na linha de comando o nome do arquivo de configuração")
        print("Exemplo: python3 chat.py config.txt")
        print("")
        print("Dentro do arquivo de configuração deve existir as seguintes linhas:")
        print("modelo: vicuna")
        print("host: localhost:11434")
        print("")
        sys.exit(1)

    # Lê os dados de configuração do arquivo
    with open(sys.argv[1], 'r') as file:
        lines = file.readlines()
        host = lines[1].split(": ")[1].strip()
        model = lines[0].split(": ")[1].strip()

    controller = Controller(host, model)
    controller.view.display_bot_image()  # Mostrar a imagem do bot
    controller.view.mainloop()
