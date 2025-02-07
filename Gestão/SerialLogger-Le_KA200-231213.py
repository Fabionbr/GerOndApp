# Arquivo Programa: run SerialLogger-Le_KA200-231213.py
# Pra rodar a partir do CMD.exe do Anaconda: 
# Digitar no prompt: python D:\Dropbox\MeusProgramas/SerialLogger-Le_KA200-231213.py
#
# Caminho de Dados: D:\Dropbox\MeusProgramas\Lixo
# 
# Autor: Fabio
# Programa para ler os dados da porta serial do Mitutoyo KA-200
# Versao anterior - 220623: "SerialLogger-2COM-220623.py" (tentativa de ler dois sensores)
# Versao 220622: Versão inicial, desenvolvida a patir do "DMS10-serial-logger-UserConfig-210725.py" 
#
# ============== Chama bibliotecas e acoes basicas iniciais ==============


# FALTA FAZER (lista feita na versao 220623)
# Gravar dados com resultado do status
# Gráficos de apresentação de dados (Independentes)
# fUNÇÃO "TRY" e de verificação de consistência
# Arquivo de configuração XML
# tempoinicial dará erro se ensaio cruzar a meia noite

# DMS10 em userconfig dos ensaios: 63 bytes/linha
# KA200: 27bytes/linha




import numpy as np
import serial
import datetime
#import time
import matplotlib.pyplot as plt

import os    # Módulo que permite acesos ao OS.
#import sys
import threading
import codecs




plt.close('all')        # Fecha todos os graficos

#################################################################################### 
# ================================================================================ #
# =========================== Variaveis pre definidas ============================ #
# ================================================================================ #
#################################################################################### 

# ==============
# Variáveis Globais. Usadas com a Thread
global horaFinal, tempoinicial, Flag_KA200        # Flags e variaveis de controle de encerrar todas as funções e de status da saída das threads
# global flag_ctrl_thread, horaFinal, tempoinicial, Flag_Sensor, Flag_KA200        # Flags e variaveis de controle de encerrar todas as threads e de status da saída das threads

# global com_port_Sensor, com_baud_Sensor, com_bytesize_Sensor, com_stopbits_Sensor    # Variaveis específicas da COM do SENSOR
global com_port_KA200, com_baud_KA200, com_bytesize_KA200, com_stopbits_KA200    # Variaveis específicas da COM do KA200
global com_parity, com_timeout, com_wrTimeout, com_intByteTimeout        # Variaveis comuns as COMs
# --------------


flag_ctrl_thread = False            # Flag que sendo "true" vai terminar a thread ou função

outputfilepath = 'D:\Dropbox\MeusProgramas\Lixo/'
filename_default = 'Test_Le_KA200'
default_duracao = 5            # Duracao prevista da aquisicao dos dados

# com_port_Sensor = 'COM1'
com_port_KA200 = 'COM20'
# com_baud_Sensor = 9600
com_baud_KA200 = 9600
# com_bytesize_Sensor = 8
com_bytesize_KA200 = 7
# com_stopbits_Sensor = 2
com_stopbits_KA200 = 1
com_parity = 'N'
com_timeout=0.5      # Pode ser None
com_wrTimeout=0.5
com_intByteTimeout=0.5      #Inter-character timeout, None to disable (default)


#################################################################################### 
# ================================================================================ #
# ===========================          Funções        ============================ #
# ================================================================================ #
#################################################################################### 


# # ==================================================================================
# # FUNÇÂO: CONFIGURA E ABRE A PORTA SERIAL DO SENSOR E LÊ DADOS ENQUANTO HOUVER ENSAIO
# # Recebe: Nada, para facilitar, em função da quantidade de parâmetros (dados porta serial e de tempo são variáveis globais)
# # Retorna: Nada, pela função ser chamada como thread (Arrays de saída e falg de erro são variáveis globais) 

# def ThreadSensor():

#     try:
#         global dadosSensor, tempoSensor, Flag_Sensor
        
#         dadosSensor = []    # Cria array com os dados de tempo e frase do sensor
#         tempoSensor = []
        
#         aa = True        # Flag de ERRO do looping 
#         tempo = 0        # Variável de instante da leitura 
#         tempSensor = ''    # Variável auxilar de leitura da COM_SENSOR
        
#         with serial.Serial(
#                 port=com_port_Sensor,
#                 baudrate=com_baud_Sensor,    # Configuração para TSS1
#                 bytesize=com_bytesize_Sensor,
#                 parity=com_parity,
#                 stopbits=com_stopbits_Sensor,    # Configuração para TSS1
#                 timeout=com_timeout,      # Pode ser None
#                 write_timeout=com_wrTimeout,
#                 inter_byte_timeout= com_intByteTimeout      #Inter-character timeout, None to disable (default)
#                 ) as ser:
            
        
#                 while aa == True and float(tempo) < horaFinal and flag_ctrl_thread == False:
#                     tempSensor += ser.read(1).hex()    # Lê string da porta serial 
#                     if tempSensor[len(tempSensor)-4:] == '0d0a':
#                         dadosSensor.append(tempSensor)
#                         # ==============
#                         # Cria o time stamp a partir do tempo inicial
#                         tempo = datetime.datetime.now().timestamp()

#                         tempoSensor.append(tempo)        # Grava time stamp np array
#                         # --------------

#                         tempSensor = ''
                    

#         ser.close()    # fecha a porta serial do SENSOR para abrir a outra

#         Flag_Sensor = 'FIM DA AQUISIÇÃO DO SENSOR'

#     except Exception as ex:
#         print("Outro ERRO: Exception")
#         print(ex)
    
#         # Interrompe a thread
#         flag_ctrl_thread == True
#         Flag_Sensor = 'ERRO LEITURA SENSOR'
#         # --------------    

#     return()
# # ----------------------------------------------------------------------------------


# ==================================================================================
# FUNÇÂO: CONFIGURA E ABRE A PORTA SERIAL DO KA200 E LÊ DADOS ENQUANTO HOUVER ENSAIO
# Recebe: Nada, para facilitar, em função da quantidade de parâmetros (dados porta serial e de tempo são variáveis globais)
# Retorna: Nada, pela função ser chamada como thread (Arrays de saída e falg de erro são variáveis globais) 


def ThreadKA200():

    try:
        global dadosKA200, tempoKA200, Flag_KA200
        
        dadosKA200 = []    # Cria array com os dados de tempo e frase do KA200
        tempoKA200 = []
        
        aa = True        # Flag de ERRO do looping 
        tempo = 0        # Variável de instante da leitura 
        tempKA200 = ''    # Variável auxilar de leitura da COM_SENSOR
        
        with serial.Serial(
                port=com_port_KA200,
                baudrate=com_baud_KA200,    # Configuração para TSS1
                bytesize=com_bytesize_KA200,
                parity=com_parity,
                stopbits=com_stopbits_KA200,    # Configuração para TSS1
                timeout=com_timeout,      # Pode ser None
                write_timeout=com_wrTimeout,
                inter_byte_timeout= com_intByteTimeout      #Inter-character timeout, None to disable (default)
                ) as ser:
            
        
                while aa == True and float(tempo) < horaFinal and flag_ctrl_thread == False:
                    
                    tempKA200 += ser.read(1).hex()    # Lê string da porta serial 
                    if tempKA200[len(tempKA200)-4:] == '0d0a':
                        dadosKA200.append(tempKA200)

                        # ==============
                        # Cria o time stamp a partir do tempo inicial
                        tempo = datetime.datetime.now().timestamp()

                        tempoKA200.append(tempo)        # Grava time stamp np array
                        # --------------
                        tempKA200 = ''

                    # ==============
                    # Mostra na tela o tempo de ensaio, sempre no mesmo lugar
                        aux1 = int((tempo - tempoinicial)*10)/10    # Tempo de ensaio em décimo de segundo
                    
                        print('\r {}'.format(aux1), end='')    # Printa na tela o tempo, sempre no mesmo lugar
                    # --------------
                        
                    # ==============
                    # Imprime na tela se leitura foi OK
                        print()
                        print()
                        # print(Flag_Sensor)    # Indicam se leitura foi OK ou não
                        print(Flag_KA200)     #
                        print()
                        print()
                    # --------------

        ser.close()    # fecha a porta serial do SENSOR para abrir a outra

        Flag_KA200 = 'FIM DA AQUISIÇÃO DO KA200'

    except Exception as ex:
        print("ERRO: Exception")
        print(ex)
    
        # Interrompe a thread
        flag_ctrl_thread == True
        Flag_KA200 = 'ERRO LEITURA KA200'
        # --------------    

    return()
# ----------------------------------------------------------------------------------


# ==================================================================================
# FUNÇÂO: VERIFICA SE HÁ DADOS INVÁLIDOS POR CAUSA DE RUÍDOS, OU SEJA COM CARACTÉRES
# DIFERENTES DE NUMEROS (30 ao 39), " " (20), "." (2e), "+" (2b), "-" (2d)
# SE HOUVER TROCA POR "&" (26)
# Recebe: Os dois LIST com dados em Hex
# Retorna:  Os mesmos LISTs corrigidos e os LISTs "Status" com o número das linhas onde houve troca ("0" não houve troca)

# def VerificaIntgridade(dadosSensor, dadosKA200):       # Recebe o array de dados
def VerificaIntgridade(dadosKA200):       # Recebe o array de dados

    # statusSensor = [0]    # Cria um LIST com o número das linhas com problema
    statusKA200 = [0]     # Quando não houve alteração, retorna só "0"

# # ==============
# # Verificação SENSOR
#     aa = 0        # 1a linha do LIST
#     while aa != len(dadosSensor):
#         mensagem = dadosSensor[aa]        # Separa a "aaéssima" linha
#         flag = 0        # Flag de houve erro na mesagem
#         for i in range(0, 9):    # Percorre variáveis da mensagem procurando bugg
#             j= i*12+ 6      # Primeiro caracter da variável. Começa com 6 para pular até o 1o sinal do Roll
#             k = 10          # posição relativa do último caracter de numero
            
#             if i >= 6:      # As 3 últimas variáveis tem 5 digitos e não 4 
#                 j= (i-6)*14+ 78      # Primeiro caracter da variável. Começa com 6 para pular até o 1o sinal do Roll
#                 k = 12          # posição relativa do último caracter de numero
                
#             dig = mensagem[j:j+2]           # Separa o enésimo sinal
#             numero = mensagem[j+2:j+k]     # Separa o valor da enésima variável
    
#             if dig != '20' and dig != '2d':  # Verifica se é 'espaço'/20 ou '-'/2d
#                 dig = '26'                   # se não for, substitui por '&'
#                 flag = 1    # Marca que houve erro na linha
    
#             for aux in range(0,len(numero), 2):    # Verifica se são numeros entre 0 e 9
#                 temp = int(numero[aux: aux+2], 16)
#                 if not(temp >= 48 and temp <= 57):
#                     numero = numero[:aux]+ '26' + numero[aux+2:]    # se não for, substitui por '&'
#                     flag = 1    # Marca que houve erro na linha
    
#             mensagem = mensagem[:j]+dig + numero+mensagem[j+k:]    # Recoloca numeros corrigidos nas posições originais
    
#         if flag != 0:
#             statusSensor.append(aa+1)    ## adiciona ao status o número da linha com erro 
    
#         dadosSensor[aa] = mensagem
#         aa += 1
#     # --------------
    
    # ==============
    # Verificação KA200
    aa = 0        # 1a linha do LIST
    while aa != len(dadosKA200):
        mensagem = dadosKA200[aa]        # Separa a "aaéssima" linha
        flag = 0        # Flag de houve erro na mesagem
        dig = mensagem[4:6]           # Separa o enésimo sinal
        numero = mensagem[6:14]     # Separa a 1a parte do valor de X
        ponto = mensagem[14:16]     # Separa o ponto
        numero1 = mensagem[16:22]     # Separa 2a parte o valor de X
    
        if dig != '2b' and dig != '2d':  # Verifica se é '+'/20 ou '-'/2d
            dig = '26'                   # se não for, substitui por '&'
            flag = 1    # Marca que houve erro na linha
    
        for aux in range(0,len(numero), 2):    # Verifica 1a parte se são numeros entre 0 e 9
                temp = int(numero[aux: aux+2], 16)     # Converte Hex em inteiro decimal
                if not(temp >= 48 and temp <= 57):    # Compara com os números em decimal na tabela ASCII 
                    numero = numero[:aux]+ '26' + numero[aux+2:]    # se não for, substitui por '&'
                    flag = 1    # Marca que houve erro na linha
    
        if ponto != '2e':  # Verifica se é '.'/2e
            ponto = '2e'                   # se não for, corrige
    
        for aux in range(0,len(numero1), 2):    # Verifica 2a parte se são numeros entre 0 e 9
                temp = int(numero1[aux: aux+2], 16)     # Converte Hex em inteiro decimal
                if not(temp >= 48 and temp <= 57):    # Compara com os números em decimal na tabela ASCII
                    numero1 = numero1[:aux]+ '26' + numero1[aux+2:]    # se não for, substitui por '&'
                    flag = 1    # Marca que houve erro na linha
    
    
        mensagem = mensagem[:4]+dig + numero+ ponto+ numero1+ mensagem[22:]    # Recoloca numeros corrigidos nas posições originais
    
        if flag != 0:
            statusKA200.append(aa+1)    ## adiciona ao status o número da linha com erro 
    
        dadosKA200[aa] = mensagem
        aa += 1

    # return(dadosSensor, dadosKA200, statusSensor, statusKA200)
    return(dadosKA200, statusKA200)

# ----------------------------------------------------------------------------------


# # ==================================================================================
# # FUNÇÂO: PLOTA OS GRÁFICOS PARA VERIFICAÇÃO DA QUALIDADE DO ENSAIO
# # Recebe: Nada, dados E TEMPOS são variáveis globais
# # Retorna: Nada
 
# def plotaGraficos():
    
# # =============================================================================
# # Imprime as leituras de cada variável do SENSOR 
#     dif = []        # Variável para verificar se o "Delta" de tempo da leitura foi constante 
#     roll = []
#     pitch = []
#     heave = []
#     ang_RateX = []
#     ang_RateY = []
#     ang_RateZ = []
#     accX = []
#     accY = []
#     accZ = []
    
#     tempo = np.float_(tempoSensor)  
    
#     # ==============
#     # Calcula Delta Tempo médio como referência para verificar a oscilação no DELTA T de aquisição
#     dif_inicial = 0
#     for i in range (0, len(tempo)-1):
#         dif_inicial += (tempo[i+1]-tempo[i]) 
#     dif_inicial = dif_inicial/len(tempo)
    
#     for i in range(0,len(dadosSensor)):
#         if i > 0:
#             dif.append(tempo[i] - tempo[i-1] - dif_inicial)    # Faz a diferença de DELTA T e depois compara com o inicial
#         # ==============
#         # Separa as variaveis do array
#         roll.append(float(dadosSensor[i][3:8])/100)  
#         pitch.append(float(dadosSensor[i][9:14])/100)  
#         heave.append(float(dadosSensor[i][15:20])/100)  
#         ang_RateX.append(float(dadosSensor[i][21:26])/100)  
#         ang_RateY.append(float(dadosSensor[i][27:32])/100)  
#         ang_RateZ.append(float(dadosSensor[i][33:38])/100)  
#         accX.append(float(dadosSensor[i][39:45])/1000)  
#         accY.append(float(dadosSensor[i][46:52])/1000)  
#         accZ.append(float(dadosSensor[i][53:59])/1000)  
    
#     plt.figure(0)
#     plt.plot(tempo[1:],dif)
#     plt.title('Diferenças para a Taxa de Amostragem básica SENSOR: '+str(int(dif_inicial*10000)/10000))
    
#     plt.figure(1)
#     plt.plot(tempo, roll)
#     plt.title('Roll')
    
#     plt.figure(2)
#     plt.plot(tempo, pitch)
#     plt.title('Pitch')
    
#     plt.figure(3)
#     plt.plot(tempo, heave)
#     plt.title('Heave')
    
#     plt.figure(4)
#     plt.plot(tempo, ang_RateX)
#     plt.title('Ang_RateX')
    
#     plt.figure(5)
#     plt.plot(tempo, ang_RateY)
#     plt.title('Ang_RateY')
    
#     plt.figure(6)
#     plt.plot(tempo, ang_RateZ)
#     plt.title('Ang_RateZ')
    
#     plt.figure(7)
#     plt.plot(tempo, accX)
#     plt.title('Aceleração X')
    
#     plt.figure(8)
#     plt.plot(tempo, accY)
#     plt.title('Aceleração Y')
    
#     plt.figure(9)
#     plt.plot(tempo, accZ)
#     plt.title('Aceleração Z')
    
# # =============================================================================
# # Imprime a leitura do SENSOR e o Delta no tempo entre aquisições

#     dif = []        # Variável para verificar se o "Delta" de tempo da leitura foi constante 
#     escala = []

#     tempo = np.float_(tempoKA200)  
    
#     # ==============
#     # Calcula Delta Tempo médio como referência para verificar a oscilação no DELTA T de aquisição
#     dif_inicial = 0
#     for i in range (0, len(tempo)-1):
#         dif_inicial += (tempo[i+1]-tempo[i]) 
#     dif_inicial = dif_inicial/len(tempo)
    
#     for i in range(0,len(dadosKA200)):
#         if i > 0:
#             dif.append(tempo[i] - tempo[i-1] - dif_inicial)    # Faz a diferença de DELTA T e depois compara com o inicial
#         # ==============
#         # Separa as variaveis do array
#         escala.append(float(dadosKA200[i][2:11]))  
    
#     plt.figure(10)
#     plt.plot(tempo[1:],dif)
#     plt.title('Diferenças para a Taxa de Amostragem básica KA200: '+str(int(dif_inicial*10000)/10000))
    
#     plt.figure(11)
#     plt.plot(tempo, escala)
#     plt.title('Escala KA200')
    
    
#     plt.show()    

#     return()
# # ----------------------------------------------------------------------------------





# =============================================================================
# =============================================================================
# ========================  PROGRAMA PRINCIPAL  ===============================
# =============================================================================
# =============================================================================

# ==============
# Prefixo do nome dos arquivos de saída 

texto = 'Escolha o prefixo do nome do arquivo de saída (default: '+filename_default+')? '
filename = input(texto)
if filename =="":
    filename = filename_default
# --------------

# ==============
# Tempo de duração das leituras 
duracao = 'Qual a duração do ensaio (default: '+ str(default_duracao) + 's)? '
duracao = input(duracao)
if duracao == "":
    duracao = default_duracao
else:
    duracao = int(duracao)
duracao += 1            # Aumenta o  tempo de ensaio para compensar o atraso no lançamento das threads (Mantido, mesmo sem lançar threads)
# --------------


# =============================================================================
# =============================================================================
# Executa leitura dos dados

print('')
print('')
print("Logging started. Ctrl-C to stop.")
print('')
print('')


# =============================================================================
# Registra o tempo de início da medição em segundos, resolução de 0.1 milissegundos
aux = datetime.datetime.now()    # Registra o momento atual
tempoinicial = aux.timestamp()
# temp = aux.strftime("%H%M%S%f")[:-2]    # Tempo em HHMMSSDDDD
# tempoinicial = float(temp[0:2])*3600 + float(temp[2:4])*60 + float(temp[4:6]) 
# + float(temp[6:10])/10000    # Tempo inicial em segundos, arredondando em décimos e ms  (sem a data do dia)
# --------------

# ==============
# Registra a hora final do ensaio em formato HHMMSS
horaFinal = tempoinicial + duracao
          
# --------------

# =============================================================================
# ======== LOOPING DE CONTROLE: PARA POR CTRL-C OU FIM DE AQUISIÇÃO ===========
# =============================================================================

try:        #Cria exceções, principalmente para o CTRL-C

    Flag_KA200 = ''
    # Flag_Sensor = ''

# # =============================================================================
# # Lança as duas Threads de aquisição das SERIAIS

#     threading.Thread(target=ThreadSensor).start()

#     threading.Thread(target=ThreadKA200).start()
    Aux = ThreadKA200()

# # -----------------------------------------------------------------------------


# # ==============
# # Mostra na tela o tempo de ensaio, sempre no mesmo lugar
#     # while Flag_KA200 =='' or Flag_Sensor == '':
#     while Flag_KA200 =='':
#         temp = datetime.datetime.now().timestamp()    # Hora agora
#         temp = int((temp - tempoinicial)*10)/10    # Tempo de ensaio em décimo de segundo

#         print('\r {}'.format(temp), end='')    # Printa na tela o tempo, sempre no mesmo lugar
# # --------------
    
# # ==============
# # Imprime na tela se leitura foi OK
#     print()
#     print()
#     # print(Flag_Sensor)    # Indicam se leitura foi OK ou não
#     print(Flag_KA200)     #
#     print()
#     print()
# # --------------

# ###################################
#     Sensor = dadosSensor       # Array pra backup de verificação
###################################
    KA200 = dadosKA200       # Array pra backup de verificação


# =============================================================================
# Nos vetores tempoXXXX da aquisição, elimina o tempo inicial e faz a formatação
# ==============
# # Executa para o SENSOR
#     for i in range(0, len(tempoSensor)):
#         temp = str(int((tempoSensor[i] - tempoinicial)*10000)/10000)    # Subtrai tempoinicial e formata p/ string de saída

#         # ==============
#         # Verifica se os decimais estão com 4 dígitos
#         aux = len(temp)-temp.find('.')
#         if aux < 5:
#             temp += '0'*(5-aux)
#         tempoSensor[i] = ' '*(9-len(temp)) + temp    # Inclui espaços no início do tempo pra string ficar sempre com o mesmo tamanho
# ==============
# Executa para o KA200
    for i in range(0, len(tempoKA200)):
        temp = str(int((tempoKA200[i] - tempoinicial)*10000)/10000)    # Subtrai tempoinicial e formata p/ string de saída

        # ==============
        # Verifica se os decimais estão com 4 dígitos
        aux = len(temp)-temp.find('.')
        if aux < 5:
            temp += '0'*(5-aux)
        tempoKA200[i] = ' '*(9-len(temp)) + temp    # Inclui espaços no início do tempo pra string ficar sempre com o mesmo tamanho
# --------------

# =============================================================================
# CHAMA FUNÇÃO PARA VER INTEGRIDADE DOS DADOS
# Elimina a primeira linha do array que pode estar incompleta e torna o tempo de 
# início de ensaio o valor de tempo da primeira mensagem lida de uma das COM (Retira
# o atraso de lançamento das threads)

# ==============
# Elimina primeira leitura

    # dadosSensor = dadosSensor[1:]
    # tempoSensor = tempoSensor[1:]

    dadosKA200 = dadosKA200[1:]
    tempoKA200 = tempoKA200[1:]
# --------------

# ==============
# "Zera" início de ensaio
    # if tempoSensor[0] >= tempoKA200[0]: 
    #     tempoinicial = float(tempoKA200[0])
    # else:
    #     tempoinicial = float(tempoSensor[0])
    tempoinicial = float(tempoKA200[0])


    # aux1 = tempoSensor        # Para SENSOR, retira o atraso de lançamento das threads
    # for i in range(0, len(aux1)):            
    #     temp = str(int((float(aux1[i])-tempoinicial)*10000)/10000)
    #     # ==============
    #     # Verifica se os decimais estão com 4 dígitos
    #     aux = len(temp)-temp.find('.')
    #     if aux < 5:
    #         temp += '0'*(5-aux)
    #     aux1[i] = ' '*(9-len(temp)) + temp    # Inclui espaços no início do tempo pra string ficar sempre com o mesmo tamanho
    # tempoSensor = aux1
    
    aux1 = tempoKA200        # Para KA200, retira o atraso de lançamento das threads
    for i in range(0, len(aux1)):            
        temp = str(int((float(aux1[i])-tempoinicial)*10000)/10000)
        # ==============
        # Verifica se os decimais estão com 4 dígitos
        aux = len(temp)-temp.find('.')
        if aux < 5:
            temp += '0'*(5-aux)
        aux1[i] = ' '*(9-len(temp)) + temp    # Inclui espaços no início do tempo pra string ficar sempre com o mesmo tamanho
    tempoKA200 = aux1

# --------------

# ==============
# Verifica integridade dos dados    
    # (dadosSensor, dadosKA200, statusSensor, statusKA200) = VerificaIntgridade(dadosSensor, dadosKA200)    # Chama função que verifica se houve dados incorretos
    (dadosKA200, statusKA200) = VerificaIntgridade(dadosKA200)    # Chama função que verifica se houve dados incorretos

    # print('Linhas do SENSOR com problema ', statusSensor)
    print('Linhas do KA200 com problema ', statusKA200)
# --------------

# ==============
# Converte as mensagens de hexa para ASCII

    # aa = 0
    # while aa != len(dadosSensor):
    #     dadosSensor[aa] = codecs.decode(dadosSensor[aa], "hex").decode('ascii')    # Converte cada STR da LIST em UTF8
    #     aa += 1
    aa = 0
    while aa != len(dadosKA200):
        dadosKA200[aa] = codecs.decode(dadosKA200[aa], "hex").decode('ascii')    # Converte cada STR da LIST em UTF8
        aa += 1
# --------------

# ==============
# Pergunta se usuário quer ver os dados
    temp = input('Deseja ver os dados (s/n)? ')
    if temp !='n':    # So não mostra se a tecla for "n"
        # aa = 0
        # print('SENSOR')
        # while aa != len(dadosSensor):
        #     print(tempoSensor[aa], '  ',dadosSensor[aa], end = ' ')
        #     aa += 1
        aa = 0
        print('CONTADOR KA200')
        while aa != len(dadosKA200):
            print(tempoKA200[aa], '  ',dadosKA200[aa], end = ' ')
            aa += 1
# --------------


# =============================================================================
# ====================== GRAVA OS DADOS NOS ARQUIVOS ==========================
# =============================================================================

# =============================================================================
# Cria nomes, abre os dois arquivos de saída e cria os cabeçalhos

    data = datetime.datetime.now().strftime("-%y%m%d_%H%M")

# # ==============
# #Arquivo Sensor
#     aux = filename + '-SENSOR' + data + '.log'
#     outputFilePath_Sensor = os.path.join(outputfilepath, aux)    # Cria nome com caminho
#     outputFile_Sensor = open(outputFilePath_Sensor, mode='wb')    # Abre arquivo

#     # ==============
#     # 3 Linhas de cabeçalho do arquivo _SENSOR
#     cabecalho = 'Dado Bruto Sensor DMS-10 modo UserConfig \r\n'
#     outputFile_Sensor.write(cabecalho.encode())
#     cabecalho = 'Status ERRO: ' + str(statusSensor) + '\r\n'
#     outputFile_Sensor.write(cabecalho.encode())
#     cabecalho = 'Tempo ; Status; Roll ; Pitch ; Heave ; Ang_RateX ; Ang_RateY ; Ang_RateZ ; AccX ; AccY ; AccZ \r\n'
#     outputFile_Sensor.write(cabecalho.encode())
#     outputFile_Sensor.flush()
#     # --------------
# # --------------

# ==============
#Arquivo KA200
    aux = filename + '-KA200' + data + '.log'
    outputFilePath_KA200 = os.path.join(outputfilepath, aux)    # Cria nome com caminho
    outputFile_KA200 = open(outputFilePath_KA200, mode='wb')    # Abre arquivo

    # ==============
    # 3 Linhas de cabeçalho do arquivo _KA200
    cabecalho = "Dado Escala Linear Mitutoyo com contador KA-212 \r\n"
    outputFile_KA200.write(cabecalho.encode())
    cabecalho = 'Status ERRO: ' + str(statusKA200) + '\r\n'
    outputFile_KA200.write(cabecalho.encode())
    cabecalho = "Tempo ; X ""Leitura Escala""; Y ""Valor não utilizado"" \r\n"
    outputFile_KA200.write(cabecalho.encode())
    outputFile_KA200.flush()
    # --------------
# --------------

# =============================================================================
# Grava dados nos arquivos

# # ==============
# #Arquivo Sensor
#     aa = 0
#     while aa != len(dadosSensor):
#         aux = tempoSensor[aa] + '  ' + dadosSensor[aa]      # Monta linha
#         outputFile_Sensor.write(aux.encode())
#         outputFile_Sensor.flush()
#         aa += 1
#     outputFile_Sensor.close()
# # --------------

# ==============
#Arquivo KA200
    aa = 0
    while aa != len(dadosKA200):
        aux = tempoKA200[aa] + '  ' + dadosKA200[aa]      # Monta linha
        outputFile_KA200.write(aux.encode())
        outputFile_KA200.flush()
        aa += 1
    outputFile_KA200.close()
# --------------
# -----------------------------------------------------------------------------

# # =============================================================================
# # Chama subrotina que plota os gráficos 

#     plotaGraficos()    # Chama função que plota gráficos. Dados e tempo são variáveis globais


# =============================================================================
# ====================== Trata os erros e interrupções ========================
# =============================================================================
except KeyboardInterrupt:
    print("Logging stopped")

    # Interrompe a thread
    flag_ctrl_thread == True
    # --------------
# except UnicodeDecodeError as ex:
#     print("Outro ERRO: UnicodeDecodeError")
#     print(ex)

#     # Interrompe a thread
#     flag_ctrl_thread == True
#     # --------------
# except Exception as ex:
#     print("Outro ERRO: Exception")
#     print(ex)

#     # Interrompe a thread
#     flag_ctrl_thread == True
#     # --------------
# --------------



# # # =============================================================================
