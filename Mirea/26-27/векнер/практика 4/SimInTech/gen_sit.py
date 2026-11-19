"""Генератор проектов SimInTech (.xprt) для ПР4, вариант 13.

Шаблоны блоков берутся из XML-проектов, сохранённых самим SimInTech
(templates/blocks.xprt и templates/pr3.xprt). Схемы собираются из
ступеньки, сумматоров с весовыми коэффициентами, интеграторов, блока
передаточной функции, временного графика и блока «В файл».
Запуск: python gen_sit.py  -> ПР4_1.xprt, ПР4_2.xprt
"""
import copy
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, 'templates')
Q = '`'


def load(fn):
    t = open(fn, encoding='utf-8-sig').read().replace('\r\n', '\n')
    return t.split('\n')


def top_objects(L):
    res, st = [], None
    for i, l in enumerate(L):
        if l == '  <object>':
            st = i
        elif l == '  </object>' and st is not None:
            res.append((st, i))
            st = None
    return res


def obj_by_name(L, name):
    for a, b in top_objects(L):
        if L[a + 1] == f'   <name>{Q}{name}{Q}</name>':
            return L[a:b + 1]
    raise KeyError(name)


def fmt(v):
    if hasattr(v, 'item'):          # numpy-скаляры
        v = v.item()
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return repr(v)
    return str(v)


def port_sign(c):
    if c == 1:
        return '+'
    if c == -1:
        return '−'
    return f'{c:.3f}'.rstrip('0').rstrip('.')


def vec(vals):
    return '[' + ' , '.join(fmt(v) for v in vals) + ']'


def mat(vals):
    return '[[' + ' , '.join(fmt(v) for v in vals) + ']]'


def pts(points):
    return '[' + ','.join(f'({fmt(x)} , {fmt(y)})' for x, y in points) + ']'


class Obj:
    def __init__(self, lines):
        self.L = list(lines)

    def _sec(self, tag, indent='   '):
        s = e = None
        for i, l in enumerate(self.L):
            if l == f'{indent}<{tag}>' and s is None:
                s = i
            elif l == f'{indent}</{tag}>' and s is not None:
                e = i
                break
        return s, e

    def set_top(self, tag, value):
        pat = re.compile(rf'^   <{tag}>.*</{tag}>$|^   <{tag}></{tag}>$')
        for i, l in enumerate(self.L):
            if pat.match(l):
                self.L[i] = f'   <{tag}>{Q}{value}{Q}</{tag}>' if value != '' else f'   <{tag}></{tag}>'
                return
        raise KeyError(tag)

    def _set_prop(self, section, name, value, text=False):
        s, e = self._sec(section)
        for i in range(s, e):
            if self.L[i] == f'     <name>{Q}{name}{Q}</name>':
                done = False
                for j in range(i, e):
                    if self.L[j].strip() == '</data>':
                        break
                    if not done and self.L[j].startswith('     <value>'):
                        self.L[j] = f'     <value>{Q}{value}{Q}</value>'
                        done = True
                    elif text and self.L[j].startswith('     <textvalue>`'):
                        # textvalue — формула параметра, SimInTech берёт её в приоритет
                        self.L[j] = f'     <textvalue>{Q}{value}{Q}</textvalue>'
                if done:
                    return
        raise KeyError((section, name))

    def vprop(self, name, value):
        self._set_prop('visual_props', name, value)

    def cprop(self, name, value):
        self._set_prop('custom_props', name, value, text=True)

    def set_points_tag(self, tag, points):
        s, e = self._sec(tag)
        for j in range(s, e):
            if self.L[j].startswith('    <value>'):
                self.L[j] = f'    <value>{Q}{pts(points)}{Q}</value>'

    def set_ports(self, ports):
        s, e = self._sec('ports')
        out = ['   <ports>']
        for p in ports:
            out += ['    <port>',
                    f'     <name>{Q}{p["name"]}{Q}</name>',
                    f'     <side>{Q}{p["side"]}{Q}</side>',
                    f'     <x>{Q}{fmt(p["x"])}{Q}</x>',
                    f'     <y>{Q}{fmt(p["y"])}{Q}</y>',
                    f'     <auto>{Q}1{Q}</auto>',
                    f'     <mode>{Q}{p["mode"]}{Q}</mode>',
                    f'     <type>{Q}0{Q}</type>',
                    f'     <itemid>{Q}-1{Q}</itemid>',
                    f'     <inversebyte>{Q}0{Q}</inversebyte>',
                    f'     <center>{Q}0{Q}</center>',
                    f'     <x_glob>{Q}{fmt(p["xg"])}{Q}</x_glob>',
                    f'     <y_glob>{Q}{fmt(p["yg"])}{Q}</y_glob>',
                    f'     <clonable>{Q}0{Q}</clonable>',
                    f'     <invisible>{Q}0{Q}</invisible>',
                    f'     <allsurface>{Q}0{Q}</allsurface>',
                    f'     <portisoff>{Q}0{Q}</portisoff>',
                    f'     <canmove>{Q}0{Q}</canmove>',
                    f'     <angbyline>{Q}0{Q}</angbyline>',
                    '    </port>']
        out.append('   </ports>')
        self.L[s:e + 1] = out


# ------------------------------------------------------------------ шаблоны
BL = load(os.path.join(TPL, 'blocks.xprt'))
PR = load(os.path.join(TPL, 'pr3.xprt'))
T = {
    'step': obj_by_name(BL, 'Step_source_1'),
    'sum': obj_by_name(BL, 'Add_oper_0'),
    'int': obj_by_name(BL, 'Integrator_0'),
    'graph': obj_by_name(BL, 'TimeGraphic_0'),
    'file': obj_by_name(BL, 'ToFile_0'),
    'tf': obj_by_name(PR, 'w1'),
    'wire': obj_by_name(PR, 'wx1'),
    'wchild': obj_by_name(PR, 'wg10'),
}
objs0 = top_objects(BL)
HEAD = BL[:objs0[0][0]]
TAIL = BL[objs0[-1][1] + 1:]


class Block:
    """Блок схемы. ports: список (name, side, mode) — порядок как в SimInTech."""

    def __init__(self, kind, name, cx, cy, w, h, ports_in, out_first, label='',
                 params=None):
        self.kind, self.name, self.cx, self.cy, self.w, self.h = kind, name, cx, cy, w, h
        self.label = label
        self.params = params or {}
        n = len(ports_in)
        self.ports = []
        outp = dict(name='outport', side=2, mode=1, x=0.5, y=0,
                    xg=cx + w / 2, yg=cy)
        ins = []
        for k, pn in enumerate(ports_in):
            ry = -0.5 + (k + 0.5) / n if n else 0
            ins.append(dict(name=pn, side=0, mode=0, x=-0.5, y=ry,
                            xg=cx - w / 2, yg=cy + ry * h))
        if kind in ('graph', 'file'):
            self.ports = ins
        elif kind == 'step':
            self.ports = [outp]
        elif out_first:
            outp['name'] = ' '
            self.ports = [outp] + ins
        else:
            self.ports = ins + [outp]

    def out_idx(self):
        return [i for i, p in enumerate(self.ports) if p['mode'] == 1][0]

    def in_idx(self, k):
        return [i for i, p in enumerate(self.ports) if p['mode'] == 0][k]

    def port_xy(self, idx):
        p = self.ports[idx]
        return p['xg'], p['yg']

    def render(self, uid):
        o = Obj(copy.deepcopy(T[self.kind]))
        o.set_top('name', self.name)
        o.vprop('Name', self.name)
        lab_y = self.cy - self.h / 2 - 18
        P = [(self.cx, self.cy), (self.cx + self.w / 2, self.cy),
             (self.cx, self.cy - self.h / 2), (self.cx, lab_y)]
        o.set_points_tag('points', P)
        o.vprop('Points', pts(P))
        o.vprop('Width', fmt(self.w))
        o.vprop('Height', fmt(self.h))
        o.set_top('width', fmt(self.w))
        o.set_top('height', fmt(self.h))
        o.vprop('LabelText', self.label)
        o.vprop('BlockIndex', str(uid))
        o.vprop('UID', str(uid))
        o.set_top('uid', str(uid))
        o.set_top('indexstr', str(uid))
        for k, v in self.params.items():
            o.cprop(k, v)
        o.set_ports(self.ports)
        return o.L


class Scheme:
    def __init__(self):
        self.blocks = []
        self.nets = []   # (src_block, [(dst_block, in_k, opts)], opts)

    def add(self, b):
        self.blocks.append(b)
        return b

    # фабрики
    def step(self, name, cx, cy, t0=0.0, yk=1.0):
        return self.add(Block('step', name, cx, cy, 32, 32, [], False, 'u(t) = 1(t)',
                              {'t': vec([t0]), 'y0': vec([0]), 'yk': vec([yk])}))

    def summ(self, name, cx, cy, coefs, label=''):
        n = len(coefs)
        h = max(32, 16 * n)
        return self.add(Block('sum', name, cx, cy, 32, h, [port_sign(c) for c in coefs],
                              True, label, {'a': vec(coefs)}))

    def integ(self, name, cx, cy, label=''):
        return self.add(Block('int', name, cx, cy, 32, 32, ['inport'], False, label,
                              {'k': vec([1]), 'x0': vec([0])}))

    def tf(self, name, cx, cy, num_asc, den_asc, label='', w=160):
        return self.add(Block('tf', name, cx, cy, w, 40, ['inport'], False, label,
                              {'b': mat(num_asc), 'a': mat(den_asc), 'y0': mat([0] * (len(den_asc) - 1))}))

    def graph(self, name, cx, cy, n, label=''):
        h = max(32, 16 * n)
        return self.add(Block('graph', name, cx, cy, 48, h,
                              [f'inport_{k + 1}' for k in range(n)], False, label,
                              {'InPortCount': str(n)}))

    def tofile(self, name, cx, cy, n, fname, step=0.02):
        h = max(32, 16 * n)
        return self.add(Block('file', name, cx, cy, 32, h,
                              [f'inport_{k + 1}' for k in range(n)], False, fname,
                              {'step': vec([step]), 'filename': fname, 'count': str(n)}))

    def net(self, src, dsts, dx=16):
        """dsts: список (block, in_k) или (block, in_k, lane_y, approach)."""
        self.nets.append((src, dsts, dx))

    # --------------------------------------------------------------- render
    def render_page(self, endtime, title):
        out = []
        blocks = self.blocks
        idx = {b.name: i for i, b in enumerate(blocks)}
        body = []
        for i, b in enumerate(blocks):
            body += b.render(i + 1)
        wires = []
        wid = 0
        for src, dsts, dx in self.nets:
            sp = src.out_idx()
            sx, sy = src.port_xy(sp)
            B = (sx + dx, sy)
            root_index = len(blocks) + len(wires)
            for j, d in enumerate(dsts):
                blk, k = d[0], d[1]
                lane = d[2] if len(d) > 2 else None
                appr = d[3] if len(d) > 3 else 8
                ip = blk.in_idx(k)
                ex, ey = blk.port_xy(ip)
                path = [B]
                if ex - appr > B[0] and lane is None:
                    if ey != B[1]:
                        path += [(B[0], ey)]
                else:
                    L_ = lane if lane is not None else ey
                    path += [(B[0], L_), (ex - appr, L_), (ex - appr, ey)]
                # убрать вырожденные точки
                clean = [path[0]]
                for p in path[1:]:
                    if p != clean[-1]:
                        clean.append(p)
                path = clean
                wid += 1
                wname = f'w{wid}'
                if j == 0:
                    o = Obj(copy.deepcopy(T['wire']))
                    inner = path            # B и изломы
                    base = [(sx, sy)] + path + [(ex, ey)]
                    o.set_top('start_bl_index', idx[src.name])
                    o.set_top('start_bl_name', src.name)
                    o.set_top('start_port_index', sp)
                    o.set_top('start_x', fmt(sx))
                    o.set_top('start_y', fmt(sy))
                    root_name = wname
                else:
                    o = Obj(copy.deepcopy(T['wchild']))
                    inner = path[1:]
                    base = path + [(ex, ey)]
                    o.set_top('parent_wire_index', root_index)
                    o.set_top('parent_wire_name', root_name)
                    o.set_top('start_x', fmt(B[0]))
                    o.set_top('start_y', fmt(B[1]))
                o.set_top('name', wname)
                o.vprop('Name', wname)
                o.set_top('point_count', len(inner))
                o.set_points_tag('points', inner)
                o.vprop('Points', pts(inner))
                o.set_points_tag('base_points', base)
                o.set_top('end_bl_index', idx[blk.name])
                o.set_top('end_bl_name', blk.name)
                o.set_top('end_port_index', ip)
                o.set_top('end_x', fmt(ex))
                o.set_top('end_y', fmt(ey))
                wires.append(o.L)
        for w in wires:
            body += w
        head = list(HEAD)
        # параметры расчёта
        sets = {'hmin': '1E-7', 'hmax': '0.01', 'intmet': 'im_rk45.dll', 'endtime': fmt(endtime),
                'relerr': '1E-8', 'abserr': '1E-10'}
        for i, l in enumerate(head):
            m = re.match(rf'^     <name>{Q}(\w+){Q}</name>$', l)
            if m and m.group(1) in sets and i < 400:
                for j in range(i, i + 8):
                    if head[j].startswith('     <value>'):
                        head[j] = f'     <value>{Q}{sets[m.group(1)]}{Q}</value>'
                        break
        for i, l in enumerate(head):
            if l.startswith('   <name>') and i > 900:
                head[i] = f'   <name>{Q}{title}{Q}</name>'
                break
        return '\n'.join(head + body + TAIL)


def save(text, fn):
    with open(fn, 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write(text)
