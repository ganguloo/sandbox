import argparse
import itertools
import os

def get_lex_mapping(n):
    """Genera el diccionario para el orden lexicográfico usual."""
    return {i: format(i, f'0{n}b') for i in range(2**n)}

def get_gray_mapping(n):
    """Genera el diccionario para el código Gray usual."""
    return {i: format(i ^ (i >> 1), f'0{n}b') for i in range(2**n)}

def get_mapping(n, orden):
    """Despachador modular de ordenamientos."""
    if orden == 'lex':
        return get_lex_mapping(n)
    elif orden == 'gray':
        return get_gray_mapping(n)
    else:
        raise ValueError(f"Ordenamiento '{orden}' no implementado.")

def generar_poliedros(n, orden, k, indicator, use_ranges, lb, ub):
    # 1. Ajuste y validación de las cotas
    max_val = 2**n - 1
    lb = 0 if lb is None else lb
    ub = max_val if ub is None else ub

    if lb < 0 or ub > max_val or lb > ub:
        print(f"Error: Las cotas deben cumplir 0 <= lb <= ub <= {max_val}.")
        return

    # 2. Obtener el mapeo de enteros a vectores binarios
    mapping = get_mapping(n, orden)

    # 3. Crear el directorio base (añadimos las cotas al nombre si no son las por defecto)
    folder_name = f"poly_{orden}_n{n}_k{k}"
    if indicator:
        folder_name += "_ind"
    if lb != 0 or ub != max_val:
        folder_name += f"_lb{lb}_ub{ub}"

    os.makedirs(folder_name, exist_ok=True)

    # 4. Validar y generar las combinaciones de límites
    elementos_disponibles = ub - lb + 2
    if 2 * k > elementos_disponibles:
        print(f"Error matemático: No es posible formar {k} intervalos disjuntos en el rango [{lb}, {ub}].")
        return

    combinaciones = itertools.combinations(range(lb, ub + 2), 2 * k)
    dim_output = n + k if indicator else n
    archivos_creados = 0

    # 5. Iterar sobre cada configuración válida de intervalos
    for file_id, combo in enumerate(combinaciones, start=1):
        intervalos = [(combo[2*i], combo[2*i+1] - 1) for i in range(k)]

        # Determinar el nombre del archivo según el flag --ranges
        if use_ranges:
            str_rangos = "_".join([f"{start}-{end}" for start, end in intervalos])
            base_filename = f"poly_{orden}_n{n}_k{k}_{str_rangos}.poi"
        else:
            base_filename = f"poly_{orden}_n{n}_k{k}_id{file_id}.poi"

        filename = os.path.join(folder_name, base_filename)

        with open(filename, 'w') as f:
            f.write(f"DIM =  {dim_output}\n\n")
            f.write("CONV_SECTION\n")

            for idx_intervalo, (start, end) in enumerate(intervalos):
                # Generar el one-hot encoding si el flag está activado
                if indicator:
                    hot_encoding = ["0"] * k
                    hot_encoding[idx_intervalo] = "1"
                    hot_str = "  " + " ".join(hot_encoding)
                else:
                    hot_str = ""

                # Imprimir cada vector del intervalo actual
                for i in range(start, end + 1):
                    bin_vec_str = " ".join(mapping[i])
                    f.write(f"({i}) {bin_vec_str}{hot_str}\n")

                f.write("\n")

            f.write("END\n")

        archivos_creados += 1

    print(f"Proceso finalizado. Se generaron {archivos_creados} archivos en la carpeta '{folder_name}/'.")

def main():
    parser = argparse.ArgumentParser(description="Generador de estructuras poliédricas para ordenamientos binarios.")

    # Argumentos posicionales (obligatorios)
    parser.add_argument("n", type=int, help="Dimensión del vector binario (entero positivo).")
    parser.add_argument("orden", type=str, choices=['lex', 'gray'], help="Tipo de ordenamiento (ej. 'lex', 'gray').")
    parser.add_argument("k", type=int, help="Número de intervalos disjuntos (entero positivo).")

    # Argumentos opcionales (flags)
    parser.add_argument("--indicator", action="store_true", help="Activa el flag para agregar el one-hot encoding de los intervalos.")
    parser.add_argument("--ranges", action="store_true", help="Nombra los archivos usando los rangos (ej. 10-15_20-25) en lugar de un ID numérico.")
    parser.add_argument("--lb", type=int, default=None, help="Cota inferior del rango total (opcional, por defecto es 0).")
    parser.add_argument("--ub", type=int, default=None, help="Cota superior del rango total (opcional, por defecto es 2^n - 1).")

    args = parser.parse_args()

    if args.n <= 0 or args.k <= 0:
        print("Error: Los argumentos 'n' y 'k' deben ser enteros estrictamente positivos.")
        return

    generar_poliedros(args.n, args.orden, args.k, args.indicator, args.ranges, args.lb, args.ub)

if __name__ == "__main__":
    main()
