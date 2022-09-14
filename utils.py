from openpyxl import load_workbook
from math import sqrt
from os import getcwd
from typing import Dict, List
from definitions import *
import numpy as np
from matplotlib.figure import Figure


def compute_von_mises_tension(stress_node: Dict[str, float]) -> float:
    """Função que recebe dicionário com valores de stress e retorna a tensão de Von mises"""
    return (1/sqrt(2))*sqrt(
        pow(stress_node['sx']-stress_node['sy'],2) + 
        pow(stress_node['sy']-stress_node['sz'],2) + 
        pow(stress_node['sz']-stress_node['sx'],2) + 
        6*(pow(stress_node['txy'],2) + pow(stress_node['tyz'],2) + pow(stress_node['tzx'],2)))


def compute_tension_with_rotation(angle_degree: int, stress_list: List[dict]) -> list:
    """Função que realiza a rotação da tensão e calcula os novos valores de tensão"""
    angle_rad = np.deg2rad(angle_degree)
    rotate_tension_list = list(map(rotate_tension, [angle_rad]*len(stress_list), stress_list))
    return list(map(compute_von_mises_tension,rotate_tension_list))


def get_tension_diff_list(rotation, stress_list, tension_list):
    """Função que recebe as tensões rotacionadas e as tenções originas
    e retorna lista com a diferença entre elas"""
    result = list()
    for i,node in enumerate(stress_list):
        new_node = {
            'node_id': node['node_id'],
            'sx': rotation['new_sx'][i],
            'sy': rotation['new_sy'][i],
            'sz': rotation['new_sz'][i],
            'tyz': node['tyz'],
            'tzx': node['tzx'],
            'txy': node['txy']
        }
        result.append(compute_von_mises_tension(new_node))

    return [a - b for a, b in zip(tension_list, result)]


def rotate_tension(angle: int, stress_node: Dict[str, float]) -> Dict[str, float]:
    """Função que realiza a rotação da tensão"""

    #Matrix de rotação
    rt_matrix = np.array([[1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)]])

    #Matrix [𝜎]
    tension = np.array([[stress_node['sx'], stress_node['txy'], stress_node['tzx']],
            [stress_node['txy'], stress_node['sy'], stress_node['tyz']],
            [stress_node['tzx'], stress_node['tyz'], stress_node['sz']]])
    
    #Rotação [𝜎']
    result = np.dot(np.dot(rt_matrix, tension),  rt_matrix.T)

    #Dicionário com os valores do nodo
    new_node = {
        'node_id': stress_node['node_id'],
        'sx': result[0,0],
        'sy': result[1,1],
        'sz': result[2,2],
        'tyz': result[1,2],
        'tzx': result[0,2],
        'txy': result[0,1]
    }
    return new_node


def import_xlsx(file_path: str, columns: dict, first_row: int) -> List[dict]:
    """Função que importa os nodos dos arquivos xlsx e retorna uma lista de dicionários
    com os valores dos nodos"""
    result = list()

    row_count = first_row   #variável de contagem de linhas da planilha

    wb_obj = load_workbook(file_path) #Abre e carrega a planilha
    sheet = wb_obj.active   #objeto página da planilha

    read_finished = False   #variável que indica a finalização da leitura do valores

    while not read_finished:    #loop para leitura da planilha e armazenamento na lista result
        node_dict = dict()
        for key,value in columns.items():
            cell = sheet[f'{value}{row_count}']
            if cell.value is None:
                read_finished = True
                break
            node_dict[key] = cell.value
        if node_dict:
            result.append(node_dict)
        row_count += 1

    return result

def get_file_path(file_name: str) -> str:
    """Função que retorna o caminho dos arquivos excel"""
    cwd = getcwd()
    return "{current_path}\\{file_name}".format(current_path = cwd, file_name=file_name)

def plot3d_nodes(fig: Figure, nodes_list: List[dict]):
    """Função que realiza a plotagem em 3d dos nodos"""

    #Adiciona subplot à figura
    ax = fig.add_subplot(1, 2, 1, projection='3d')
    ax.grid(True) 

    #Listas com os pontos das coordenadas x,y e z
    xs = list()
    ys = list()
    zs = list()

    #Loop para adicionar os pontos nas listas
    for node in nodes_list:
        xs.append(node['x_pos'])
        ys.append(node['y_pos'])
        zs.append(node['z_pos'])

    #Adiciona as listas de pontos ao gráfico
    ax.scatter(xs, ys, zs)

    #Define as labels do gráfico
    ax.set_xlabel('Eixo X')
    ax.set_ylabel('Eixo Y')
    ax.set_zlabel('Eixo Z')
    return

def plot_xy_graph(fig: Figure, tension_before: list, tension_after: list, tension_diff: list):
    """Função que realiza a plotagem em gráfico xy"""

    #Adiciona subplot à figura
    ax = fig.add_subplot(1, 2, 2)
    ax.grid(True)

    x_axis = [x+1 for x in range(len(tension_before))]
    #Adiciona as lista de pontos ao gráfico
    ax.plot(
        x_axis,
        tension_before,
        linestyle='dashed', 
        marker='o', 
        linewidth=1, 
        markersize=3, 
        color='green', 
        label='\u03C3x antes da rotação')

    #Adiciona as lista de pontos ao gráfico
    ax.plot(
        x_axis,
        tension_after,
        linestyle='dashed', 
        marker='o', 
        linewidth=1, 
        markersize=3, 
        color='red', 
        label='\u03C3x depois da rotação')

    #Adiciona as lista de pontos ao gráfico
    ax.plot(
        x_axis,
        tension_diff,
        linestyle='dashed', 
        marker='o', 
        linewidth=1, 
        markersize=3, 
        color='blue', 
        label='Diferença das tensões antes e depois')


    #Define as labels do gráfico
    ax.set_xlabel('ID do nodo')
    ax.set_ylabel('Tensão')

    

    return
