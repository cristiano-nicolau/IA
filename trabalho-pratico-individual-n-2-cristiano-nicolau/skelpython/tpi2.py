#encoding: utf8

# YOUR NAME: Cristiano Nicolau
# YOUR NUMBER: 108536

# COLLEAGUES WITH WHOM YOU DISCUSSED THIS ASSIGNMENT (names, numbers):
# - Vasco Faria, 107323
# - Gonçalo Lopes, 107572

from semantic_network import *
from constraintsearch import *

class MySN(SemanticNetwork):

    def __init__(self):
        SemanticNetwork.__init__(self)
        # ADD CODE HERE IF NEEDED
        pass

    def query_local(self,user=None,e1=None,rel=None,e2=None):
        
        self.query_result = []

        for current_user, data in self.declarations.items():
            if user is not None and user != current_user:
                continue
                
            for (entity1, relation), entity2 in data.items():
                if (
                    (e1 is None or entity1 == e1)
                    and (rel is None or relation == rel) 
                    and (e2 is None or entity2 == e2)
                ):
                    self.query_result.append(Declaration(current_user, Relation(entity1, relation, entity2)))

        return self.query_result # Your code must leave the output in
                          # self.query_result, which is returned here

    def query(self, entity, assoc=None):

        self.query_result = []
        pds_assoc = []
        pds = self.query_local(e1=entity, rel = 'member') + self.query_local(e1=entity, rel = 'subtype') 

        for ent2 in [pd.relation.entity2 for pd in pds]:
            pds_assoc.extend(self.query(ent2, assoc))

        local_assoc = self.query_local(e1=entity, rel=assoc)

        self.query_result =  local_assoc + pds_assoc

        for i in self.query_result:
            if i.relation.name == 'subtype' or i.relation.name == 'member':
                self.query_result.remove(i)

        return self.query_result


    def update_assoc_stats(self, assoc, user=None):
        self.assoc_stats = {}

        # Get the declarations based on the user, if provided
        if user is not None:
            declarations = self.query_local(user=user, rel=assoc)
        else:
            declarations = self.query_local(rel=assoc)

        # Convert the association to a tuple before using it as a key
        assoc_key = (assoc, user)

        if assoc_key not in self.assoc_stats:
            self.assoc_stats[assoc_key] = ({}, {})

        for declaration in declarations:
            # Get the entity that is the subject of the association
            entity = declaration.relation.entity1

            # Get the entity that is the object of the association
            assoc_entity = declaration.relation.entity2

            decl = self.query_local(e1=entity, rel='member') + self.query_local(e1=entity, rel='subtype')
            decl_ass = self.query_local(e1=assoc_entity, rel='member') + self.query_local(e1=assoc_entity, rel='subtype')

            decl_user = self.query_local(e1=entity, rel=assoc, user=user) + self.query_local(e1=entity, rel=assoc, user=user)
            decl_user_ass = self.query_local(e1=assoc_entity, rel=assoc, user=user) + self.query_local(e1=assoc_entity, rel=assoc, user=user)

            if decl:
                if decl[0].relation.entity2 not in self.assoc_stats[assoc_key][0]:
                    self.assoc_stats[assoc_key][0][decl[0].relation.entity2] = 1
                else:
                    self.assoc_stats[assoc_key][0][decl[0].relation.entity2] += 1
         

        return self.assoc_stats
                    
                


class MyCS(ConstraintSearch):

    def __init__(self,domains,constraints):
        ConstraintSearch.__init__(self,domains,constraints)
        # ADD CODE HERE IF NEEDED
        pass


    def search_all(self, domains=None):
        if domains is None:
            domains = self.domains

        self.result = []
        self.search_recursive(domains.copy())
        return self.result

    def search_recursive(self, domains):
        self.calls += 1

        if any([lv == [] for lv in domains.values()]):
            return

        if all([len(lv) == 1 for lv in domains.values()]):
            for (var1, var2) in self.constraints:
                constraint = self.constraints[var1, var2]
                if not constraint(var1, domains[var1][0], var2, domains[var2][0]):
                    return
            self.result.append({v: lv[0] for (v, lv) in domains.items()})
            return

        var_to_expand = self.select_variable(domains)

        if len(domains[var_to_expand]) > 1:
            for val in domains[var_to_expand]:
                new_domains = dict(domains)
                new_domains[var_to_expand] = [val]
                new_domains = self.propagate(new_domains, var_to_expand, val)
                if new_domains is None:
                    continue
                self.search_recursive(new_domains)

    def propagate(self, domains, var, value):
        for v, domain in domains.items():
            if v == var:
                continue
            if (v, var) in self.constraints:
                constraint = self.constraints[v, var]
                new_domain = [val for val in domain if constraint(v, val, var, value)]
                if new_domain == []:
                    return None
                domains[v] = new_domain

        return domains

    def select_variable(self, domains):
        for var, values in domains.items():
            if len(values) > 1:
                return var
        return None

        