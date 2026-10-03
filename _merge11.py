import io, shutil, os

src = r'E:\FPGA知识库\Verilog语法\2-Verilog入门学习笔记.md'
bak = src + '.bak'

if not os.path.exists(bak):
    for i in range(3):
        try:
            shutil.copy2(src, bak)
            break
        except Exception as e:
            print('backup attempt %d failed: %r' % (i + 1, e))
print('backup exists:', os.path.exists(bak))

t = io.open(src, encoding='utf-8').read()

h_data = '# 10.数据类型'
h_num = '# 11.数字的表示格式'
h_next = '# 12.if语句'
a, b, c = t.index(h_data), t.index(h_num), t.index(h_next)
assert a < b < c


def demote(text):
    out = []
    for ln in text.split('\n'):
        if ln.startswith('### '):
            out.append('#### ' + ln[4:])
        elif ln.startswith('## '):
            out.append('### ' + ln[3:])
        else:
            out.append(ln)
    return '\n'.join(out)


body_old = t[a:b].strip('\n')          # starts with '# 10.数据类型'
num_old = t[b:c].strip('\n')           # starts with '# 11.数字的表示格式'

body_old = body_old.replace(h_data, '## 1. 数据类型（原笔记第 10 章）', 1)
num_old = num_old.replace(h_num, '## 2. 数字的表示格式（原笔记第 11 章）', 1)

new_ch11 = (
    '# 11. 数据类型与数字表示\n'
    '\n'
    '> 本章由原笔记的"数据类型"与"数字的表示格式"两章合并而成（新目录把它们并为一章），'
    '本节内的编号保持原样，只做层级下调。\n'
    '> ⭐【重点·重复】"常量要指定位宽"在第 6 章（拼接）、第 10 章（运算符）都出现过，'
    '这里再讲一次，是初学最常踩的坑之一。\n'
    '\n'
    + demote(body_old)
    + '\n\n---\n\n'
    + demote(num_old)
    + '\n\n'
)

newt = t[:a] + new_ch11 + '\n---\n\n' + t[c:]
io.open(src, 'w', encoding='utf-8', newline='\n').write(newt)
print('OK new length', len(newt))
