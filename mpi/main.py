#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mpi4py import MPI
import numpy as np
import os, argparse, math, time
from pathlib import Path

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def chunks(lst, k):
    """Divide lst en k sublistas (lo más balanceadas posible)."""
    n = len(lst)
    base, sobra = divmod(n, k)
    out = []
    start = 0
    for i in range(k):
        extra = 1 if i < sobra else 0
        end = start + base + extra
        out.append(lst[start:end])
        start = end
    return out

# ------------------ Parte 1: π por Monte Carlo (distribuido) ------------------

def pi_montecarlo(total_muestras: int, seed_base: int = 1234):
    """
    Cada proceso genera 'muestras_locales' puntos uniformes en el cuadrado [0,1]x[0,1]
    y cuenta cuántos caen dentro del círculo de radio 1 (x^2+y^2 <= 1).
    Se combinan los aciertos con MPI.REDUCE para estimar π = 4 * hits / total.
    """
    # repartir el trabajo
    muestras_locales = total_muestras // size
    if rank == size - 1:
        # el último proceso se queda con el "resto"
        muestras_locales += total_muestras % size

    # RNG independiente por proceso
    seed = seed_base + rank * 1000003
    rng = np.random.default_rng(seed)
    x = rng.random(muestras_locales, dtype=np.float64)
    y = rng.random(muestras_locales, dtype=np.float64)
    hits_locales = np.count_nonzero(x*x + y*y <= 1.0)

    # Reducimos la suma de hits a rank 0
    hits_totales = comm.reduce(hits_locales, op=MPI.SUM, root=0)

    if rank == 0:
        pi_est = 4.0 * hits_totales / float(total_muestras)
        return pi_est
    return None

# --------------- Parte 2: Conteo distribuido de líneas en archivos ------------

def contar_lineas_en_archivo(path: Path) -> int:
    try:
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0

def contar_lineas_distribuido(archivos):
    """
    rank 0 reparte la lista de archivos con Scatter (listas de Python),
    cada proceso cuenta localmente, y luego rank 0 recoge resultados con Gather.
    Devuelve un dict filename->linecount y un total global (en rank 0).
    """
    if rank == 0:
        # normalizamos a Path
        archivos = [Path(a) for a in archivos]
        trozos = chunks(archivos, size)
    else:
        trozos = None

    # cada proceso recibe su sublista
    mis_archivos = comm.scatter(trozos, root=0)

    # conteo local
    resultados_locales = {}
    total_local = 0
    for p in mis_archivos:
        c = contar_lineas_en_archivo(p)
        resultados_locales[str(p)] = c
        total_local += c

    # rank 0 junta todos los dicts
    resultados = comm.gather(resultados_locales, root=0)
    total_global = comm.reduce(total_local, op=MPI.SUM, root=0)

    if rank == 0:
        # combinar dicts (si un mismo archivo aparece, sumamos por si acaso)
        combinado = {}
        for d in resultados:
            for k, v in d.items():
                combinado[k] = combinado.get(k, 0) + v
        return combinado, total_global
    return None, None

# ------------------------- Utilidades demo / CLI ------------------------------

def crear_archivos_dummy(carpeta: Path, n_archivos: int, lineas_por_archivo: int):
    """
    Crea N archivos de texto con 'lineas_por_archivo' líneas cada uno.
    SOLO se ejecuta en rank 0 para evitar colisiones.
    """
    if rank != 0:
        return
    carpeta.mkdir(parents=True, exist_ok=True)
    for i in range(n_archivos):
        path = carpeta / f"datos{i}.txt"
        with path.open('w', encoding='utf-8') as f:
            for j in range(lineas_por_archivo):
                f.write(f"Linea {j} del archivo {i}\n")

def main():
    parser = argparse.ArgumentParser(description="Demo MPI: π Monte Carlo + conteo distribuido de líneas")
    parser.add_argument("--pi-samples", type=int, default=5_000_000,
                        help="Número total de muestras Monte Carlo para π (se reparten entre procesos)")
    parser.add_argument("--files", nargs="*", default=[],
                        help="Lista de archivos a contar. Si se omite y --make-dummy se usa, se crean en ./data")
    parser.add_argument("--make-dummy", action="store_true",
                        help="Crear archivos de prueba en ./data (solo rank 0) si no hay lista --files")
    parser.add_argument("--dummy-n", type=int, default=4, help="Cantidad de archivos dummy")
    parser.add_argument("--dummy-lines", type=int, default=100000, help="Líneas por archivo dummy")
    args = parser.parse_args()

    # ------------------- Cálculo distribuido de π -------------------
    if rank == 0:
        print(f"[MPI] Procesos: {size}")
        print(f"[π] Monte Carlo con {args.pi_samples:,} muestras totales...")
    comm.Barrier()
    t0 = MPI.Wtime()
    pi_est = pi_montecarlo(args.pi_samples)
    t1 = MPI.Wtime()
    if rank == 0:
        print(f"[π] π ≈ {pi_est:.12f}  | tiempo: {t1 - t0:.3f} s\n")

    # --------------- Conteo distribuido de líneas -------------------
    # Preparación de archivos (opcional)
    archivos = args.files
    if not archivos and args.make_dummy:
        data_dir = Path("./data")
        crear_archivos_dummy(data_dir, n_archivos=args.dummy_n, lineas_por_archivo=args.dummy_lines)
        # Sincronizamos para que todos vean los archivos creados (FS compartido)
        comm.Barrier()
        if rank == 0:
            # generamos lista
            archivos = [str(p) for p in sorted(data_dir.glob("datos*.txt"))]

    if rank == 0:
        if archivos:
            print(f"[I/O] Conteo distribuido de líneas en {len(archivos)} archivo(s)...")
        else:
            print("[I/O] No se proporcionaron archivos. Sáltandose esta parte.\n")
    comm.Barrier()

    if archivos:
        t2 = MPI.Wtime()
        detalle, total = contar_lineas_distribuido(archivos)
        t3 = MPI.Wtime()
        if rank == 0:
            print("[I/O] Resultados por archivo:")
            # Muestra algunos (o todos si son pocos)
            mostrar = min(len(detalle), 8)
            for i, (k, v) in enumerate(sorted(detalle.items())):
                if i < mostrar:
                    print(f"   - {k}: {v} líneas")
                else:
                    break
            if len(detalle) > mostrar:
                print(f"   ... y {len(detalle) - mostrar} más")
            print(f"[I/O] Total de líneas (global) = {total:,}  | tiempo: {t3 - t2:.3f} s\n")

    if rank == 0:
        print("✅ Demo MPI finalizada.")

if __name__ == "__main__":
    main()
