#!/bin/bash
clear

#instalar o ollama via terminal 
curl -fsSL https://ollama.com/install.sh | sh

#baixar o modelo llama2
ollama pull llama2

#iniciar servidor ollama com o modelo llama2
ollama run llama2
