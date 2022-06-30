# unittest general util 1

import unittest
import cartesian_product_filtered_generator as cpf
from itertools import product
from typing import Any

class TestNdimProductFiltered(unittest.TestCase):

    def test_ndim_filter(self):
        verbose = True
        if verbose: print()
        # parameters for generating testable combination_lists
        alphabet = [0, 1, 2, 3, 4, ('a', None), 'b', 'c']
        # max_duplicates = 0 means not to filter at all in ndim_permute
        max_duplicates_list = [0, 1, 2, 3]
        # parameters for testing filtering
        dfll =  [ [ [[], []], [[0],[]], [[0],[3,4,5]] ],
                  [ [[0,1],[2],[]], [[0,1],[('a', None),2],[4,5]], [[],[],[]] ],
                  [ [[0],[],[1,2],[3,4,5]], [[0],[1],[1,2],[3,4,5]] ],
                  [ [[0],[],[('a', None)],[1,2],[3,4,5]],
                    [[],[4],[5],[1,2],[]] ] ]                        # 5 DIM
                  #[ [[],[],[('a', None)],[1,2],[],[]], \
                    #[[],[0,1,2,4],['b','a','c'],[5],[1,2],[]] ],    # 6 DIM
                  #[ [[],[],[('a', None)],[1,2],[1,2,3,4],[],[]], \
                    #[[],[0,1,2,4],['b','a','c'],[5],[],[],[]] ] ]   # 7 DIM
        dimensional_filterlist_list: list[list[list[list[Any]]]] = dfll
        returnwhich_list = ['filtered', 'unfiltered']
        #for returnwhich in returnwhich_list:
        filtermode_list = ['loose', 'strict']

        # for all combinations of dimensions_list and max_duplicates_list
        for max_duplicates in max_duplicates_list:
            # only use filterlists with correct dimensionalities
            for i, dim_filter in enumerate(dimensional_filterlist_list):
                if verbose:
                    print(f'{len(dim_filter)}-dim filter = '      
                            f'{dim_filter}')
                dimensions = i+2
                cart_power = list(product(alphabet, repeat=dimensions))
                self.assertEqual(len(cart_power),
                                    len(alphabet)**(dimensions))
                for filter in dim_filter:
                    mode = 'loose'
                    self.assertTrue(cpf.ndimensional_filter(cart_power,
                                                            dim_filter,
                                                            max_duplicates,
                                                            mode))
                    

                        

                        if returnwhich == 'filtered' and \
                            mode == 'strict':
                            # content of filtered cant be in unfiltered
                            opposite = (cpf.ndimensional_filter(cart_power,
                            dim_filter, 'unfiltered', mode,
                            verbose2))

                            for perm in result_ndim_filter:
                                self.assertNotIn(perm, opposite)

                                for i, item in enumerate(perm):
    # check for item within filter at dimension i if filter isnt empty
                                    if dim_filter[i] != []:
                                        self.assertIn(item, dim_filter[i])
                                    
                                    for item in alphabet:
                                        if item not in dim_filter[i]:
            # check for item not within filter at dimension i
                                            self.assertNotIn(item,
                                            dim_filter[i])
# filtered and unfiltered lists lengths should always sum up to the length of
# the original list
                            length_sum = result_ndim_filter_length + \
                                                len(opposite)
                            self.assertEqual(length_sum, to_filter_length)

                        elif returnwhich == 'filtered' and \
                                mode == 'loose':
                            # content of filtered cant be in unfiltered
                            opposite = (cpf.ndimensional_filter(cart_power,
                            dim_filter, 'unfiltered', mode,
                            verbose2))

                            for perm in result_ndim_filter:
                                self.assertNotIn(perm, opposite)
                            
                                oneiteminanydemensioninfilter = False
                                for i, item in enumerate(perm):
# if dimensional item in any dimension is found in filter evaluate True
                                    if item in dim_filter[i] or \
                                            dim_filter[i] == []:
                                        oneiteminanydemensioninfilter = True
                                        break
                                self.assertTrue(
                                        oneiteminanydemensioninfilter)
# filtered and unfiltered lists lengths should always sum up to the length of
# the original list
                            length_sum = result_ndim_filter_length + \
                                                len(opposite)
                            self.assertEqual(length_sum, to_filter_length)
                                  

                        elif returnwhich == 'unfiltered' and \
                                mode == 'strict':
                            # content of unfiltered cant be in filtered
                            opposite = cpf.ndimensional_filter(cart_power,
                            dim_filter, 'filtered', mode, verbose2)
                            for perm in result_ndim_filter:
                                self.assertNotIn(perm, opposite)
# filtered and unfiltered lists lengths should always sum up to the length of
# the original list
                            length_sum = result_ndim_filter_length + \
                                                len(opposite)
                            self.assertEqual(length_sum, to_filter_length)

                        elif returnwhich == 'unfiltered' and \
                                mode == 'loose':
                            # content of unfiltered cant be in filtered
                            opposite = cpf.ndimensional_filter(cart_power,
                            dim_filter, 'filtered', mode, verbose2)
                            for perm in result_ndim_filter:
                                self.assertNotIn(perm, opposite)
# filtered and unfiltered lists lengths should always sum up to the length of
# the original list
                            length_sum = result_ndim_filter_length + \
                                                len(opposite)
                            self.assertEqual(length_sum, to_filter_length)


if __name__ == '__main__':
    unittest.main(argv=['ignored', '-v'], exit=False)
    import sys
    print(f'Tested:\n {sys.modules["__main__"]}\t'
            f'{sys.modules["__main__"].__file__}')
    print(f'{sys.modules["app"]}\t'
            f'{sys.modules["app"].__file__}')


