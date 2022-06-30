# unittest general util 1

import unittest
import cartesian_product_filtered2 as cpf

class TestNdimProductFiltered(unittest.TestCase):

    def test_flatten_list(self):
        to_flatten = [[[0, 1, 2], [3, 4, 5], [6, 7, 8]], [[],[1,2,3],[4,5,6]],
                      [[1],[1]], [[],[],[]]]

        for list in to_flatten:
            # reinitialize counter before each list
            count = 0
            for sublist in list:
                # add up items count of all sublists
                count += len(sublist)

            flattened = cpf.flatten_list(list)
            # check if length of flattened list equals sum of count
            self.assertEqual(len(flattened), count)

    
    def test_ndim_product(self):
        print()
        to_permute = [0, 1, 2, 3, 4]
        to_permute = [0, 1, 2, ('a', None), 4, 'b', 'c']
        dimensions_list = [2, 3, 4, 5]
        # max_duplicates = 0 means not to filter at all
        max_duplicates_list = [0, 1, 2, 3, 4, 5]
        verbose = 1

        # for all combinations of dimensions_list and max_duplicates_list
        for dims in dimensions_list:
            for max_duplicates in max_duplicates_list:

                if max_duplicates <= dims:
                    ndim_prod_filtered = cpf.ndimensional_product(to_permute,
                        dims, max_duplicates, 'filtered', verbose)
                    filtered_result_length = len(ndim_prod_filtered)

                    ndim_prod_unfiltered = cpf.ndimensional_product(to_permute,
                        dims, max_duplicates, 'unfiltered', verbose)
                    unfiltered_result_length = len(ndim_prod_unfiltered)

                    combinations = len(to_permute) ** dims
                    lensum = filtered_result_length + unfiltered_result_length
                    self.assertEqual(combinations, lensum)
# length of combined equals n(combined elements) to the power of n(dimensions)
# if not filtered
                    if max_duplicates == 0: 
                        self.assertEqual(filtered_result_length, \
                                        (len(to_permute) ** dims))
# check if each items count in each combination is less than or equal to
# max_duplicates
                    else:
                        for perm in ndim_prod_filtered:
                            for item in perm:
                                self.assertTrue(perm.count(item) <= \
                                                    max_duplicates)


    def test_ndim_filter(self):
        verbose = True
        if verbose: print()
        # paramers for generating testable combination_lists
        to_permute = [0, 1, 2, 3, 4, ('a', None), 'b', 'c']
        dimensions_list = [2, 3, 4, 5]
        # max_duplicates = 0 means not to filter at all in ndim_permute
        max_duplicates_list = [0, 1, 2, 3, 4, 5]
        verbose1 = 1
        
        # parameters for testing filtering
        dfll =  [ [ [[], []], [[0],[]], [[0],[3,4,5]] ],
                  [ [[0,1],[2],[]], [[0,1],[('a', None),2],[4,5]], [[],[],[]] ],
                  [ [[0],[],[1,2],[3,4,5]], [[0],[1],[1,2],[3,4,5]] ],
                  [ [[0],[],[('a', None)],[1,2],[3,4,5]], \
                    [[],[4],[5],[1,2],[]] ] ]                        # 5 DIM
                  #[ [[],[],[('a', None)],[1,2],[],[]], \
                    #[[],[0,1,2,4],['b','a','c'],[5],[1,2],[]] ],    # 6 DIM
                  #[ [[],[],[('a', None)],[1,2],[1,2,3,4],[],[]], \
                    #[[],[0,1,2,4],['b','a','c'],[5],[],[],[]] ] ]   # 7 DIM
        dimensional_filterlist_list = dfll
        returnwhich_list = ['filtered', 'unfiltered']
        filtermode_list = ['loose', 'strict']
        verbose2 = 0

        # for all combinations of dimensions_list and max_duplicates_list
        for dims in dimensions_list:
            for max_duplicates in max_duplicates_list:
                for returnwhich in returnwhich_list:
                    for filtermode in filtermode_list:

                        tofilter = cpf.ndimensional_product(to_permute, dims,
                            max_duplicates, returnwhich, verbose1)
                        to_filter_length = len(tofilter)

                        # only use filterlists with correct dimensionalities
                        for dim_filter in dimensional_filterlist_list[dims -2]:
                            if verbose:
                                print(f'{len(dim_filter)}-dim filter = '      
                                        f'{dim_filter}')
                            
                            result_ndim_filter = cpf.ndimensional_filter(
                                tofilter, dim_filter, returnwhich, filtermode,
                                verbose2)
                            result_ndim_filter_length = len(result_ndim_filter)

                            if returnwhich == 'filtered' and \
                                filtermode == 'strict':
                                # content of filtered cant be in unfiltered
                                opposite = (cpf.ndimensional_filter(tofilter,
                                dim_filter, 'unfiltered', filtermode,
                                verbose2))

                                for perm in result_ndim_filter:
                                    self.assertNotIn(perm, opposite)

                                    for i, item in enumerate(perm):
        # check for item within filter at dimension i if filter isnt empty
                                        if dim_filter[i] != []:
                                            self.assertIn(item, dim_filter[i])
                                        
                                        for item in to_permute:
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
                                    filtermode == 'loose':
                                # content of filtered cant be in unfiltered
                                opposite = (cpf.ndimensional_filter(tofilter,
                                dim_filter, 'unfiltered', filtermode,
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
                                    filtermode == 'strict':
                                # content of unfiltered cant be in filtered
                                opposite = cpf.ndimensional_filter(tofilter,
                                dim_filter, 'filtered', filtermode, verbose2)
                                for perm in result_ndim_filter:
                                    self.assertNotIn(perm, opposite)
# filtered and unfiltered lists lengths should always sum up to the length of
# the original list
                                length_sum = result_ndim_filter_length + \
                                                    len(opposite)
                                self.assertEqual(length_sum, to_filter_length)

                            elif returnwhich == 'unfiltered' and \
                                    filtermode == 'loose':
                                # content of unfiltered cant be in filtered
                                opposite = cpf.ndimensional_filter(tofilter,
                                dim_filter, 'filtered', filtermode, verbose2)
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


