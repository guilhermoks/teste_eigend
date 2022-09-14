from definitions import *
from utils import *
import matplotlib.pyplot as plt


def main():
    #--------------- ETAPA 1 ---------------#
    # 1) Importe os arquivos fornecidos
    node_file_path = get_file_path('node.xlsx')
    stress_file_path = get_file_path('stress.xlsx')
    
    nodes_list = import_xlsx(node_file_path, node_colums, first_row=2)
    stress_list = import_xlsx(stress_file_path, stress_colums, first_row=2)
    
    # 2) Calcule a tensão de von Mises
    tension_list = list(map(compute_von_mises_tension, stress_list))
    
    
    #--------------- ETAPA 2 ---------------#
    # 1) Construa uma variável que deverá conter três valores
    # 2) Atribua o valor de 7° para rotação em X, 0° para rotação em Y e 0° para rotação em Z
    # 3) Calcule e armazene a matriz de rotação
    # 4) Rotacione a tensão [𝜎] para cada nó da variável correspondente ao arquivo stress.xlsm
    
    rotation_variable = {
        'new_sx': compute_tension_with_rotation(7, stress_list),
        'new_sy': compute_tension_with_rotation(0, stress_list),
        'new_sz': compute_tension_with_rotation(0, stress_list)      
    }

    # 5) Refaça a etapa 1.2 para os novos valores de tensão obtidos na etapa 2.4;
    # 6) Subtraia o resultado da etapa 1.2 pelo da etapa 2.5.
    tension_diff_list = get_tension_diff_list(rotation_variable, stress_list, tension_list)

    # 7) Faça uma plotagem em dois subplots
    fig = plt.figure(figsize=(17, 6))
    fig.suptitle('Teste prático Eigendauer')

    # 7.a) Plot 3D com todos os nós fornecidos no arquivo node.xlsm
    plot3d_nodes(fig, nodes_list)

    # 7.b) Gráfico XY
    sx_before = [node['sx'] for node in stress_list] #Lista com 𝜎x original
    plot_xy_graph(fig, sx_before, rotation_variable['new_sx'], tension_diff_list) #Plota gráfico com as tensões

    #mostra janela com os gráficos
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()