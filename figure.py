import matplotlib.pyplot as plt


def main(art1, art2):
    """
    :param art1: word frequency
    :param art2: word emotion preference
    :return: draw figures
    """
    _, fg1 = plt.subplots()
    plt.title("单词权重与情感倾向")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    x = list(art1.keys())
    y1 = list(art1.values())
    all_freq = sum(y1)
    y1 = [v / all_freq for v in y1]
    y2 = list(art2.values())
    plt.xticks(rotation=90)
    fg2 = fg1.twinx()
    fg1.bar(x, y1, width=0.1, color='#0080EE')
    fg2.plot(x, y2, color='#EE4000')
    plt.show()
