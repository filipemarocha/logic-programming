import numpy as np

class FuzzyDecider:

    def __init__(self):
        self.universes = {}
        self.fuzzy_sets = {}
        self.binary_relations = {}
        self.rules = []

    def add_universe(self, universe_name, universe_points):
        self.universes[universe_name] = np.array([universe_points])
        print (self.universes[universe_name])

    def add_fuzzy_set(self, set_name, universe_name, set_values):
        if len(set_values) == len(self.universes[universe_name][0]):
            self.fuzzy_sets[set_name] = {}
            self.fuzzy_sets[set_name]['universe'] = universe_name
            self.fuzzy_sets[set_name]['values'] = np.array([set_values])
            print (self.fuzzy_sets[set_name])
        else:
            raise Exception('Number of values in the fuzzy set must match number of universe points.')

    def add_binary_relation(self, set_name, set_values):
        self.binary_relations[set_name] = set_values
        print (self.binary_relations[set_name])
        print (self.binary_relations[set_name].shape)

    def product(self, fuzzy_set_name_1, fuzzy_set_name_2):
        fuzzy_set_1 = self.fuzzy_sets[fuzzy_set_name_1]['values']
        fuzzy_set_2 = self.fuzzy_sets[fuzzy_set_name_2]['values']
        fuzzy_set_2 = np.repeat(fuzzy_set_2, fuzzy_set_1.shape[1], axis = 0)
        fuzzy_set_1 = np.repeat(np.transpose(fuzzy_set_1), fuzzy_set_2.shape[1], axis = 1)
        return np.minimum(fuzzy_set_2, fuzzy_set_1)

    def union(self, fuzzy_set_name_1, fuzzy_set_name_2):
        fuzzy_set_1 = self.fuzzy_sets[fuzzy_set_name_1]['values']
        fuzzy_set_2 = self.fuzzy_sets[fuzzy_set_name_2]['values']
        return np.maximum(fuzzy_set_1, fuzzy_set_2)

    def intersect(self, fuzzy_set_name_1, fuzzy_set_name_2):
        fuzzy_set_1 = self.fuzzy_sets[fuzzy_set_name_1]['values']
        fuzzy_set_2 = self.fuzzy_sets[fuzzy_set_name_2]['values']
        return np.minimum(fuzzy_set_1, fuzzy_set_2)

    def composition(self, binary_relation_name_1, binary_relation_name_2):
        binary_relation_1 = self.binary_relations[binary_relation_name_1]
        binary_relation_2 = self.binary_relations[binary_relation_name_2]
        binary_relation_1 = np.transpose(binary_relation_1)
        binary_relation_1 = np.broadcast_to(binary_relation_1, (binary_relation_2.shape[1], ) + binary_relation_1.shape)
        binary_relation_1 = np.transpose(binary_relation_1)
        binary_relation_2 = np.broadcast_to(binary_relation_2, (binary_relation_1.shape[0], ) + binary_relation_2.shape)
        return np.amax(np.minimum(binary_relation_1, binary_relation_2), axis = 1)

    def negation(self, fuzzy_set_name):
        fuzzy_set = self.fuzzy_sets[fuzzy_set_name]['values']
        return 1 - fuzzy_set

    def add_rule(self, antecedent, consequent):
        pass

    def inference(self, antecedent):
        pass


if __name__ == "__main__":

    fuzzy_decider = FuzzyDecider()
    fuzzy_decider.add_universe('Truthiness', [0, 1, 2, 3])
    #fuzzy_decider.add_universe('Falsinness', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    fuzzy_decider.add_fuzzy_set('A is False', 'Truthiness', [0, 0, 1, 1])
    fuzzy_decider.add_fuzzy_set('A is True', 'Truthiness', [1, 1, 0, 0])
    fuzzy_decider.add_binary_relation('A is False and A is True', fuzzy_decider.product('A is False', 'A is True'))


    fuzzy_decider = FuzzyDecider()
    fuzzy_decider.add_universe('Truthiness', [0, 1, 2, 3])
    fuzzy_decider.add_universe('Falsiness', [0, 1, 2, 3])
    fuzzy_decider.add_fuzzy_set('Classical_True', 'Truthiness', [0, 0, 1, 1])
    fuzzy_decider.add_fuzzy_set('Classical_False', 'Truthiness', [1, 1, 0, 0])
    fuzzy_decider.add_binary_relation('Classical_True x Classical_False', fuzzy_decider.product('Classical_True', 'Classical_False'))
    print (fuzzy_decider.intersect('Classical_True', 'Classical_False'))
    print (fuzzy_decider.negation('Classical_True'))
    print (fuzzy_decider.union('Classical_True', 'Classical_False'))


    fuzzy_decider.add_universe('U', [1, 2, 3, 4, 5])
    fuzzy_decider.add_universe('V', [1, 2, 3])
    fuzzy_decider.add_universe('W', [1, 2, 3, 4])

    fuzzy_decider.add_fuzzy_set('Tall', 'U', [0.9, 0.5, 0.8, 0.4, 0.1])
    fuzzy_decider.add_fuzzy_set('Handsome', 'V', [0.5, 0.8, 0.9])
    fuzzy_decider.add_fuzzy_set('Rich', 'W', [0.3, 0.2, 0.3, 0.8])

    fuzzy_decider.add_binary_relation('Tall x Handsome', fuzzy_decider.product('Tall', 'Handsome'))
    fuzzy_decider.add_binary_relation('Handsome x Rich', fuzzy_decider.product('Handsome', 'Rich'))

    print (np.all(fuzzy_decider.composition('Tall x Handsome', 'Handsome x Rich') == fuzzy_decider.product('Tall', 'Rich')))
