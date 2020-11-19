import platform
osName = platform.platform().split('-')[0]


def show(massage, level=0, sign='>', nlb=False, nla=False, signAfter=False):
    nspace = {i:6+i for i in range(100)}
    nsign  = {0:2, 1:2, 2:3, 3:3, 4:3 , 5:3 , 6:4 , 7:4}
    nsign.update({i :5 for i in range(8,100)})

    if nla and nlb:
        line = '\n' + ' '*nspace[level] + f'{sign}'*nsign[level]  + f' {massage}' + '\n'
    elif nla:
        line = ' '*nspace[level] + f'{sign}'*nsign[level]  + f' {massage}' + '\n'
    elif nlb:
        line = '\n' + ' '*nspace[level] + f'{sign}'*nsign[level]  + f' {massage}'
    else:
        line = ' '*nspace[level] + f'{sign}'*nsign[level]  + f' {massage}'

    if osName == 'Windows':
        print(line.encode('cp950', 'ignore').decode('CP950'))
    elif osName == 'Darwin':
        print(line)

    else:
        print('不屬於上述任何環境，後續可能有問題，也可能沒有')
