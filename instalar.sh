clear
echo "Preparando tudo...."
sudo apt update && sudo apt upgrade -y
sudo apt autoremove && sudo apt autoclean
sudo apt install python3 python3-pip
sudo pip3 install virtualenv
virtualenv --version
echo
echo "Instalando as bibliotecas..."

# Captura o nome do diretório atual
current_dir=$(basename "$PWD")
echo "Diretório atual: $current_dir"

# Retrocede um diretório
cd ..

# Cria o ambiente virtual python
virtualenv chatbot-ollama
#cd chatbot-ollama

# Retorna ao diretório original
echo "Retornando ao diretório: $current_dir"
cd "$current_dir"
source bin/activate


pip install tk
pip install pillow
pip install ollama
pip install gtts
pip install playsound
echo
echo "Instalando o Ollama..."

# Verifica se o LLM Ollama está instalado
if command -v ollama &>/dev/null; then
    echo "LLM Ollama já está instalado."
else
    # Instalação do LLM Ollama
    echo "LLM Ollama não está instalado. Instalando..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

ollama pull llamma2
ollama list
python3 chatbot.py config.txt
