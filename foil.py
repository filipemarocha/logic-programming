from problog.program import SimpleProgram, PrologString
from problog.logic import *
from problog.engine import DefaultEngine
from math import log
import numpy as np

# Positive examples are descriptions of states in a RL task that correspond to the goal
pos_examples = [[2,1,2,1,2,1,0],[3,4,3,4,3,4,0]]
# Negative examples are descriptions of states other than goal states
neg_examples = [[1,1,2,2,3,3,0],[1,0,1,0,4,4,1],[2,3,1,1,2,3,2],[2,1,1,1,1,1,0],
    [2,3,1,1,2,3,0],[1,0,2,2,3,3,0],[1,4,1,3,1,4,0],[1,4,2,4,2,4,0],[1,1,1,4,1,4,0],
    [2,1,1,1,2,3,0],[2,2,2,2,2,2,1],[0,2,0,2,2,2,0],[0,1,0,1,0,0,0],[1,0,0,1,1,1,0]]

class FOIL:
    # extra terms is list of dicts: key is term name, value is the full declaration in prolog, arity is the number of variables of the term
    def __init__(self, pos_examples, neg_examples, extra_terms=[], target_name = 'target'):
        # Define the language of terms
        self.target = Term(target_name)
        self.equal = Term('equal')
        self.pos_examples = pos_examples
        self.neg_examples = neg_examples
        self.examples = pos_examples + neg_examples
        self.extra_terms = extra_terms
        #TODO: check extra terms arity, if greater than target arity, create more variables
        n_target_variables = len(self.examples[0])
        target_variables_names = ['X'+str(i) for i in range(1,n_target_variables+1)]
        self.X = list(map(Var,target_variables_names))
        constants = set()
        for example in self.examples:
            constants.update(example)
        self.c = list(map(Term, [str(constant) for constant in constants]))
        # Initialize the logic program
        self.pl = SimpleProgram()
        self.pl += self.equal(self.X[0],self.X[0])
        self.pl += self.target(*tuple(self.X))
        for extra_term in self.extra_terms:
            self.pl += PrologString(extra_term)
        self.predicates = [self.equal]# + list(extra_terms.keys())
        self.engine = DefaultEngine()
        self.db = self.engine.prepare(self.pl)
        self.original_rule = list(self.pl)[1]
        self.new_body_literals = []
        print(list(self.pl))

    def generate_candidates(self):
        candidate_literals = []
        for predicate in self.predicates:
            # TODO: adapt to serve other predicates besides equal
            # First test each variable equal to constant
            for i_x in range(len(self.X)):
                for i_c in range(len(self.c)):
                    candidate_literals.append(self.equal(self.X[i_x],self.c[i_c]))
            # Second test each variable equal to another variable
            for i_x in range(len(self.X)):
                for i_xx in range(i_x+1,len(self.X)):
                    candidate_literals.append(self.equal(self.X[i_x],self.X[i_xx]))
        return candidate_literals

    def state(self, state):
        return tuple([self.c[s_c] for s_c in state])

    def pos_neg_examples_bindings(self, rule, db):
        pos_bindings = []
        neg_bindings = []
        for i_pos in range(len(self.pos_examples)):
            query_term = rule(*self.state(self.pos_examples[i_pos]))
            res = self.engine.query(db, query_term)
            binding = bool(res)
            if binding:
                pos_bindings.append(i_pos)
        for i_neg in range(len(self.neg_examples)):
            query_term = rule(*self.state(self.neg_examples[i_neg]))
            res = self.engine.query(db, query_term)
            binding = bool(res)
            if binding:
                neg_bindings.append(i_neg)
        return pos_bindings, neg_bindings

    def add_literal_to_goal(self, literal):
        if len(self.new_body_literals) == 0:
            new_goal = self.original_rule << literal
        else:
            new_body = literal
            for l in self.new_body_literals:
                new_body = new_body & l
            new_goal = self.original_rule << new_body
        new_pl = SimpleProgram()

        new_pl += list(self.pl)[0]
        new_pl += new_goal
        new_db = self.engine.prepare(new_pl)
        return new_db, new_pl

    def foil_gain(self, literal, rule):
        # n pos and neg bindings for Rule
        p_r, n_r = self.pos_neg_examples_bindings(rule, self.db)
        new_db, _ = self.add_literal_to_goal(literal)
        # n pos and neg bindings for Rule + Literal
        p_r_l, n_r_l = self.pos_neg_examples_bindings(rule, new_db)
        t = len(set(p_r).intersection(set(p_r_l)))
        foil_gain = t * ( log(len(p_r_l)+1/(len(p_r_l) + len(n_r_l)+1),2) - log(len(p_r)+1/(len(p_r) + len(n_r)+1),2) )
        return foil_gain

    def run(self):
        new_rule_pos = self.pos_examples
        while len(new_rule_pos)>0:
            rule = self.target
            new_rule_neg = self.neg_examples
            while len(new_rule_neg)>0:
                candidate_literals = self.generate_candidates()
                foil_gains = []
                for literal in candidate_literals:
                    foil_gains.append(self.foil_gain(literal,rule))
                max_ig = max(foil_gains)
                max_ig_index = foil_gains.index(max_ig)
                new_literal = candidate_literals[max_ig_index]
                self.db, self.pl = self.add_literal_to_goal(new_literal)
                self.new_body_literals.append(new_literal)
                new_rule_pos_bind, new_rule_neg_bind = self.pos_neg_examples_bindings(rule, self.db)
                new_rule_neg = [self.neg_examples[neg_index] for neg_index in new_rule_neg_bind]
            new_rule_pos_covered = [self.pos_examples[pos_index] for pos_index in new_rule_pos_bind]
            new_rule_pos = [pos for pos in new_rule_pos if pos not in new_rule_pos_covered]
        return list(self.pl)[1]

foil = FOIL(pos_examples,neg_examples, target_name='goal')
learned_target = foil.run()
print(learned_target)
