import copy

from clasesExtra import ItemLR1, SetItemsLR1
from clases import DescensoRecGramGram, AnalizadorLexico, ClaseNodo


class ConjuntoSjLR1(object):
    def __init__(self):
        self.j = -1
        self.sj = SetItemsLR1()


class AnalizadorLR1:
    def __init__(self, cad_gramatica):
        self.gram = cad_gramatica
        self.desc_rec_gg = DescensoRecGramGram(cad_gramatica)
        # self.a_lex = AnalizadorLexico(cad_gramatica, archivo_a_lex)

        self.num_renglones_ira = 0
        self.sigma = ""
        self.tabla_lr1 = list()
        self.v_t = list()
        self.v_n = list()
        self.v = list()

    # noinspection DuplicatedCode
    def crear_tabla_lr1(self):
        # result_first = set()
        # result_follow = set()

        # Conjunto de todos los Sj
        c = list()

        # Conjunto Sj
        conj_sj = ConjuntoSjLR1()

        # Conj temporal de Items
        conj_items = SetItemsLR1()

        # Sj sin analizar, quedan en cola
        q = list()

        if not self.desc_rec_gg.analizar_gramatica():
            return False

        iter_simbolos = list()

        pos_insert = 0
        for simb in self.desc_rec_gg.v_t:
            self.v.append(simb)
            self.v_t.append(simb)
            iter_simbolos.append(simb)
        self.v.append('$')
        for simb in self.desc_rec_gg.v_n:
            self.v.append(simb)
            self.v_n.append(simb)
            iter_simbolos.insert(pos_insert, simb)
            pos_insert += 1
        # iter_simbolos.pop(0)
        self.tabla_lr1.append(['-1' for j in range(0, len(self.v))])
        conj_items.agregar(ItemLR1(0, 0, '$'))

        j = 0

        # print("-" * 20)

        conj_sj.sj = self.cerradura_lr1(conj_items)

        # print(f"De la cerradura de S_0 obtuve {len(conj_sj.sj.conjunto)} elementos")

        conj_sj.j = j
        c.append(copy.deepcopy(conj_sj))
        q.append(copy.deepcopy(conj_sj))

        self.num_renglones_ira += 1

        # Contador de conjuntos sj
        j += 1

        # print("***************************************INCIIANDO ANALISIS DE SJ'S")
        while len(q) > 0:
            conj_sj = q.pop(0)

            # print(f"Analizando {conj_sj.j}")

            # Ahora se calcula el IrA del Sj con cada simbolo de V = V_t U V_n
            for simb in iter_simbolos:

                # Aux para guardar temporalmente el resultado de un IrA
                # print(f"\t---->{simb}")
                sj_aux = self.ir_a_lr1(conj_sj.sj, simb)
                # print(f"\t---->{simb} trajo un conj con {sj_aux.tamano()} elementos")
                if sj_aux.tamano() == 0:
                    continue

                # Verificar si este conjunto sj_aux ya existe en c
                existe = False

                for elem_sj in c:
                    if elem_sj.sj.tamano() == sj_aux.tamano():
                        if elem_sj.sj.igual_a(sj_aux):
                            existe = True

                            index_simb = self.v.index(simb)
                            if simb in self.v_t:
                                self.tabla_lr1[conj_sj.j][index_simb] = f"d{elem_sj.j}"
                            else:
                                self.tabla_lr1[conj_sj.j][index_simb] = elem_sj.j

                            self.num_renglones_ira += 1

                            break
                if not existe:
                    # Conjunto Sj
                    conj_sj_aux = ConjuntoSjLR1()
                    conj_sj_aux.sj = sj_aux
                    conj_sj_aux.j = j

                    index_simb = self.v.index(simb)
                    if simb in self.v_t:
                        self.tabla_lr1[conj_sj.j][index_simb] = f"d{j}"
                    else:
                        self.tabla_lr1[conj_sj.j][index_simb] = j

                    self.tabla_lr1.append(['-1' for j in range(0, len(self.v))])

                    self.num_renglones_ira += 1
                    j += 1

                    c.append(copy.deepcopy(conj_sj_aux))
                    q.append(copy.deepcopy(conj_sj_aux))

        # return c
        # print(f"Se obtuvieron {len(c)} conjuntos")
        # for linea in self.tabla_lr1:
        #     print(linea)

        for paquete_sj in c:
            # print(f"CHECANDO {paquete_sj.j}")
            # for conjunto_sj in paquete_sj.sj.conjunto:
            for item_LR1 in paquete_sj.sj.conjunto:
                no_regla = item_LR1.numero_regla
                # print(f"\tEvaluando {no_regla} con pos punto {conjunto_sj.pos_punto}")

                if len(self.desc_rec_gg.arr_reglas[no_regla].lista_lado_derecho) == item_LR1.pos_punto:

                    if no_regla != 0:
                        index_simb = self.v.index(item_LR1.simbolo)
                        self.tabla_lr1[paquete_sj.j][index_simb] = f"r{no_regla}"
                        continue

                    index_simb = self.v.index(item_LR1.simbolo)
                    self.tabla_lr1[paquete_sj.j][index_simb] = "ACEPTAR"

        return True

    def mover_lr1(self, c: SetItemsLR1, simbolo: str):
        # print(f"Moviendo {simbolo}")
        r = SetItemsLR1()

        for i in c.conjunto:
            lista = self.desc_rec_gg.arr_reglas[i.numero_regla].lista_lado_derecho

            # print(f"Intentando mover", sep=' ')
            # print(f"{self.desc_rec_gg.arr_reglas[i.numero_regla].info_simbolo.simbolo} ->", end=' ')
            # for index, l in enumerate(lista):
            #     if index == i.pos_punto:
            #         print("·", end=' ')
            #     print(f"{l.simbolo}", end=' ')
            # print(f", {i.simbolo}]")

            if i.pos_punto < len(lista):
                n = lista[i.pos_punto]
                if n.simbolo == simbolo:
                    r.agregar(ItemLR1(i.numero_regla, i.pos_punto + 1, i.simbolo))
        # print(f"Moviendo {simbolo} se obtuvieron:\n\t")
        # for item in r.conjunto:
        #     print(item.numero_regla, item.pos_punto, item.simbolo)
        return r

    def cerradura_lr1(self, c: SetItemsLR1):
        # print(f"Aplicando cerradura a un conjunto con {len(c.conjunto)} itmems")
        r = SetItemsLR1()
        temporal = SetItemsLR1()

        if c.tamano() == 0:
            return r
        r.unir(c)

        # Itero mi conjunto de items
        for i in c.conjunto:
            nodo_aux = ClaseNodo(i.simbolo, True)

            # Saco mi lado derecho de la regla de mi item
            lista = self.desc_rec_gg.arr_reglas[i.numero_regla].lista_lado_derecho

            l_i = self.desc_rec_gg.arr_reglas[i.numero_regla].info_simbolo
            # print(f"Analizando ({i.numero_regla}, {i.pos_punto}, {i.simbolo})")
            # print(f">>>>>>>>Analizando:", end=' ')
            # print(f"> [{self.desc_rec_gg.arr_reglas[i.numero_regla].info_simbolo.simbolo} ->", end=' ')
            # for index, l in enumerate(lista):
            #     if index == i.pos_punto:
            #         print("·", end=' ')
            #     print(f"{l.simbolo}", end=' ')
            # print(f", {i.simbolo}]")

            lista_sig_elemento = list()

            if i.pos_punto == len(lista):
                continue

            simbolo_en_punto = self.desc_rec_gg.arr_reglas[i.numero_regla].lista_lado_derecho[i.pos_punto]
            if simbolo_en_punto.terminal:
                continue

            for m in range(i.pos_punto + 1, len(lista)):
                lista_sig_elemento.append(copy.deepcopy(lista[m]))
            lista_sig_elemento.append(copy.deepcopy(nodo_aux))

            conj_first = self.desc_rec_gg.first(lista_sig_elemento)
            # print(f"\tDe la regla #{i.numero_regla} en punto {i.pos_punto} tengo {conj_first}")

            # Verifico si mi punto no esta ya al final
            if i.pos_punto < len(lista):
                n = lista[i.pos_punto]
                if not n.terminal:

                    # Como no fue terminal el nodo de lista lado derecho itero en toda mi lista para
                    # encontrar otras reglas con el no terminal encontrado
                    for k in range(0, self.desc_rec_gg.numero_reglas):

                        # Verifico si ya encontre una coincidencia
                        if self.desc_rec_gg.arr_reglas[k].info_simbolo.simbolo == n.simbolo:
                            for simb_first in conj_first:
                                aux = ItemLR1(k, 0, simb_first)
                                if not c.contiene(aux):
                                    # print(f"\t--->Termporary adding...", end=' ')

                                    # print(f"> [{self.desc_rec_gg.arr_reglas[k].info_simbolo.simbolo} ->",
                                    #       end=' ')
                                    # for index, l in enumerate(self.desc_rec_gg.arr_reglas[k].lista_lado_derecho):
                                    #     if index == i.pos_punto:
                                    #         print("·", end=' ')
                                    #     print(f"{l.simbolo}", end=' ')
                                    # print(f", {simb_first}]")

                                    temporal.agregar(copy.deepcopy(aux))
            # print("<<<<<<<<Finalizando...", end=' ')
            # print(f"> [{self.desc_rec_gg.arr_reglas[i.numero_regla].info_simbolo.simbolo} ->", end=' ')
            # for index, l in enumerate(lista):
            #     if index == i.pos_punto:
            #         print("·", end=' ')
            #     print(f"{l.simbolo}", end=' ')
            # print(f", {i.simbolo}]")

        # print("Unir", c.)
        r.unir(self.cerradura_lr1(temporal))
        # print(f"Termine con {r.tamano()} elementos")
        return r

    # noinspection PyMethodMayBeStatic
    def c_contiene(self, c: SetItemsLR1, aux: ItemLR1):  # c: es un set de Item_LR0, aux es un Item_LR0
        for i in c.conjunto:
            if i.numero_regla == aux.numero_regla and i.pos_punto == aux.pos_punto and i.simbolo == aux.simbolo:
                return True
        return False

    def ir_a_lr1(self, c: SetItemsLR1, simbolo: str):
        return self.cerradura_lr1(self.mover_lr1(c, simbolo))
