import pyautogui
from time import sleep

pyautogui.click(107,109, duration=2)
pyautogui.write('a')
pyautogui.click(107,148, duration=2)
pyautogui.write('a')
pyautogui.click(154,181, duration=2)

with open('produtos.txt', 'r') as arquivo:
    for linha in arquivo:
        produto = linha.split(',')[0]
        quantidade = linha.split(',')[1]
        preco = linha.split(',')[2]

        pyautogui.click(127,46, duration=1.5)
        pyautogui.write(produto)

        pyautogui.click(128,76, duration=2)
        pyautogui.write(quantidade)

        pyautogui.click(129,107, duration=2)
        pyautogui.write(preco)

        pyautogui.click(179,155, duration=2)