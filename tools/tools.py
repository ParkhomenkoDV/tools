import os
import time
import multiprocessing as mp
import threading as th

from tqdm import tqdm
from colorama import Fore
import pandas as pd
import numpy as np
from numpy import array, arange, linspace
import matplotlib.pyplot as plt

from decorators import timeit


def find(name: str, path: str = os.getcwd()) -> list[str]:
    """Поиск файла/директории по пути"""
    is_file = True if '.' in name else False
    result = list()
    for root, dirs, files in os.walk(path):
        if not is_file:
            for dir in dirs:
                if name in dir:
                    result.append(os.path.join(root, dir))
        for file in files:
            if name in file:
                result.append(os.path.join(root, file))
    return result


def clear_dir(dir: str):
    """Удаление файлов и директории в указанной директории"""
    assert isinstance(dir, str), f'"{dir}" is not str'
    assert os.path.exists(dir), f'"{dir}" directory is not exists'
    assert os.path.isdir(dir), f'"{dir}" is not a directory'

    for file in os.listdir(dir):
        path = os.path.join(dir, file)
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                clear_dir(path)
                os.rmdir(path)
            else:
                raise Exception(f'"{path}" is not a file or a directory')
        except Exception as exception:
            print(f"Failed to delete {path}. Reason: {exception}")


def isnum(s, type_num: str = 'float') -> bool:
    """Проверка на число"""
    if type(s) is not str: s = str(s)
    if type_num.lower() in ('int', 'integer'):
        try:
            int(s)
        except ValueError:
            return False
        else:
            return True
    elif type_num.lower() in ('float', 'real'):
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True
    else:
        print('type_num = "int" or "float"'), exit()
    # finally: print('check isnum() done')


def isiter(i) -> bool:
    """Проверка на итератор"""
    try:
        for _ in i:
            return True
    except:
        return False


# формируем список из всех римских чисел и новых комбинаций
all_roman = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'),
             (90, 'XC'), (50, 'L'), (40, 'XL'),
             (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]


def to_roman(num: int) -> str:
    """Перевод в римскую систему счисления"""
    roman = ''
    while num > 0:
        for i, r in all_roman:
            while num >= i:  # пока наше число больше или равно числу из словаря
                roman += r  # добавляем соответствующую букву в римское число
                num -= i  # вычитаем словарное число из нашего числа
    return roman


def to_dec(rom: str) -> int:
    """Перевод в десятичную систему счисления"""
    dec = 0
    for i, r in all_roman:
        while rom.startswith(r):  # пока римское число начинается буквы из словаря
            dec += i  # увеличиваем десятичное число на соответствующее значение из словаря
            rom = rom[len(r):]  # убираем найденную букву из римского числа
    return dec


def rounding(s, n=0) -> float:
    """Округление до n значащих цифр"""
    if isnum(s) is False:
        print(Fore.RED + 'can not round not a num!')
    else:
        return float('{:g}'.format(float('{:.{p}g}'.format(s, p=n))))


def check_brackets(s: str) -> bool:
    """Проверка на верность постановки скобок"""
    temp = list()
    for i in s:
        if i in ('(', '{', '['):
            temp.append(i)
        else:
            if temp[-1] + i in ('()', '[]', '{}'):
                temp = temp[:-1]
            else:
                return False
    return True


def correlation(data, method='pearson', dropna=False, **kwargs):
    assert type(method) is str, 'type(method) is str'
    assert method.strip().lower() in ('pearson', 'kendall', 'spearman'), \
        'method must be "pearson" or "kendall" or "spearman"!'

    if type(data) is pd.DataFrame:
        cor = data[1:].corr(method=method)
    elif type(data) is np.ndarray:
        cor = np.corrcoef(data)

    if dropna:  # удаление всех строк и столбцов, содержащие только nan
        cor.dropna(how='all', axis=0, inplace=True)  # удаление всех строк содержащих только nan
        cor.dropna(how='all', axis=1, inplace=True)  # удаление всех столбцов содержащих только nan
    return cor


def show_correlation(df, show_num=True, cmap='bwr', fmt=4, savefig=False, **kwargs):
    """Построение матрицы корреляции"""

    assert type(fmt) is int, 'type(fmt) is int'
    assert 1 <= fmt, '1 <= fmt'

    cor = correlation(df, **kwargs)
    if cor is None: return
    if not isnum(fmt, type_num='int') or fmt < 0: fmt = 4
    cor = cor.round(fmt)

    fig, ax = plt.subplots(figsize=kwargs.get('figsize', (12, 12)))
    plt.suptitle('Correlation', fontsize=16, fontweight='bold')
    ax.set_aspect('equal')
    im = ax.imshow(cor, interpolation='nearest',
                   cmap=cmap)  # RGB: 'turbo', # blue vs red: 'bwr', # 2side: 'twilight','twilight_shifted'

    clrbar = fig.colorbar(im, orientation='vertical')
    clrbar.ax.tick_params(labelsize=12)

    clrbar.set_label('Color Intensity []', fontsize=14)
    clrbar.set_ticks(linspace(-1, 1, 21))

    ax.set_xticks(range(len(cor.columns)), cor.columns, fontsize=12, rotation=90)
    ax.set_yticks(range(len(cor.columns)), cor.columns, fontsize=12, rotation=0)
    ax.tick_params(top=False, bottom=False, labeltop=False, labelbottom=True)
    plt.grid(False)

    if show_num:
        for row in range(len(cor.columns)):
            for col in range(len(cor.columns)):
                ax.text(row, col, cor.to_numpy()[row, col],
                        ha="center", va="center", color='black', fontsize=12, rotation=45)

    plt.show()


@timeit()
def run_cpu_tasks_in_parallel(*tasks):
    processes = list()
    for task in tasks:
        if len(task) == 1:
            processes.append(mp.Process(target=task[0]))
        elif len(task) == 2:
            processes.append(mp.Process(target=task[0], args=task[1]))
        else:
            raise 'Incorrect values'
    for process in processes: process.start()
    for process in processes: process.join()


@timeit()
def run_thread_tasks_in_parallel(*tasks):
    threads = list()
    for task in tasks:
        if len(task) == 1:
            threads.append(th.Thread(target=task[0]))
        elif len(task) == 2:
            threads.append(th.Thread(target=task[0], args=task[1]))
        else:
            raise 'Incorrect values'
    for thread in threads: thread.start()
    for thread in threads: thread.join()


def test_f1():
    time.sleep(1)
    a = list()
    for i in range(100_000): a.append(i ** 0.5)
    del a


def test_f2():
    time.sleep(2)
    a = list()
    for i in range(100_000): a.append(i ** 0.5)
    del a


def meke_calc(n):
    time.sleep(n)
    return n


if __name__ == '__main__':
    clear_dir('t')
    exit()

    run_cpu_tasks_in_parallel((test_f1,), (test_f2,))
    run_thread_tasks_in_parallel((test_f1,), (test_f2,))

    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.map(meke_calc, [1, 2, 3])
    print(f'results: {results}')

    exit()

    print(isnum(str(nan)))
    print(rounding(-23456734567.8, 2))  # bug
