


# Guiao de representacao do conhecimento
# -- Redes semanticas
#
# Inteligencia Artificial & Introducao a Inteligencia Artificial
# DETI / UA
#
# (c) Luis Seabra Lopes, 2012-2020
# v1.9 - 2019/10/20
#


# Classe Relation, com as seguintes classes derivadas:
#     - Association - uma associacao generica entre duas entidades
#     - Subtype     - uma relacao de subtipo entre dois tipos
#     - Member      - uma relacao de pertenca de uma instancia a um tipo
#

from collections import Counter

class Relation:
    def __init__(self, e1, rel, e2):
        self.entity1 = e1
#       self.relation = rel  # obsoleto
        self.name = rel
        self.entity2 = e2

    def __str__(self):
        return self.name + "(" + str(self.entity1) + "," + \
            str(self.entity2) + ")"

    def __repr__(self):
        return str(self)


# Subclasse Association
class Association(Relation):
    def __init__(self, e1, assoc, e2):
        Relation.__init__(self, e1, assoc, e2)

#   Exemplo:
#   a = Association('socrates','professor','filosofia')

# Subclasse Subtype

class AssocOne(Association):
    one = dict()
    def __init__(self, e1, assoc, e2):
        if assoc not in self.one:
            self.one[assoc] = dict()
        assert e2 not in self.one[assoc] or self.one[assoc][e2].entity1 == e1
        Association.__init__(self, e1, assoc, e2)
        self.one[assoc][e2] = self
class AssocNum(Association):
    def __init__(self, e1, assoc, e2):
        assert isinstance(e2, (int, float))
        Association.__init__(self, e1, assoc, e2)
class Subtype(Relation):
    def __init__(self, sub, super):
        Relation.__init__(self, sub, "subtype", super)
#   Exemplo:
#   s = Subtype('homem','mamifero')

# Subclasse Member
class Member(Relation):
    def __init__(self, obj, type):
        Relation.__init__(self, obj, "member", type)
#   Exemplo:
#   m = Member('socrates','homem')

# classe Declaration
# -- associa um utilizador a uma relacao por si inserida
#    na rede semantica
#


class Declaration:
    def __init__(self, user, rel):
        self.user = user
        self.relation = rel

    def __str__(self):
        return "decl("+str(self.user)+","+str(self.relation)+")"

    def __repr__(self):
        return str(self)

#   Exemplos:
#   da = Declaration('descartes',a)
#   ds = Declaration('darwin',s)
#   dm = Declaration('descartes',m)

# classe SemanticNetwork
# -- composta por um conjunto de declaracoes
#    armazenado na forma de uma lista
#


class SemanticNetwork:
    def __init__(self, ldecl=None):
        self.declarations = [] if ldecl == None else ldecl

    def __str__(self):
        return str(self.declarations)

    def insert(self, decl):
        self.declarations.append(decl)

    def query_local(self, user=None, e1=None, rel=None, e2=None, type=None):
        self.query_result = \
            [d for d in self.declarations
                if (user == None or d.user == user)
                and (e1 == None or d.relation.entity1 == e1)
                and (rel == None or d.relation.name == rel)
                and (e2 == None or d.relation.entity2 == e2)
                and (type == None or isinstance(d.relation, type))]
            
        return self.query_result

    def show_query_result(self):
        for d in self.query_result:
            print(str(d))

    def list_associations(self):
        return list(set(i.relation.name for i in self.declarations if isinstance(i.relation, Association)))

    def list_objects(self):
        return list(set(i.relation.entity1 for i in self.declarations if isinstance(i.relation, Member)))

    def list_users(self):
        return list(set(i.user for i in self.declarations))

    def list_types(self):
        lst = []
        for i in self.declarations:
            if isinstance(i.relation, (Subtype, Member)):
                lst.append(i.relation.entity2)
            if isinstance(i.relation, Subtype):
                lst.append(i.relation.entity2)
        return set(lst)

    def list_local_associations(self, entity):
        lst = []
        for i in self.declarations:
            if isinstance(i.relation, Association):
                if entity in [i.relation.entity1, i.relation.entity2]:
                    lst.append(i.relation.name)
        return set(lst)

    def list_relations_by_user(self, user):
        lst = []
        for i in self.declarations:
            if user == i.user:
                lst.append(i.relation.name)
        return set(lst)
    
    def associations_by_user(self, user):
        lst = []
        for i in self.declarations:
            if isinstance(i.relation,Association):
                if user == i.user:
                    lst.append(i.relation.name)
        return len(set(lst))
    
    def list_local_associations_by_entity(self, entity):
        lst = []
        for i in self.declarations:
            if isinstance(i.relation, Association):
                if entity in [i.relation.entity1, i.relation.entity2]:
                    lst.append((i.relation.name, i.user))
        return set(lst)
    
    def predecessor(self, ent1, ent2):
        for i in self.declarations:
            if isinstance(i.relation, (Member, Subtype)) and ent2 == i.relation.entity1:
                if i.relation.entity2 == ent1 or self.predecessor(ent1, i.relation.entity2):
                    return True
        return False
    
    def predecessor_path(self, ent1, ent2):
        for i in self.declarations:
            if isinstance(i.relation, (Member, Subtype)) and ent2 == i.relation.entity1:
                if i.relation.entity2 == ent1:
                    return [ent1, ent2]
                return self.predecessor_path(ent1, i.relation.entity2) + [ent2]
            
    def query(self, entity, assoc=None):
        pds_assoc = []
        pds = self.query_local(e1=entity, type=(Member, Subtype))
        for ent2 in [d.relation.entity2 for d in pds]:
            pds_assoc.extend(self.query(ent2, assoc))
        local_assoc = self.query_local(e1=entity, rel=assoc, type=Association)
        return pds_assoc + local_assoc
    
    def query2(self, entity, rel=None):
        pds_assoc = []
        pds = self.query_local(e1=entity, type=(Member, Subtype))
        for ent2 in [d.relation.entity2 for d in pds]:
            pds_assoc.extend(self.query(ent2, rel))
        local_assoc = self.query_local(e1=entity, rel=rel)
        return pds_assoc + local_assoc
    
    def query_cancel(self, entity, assoc=None):
        pds_assoc = []
        local_assoc = self.query_local(e1=entity, rel=assoc)
        pds = self.query_local(e1=entity, type=(Member, Subtype))
        for ent2 in [d.relation.entity2 for d in pds]:
            pds_assoc.extend([d for d in self.query_cancel(ent2, assoc) if d.relation.name not in [l.relation.name for l in local_assoc]])
        return pds_assoc + local_assoc
        
    def query_down(self, entity, assoc, first=True):
        decendents_assoc = []
        decendents = self.query_local(e2=entity, type=(Member, Subtype))
        for e1  in [d.relation.entity1 for d in decendents]:
            decendents_assoc.extend(self.query_down(e1, assoc, False))
        if first:
            local_assoc = []
        else:        
            local_assoc = self.query_local(e1=entity, rel=assoc)
        return decendents_assoc + local_assoc
    
    def query_induce(self, entity, assoc):
        descedents_assoc = self.query_down(entity, assoc)
        assoc_values = [d.relation.entity2 for d in descedents_assoc]
        for c, _ in Counter(assoc_values).most_common(1):
            return c
        
    def query_local_assoc(self, entity, assoc):
        local = self.query_local(e1=entity, rel=assoc, type=Association)
        for d in local:
            if isinstance(d.relation, AssocNum):
                return sum([d.relation.entity2 for d in local]) / len(local)
            if isinstance(d.relation, AssocOne):
                for c, v in Counter([d.relation.entity2 for d in local]).most_common(1):
                    return c, v / len(local)
                return None
            total_freq = 0
            res = list()
            for c, v in Counter([d.relation.entity2 for d in local]).most_common():
                res.append((c, v / len(local)))
                total_freq += v / len(local)
                if total_freq > 0.75:
                    return res
    
    def query_assoc_value(self, E, A):
        #first point
        local = self.query_local(e1=E, rel=A, type=Association)
        if len(local) and all([local[0].relation.entity2 == d.relation.entity2 for d in local]):
            return local[0].relation.entity2
        #second point
        herdados = []
        pds = self.query_local(e1=E, type=(Member, Subtype))
        for ent2 in [d.relation.entity2 for d in pds]:
            herdados.extend(self.query(ent2, A))
            
        def perc_v(assocs, v):
            if len(assocs):
                return [a.relation.entity2 for a in assocs].count(v)
            return 0
        
        #third point
        maximization = list()
        for v in [a.relation.entity2 for a in local + herdados]:
            maximization.append((v, (perc_v(herdados, v) + perc_v(herdados, v))/2))
        v, _ = max(maximization, key=lambda x: x[1])
        return v