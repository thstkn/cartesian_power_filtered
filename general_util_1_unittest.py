# unittest general util 1

import unittest
import general_util_1 as gu1


class TestNdimPermutFiltered(unittest.TestCase):

    def test_flatten_list(self):
        to_flatten = [[[0, 1, 2], [3, 4, 5], [6, 7, 8]], [[],[1,2,3],[4,5,6]],
                      [[1],[1]], [[],[],[]]]
        count = 0

        for list in to_flatten:
            for sublist in list:
                # add up items count of all sublists
                count += len(sublist)

            flattened = gu1.flatten_list(list)
            # check if length of flattened list equals sum of count
            self.assertEqual(len(flattened), count)
            # reinitialize counter after each list
            count = 0

    
    def test_ndim_permute(self):
        to_permute = [0, 1, 2, 3, 4]
        dimensions_list = [2, 3, 4, 5]
        # max_duplicates = 0 means not to filter at all
        max_duplicates_list = [0, 1, 2, 3, 4, 5]
        flattened = False
        verbose = 0

        # for all combinations of dimensions_list and max_duplicates_list
        for dimensions in dimensions_list:
            for max_duplicates in max_duplicates_list:

                if max_duplicates <= dimensions:
                    
                    result_ndim_permute = gu1.ndimensional_permute(to_permute, dimensions, max_duplicates, flattened, verbose)
                    unfiltered_result_length = len(gu1.flatten_list(result_ndim_permute))
                    # length of permuted equals n(permuted elements) to the power of n(dimensions) if not filtered
                    if max_duplicates == 0: 
                        self.assertEqual(unfiltered_result_length, len(to_permute) ** dimensions)
                    
                    else:
                        for sublist in result_ndim_permute:
                            # check if possible empty sublists werent removed
                            self.assertNotEqual(sublist, [])

                            for perm in sublist:
                                for item in perm:
                                    # check if each items count in each permutation is less than or equal to max_duplicates
                                    self.assertTrue(perm.count(item) <= max_duplicates)


    def test_ndim_filter(self):
        # paramers for generating testable permutation_lists
        to_permute = [0, 1, 2, 3, 4]
        dimensions_list = [2, 3, 4, 5]
        # max_duplicates = 0 means not to filter at all in ndim_permute
        max_duplicates_list = [0, 1, 2, 3, 4]
        flattened1 = False
        verbose1 = 0
        
        # parameters for testing filtering
        dimensional_filterlist_list = [ [ [[], []], [[0],[]], [[0],[3,4,5]] ],
                                        [ [[0,1],[2],[]], [[0,1],[2],[3,4,5]], [[],[],[]] ],
                                        [ [[0],[],[1,2],[3,4,5]], [[0],[1],[1,2],[3,4,5]] ],
                                        [ [[0],[],[],[1,2],[3,4,5]], [[0],[4],[5],[1,2],[3,4,5]] ] ]
        returnwhich_list = ['filtered', 'unfiltered']
        filtermode_list = ['loose', 'strict']
        flattened2 = False
        verbose2 = 0

        # for all combinations of dimensions_list and max_duplicates_list
        for dimensions in dimensions_list:
            for max_duplicates in max_duplicates_list:

                if max_duplicates <= dimensions:
                    
                    to_filter = gu1.ndimensional_permute(to_permute, dimensions, max_duplicates, flattened1, verbose1)
                    to_filter_length = len(gu1.flatten_list(to_filter))

                    # only use filterlists with correct dimensionalities
                    for dimensional_filterlist in dimensional_filterlist_list[dimensions -2]:
                        print(f'{len(dimensional_filterlist)}-dim filter = {dimensional_filterlist}')

                        for returnwhich in returnwhich_list:
                            for filtermode in filtermode_list:

                                
                                
                                result_ndim_filter = gu1.ndimensional_filter(to_filter, dimensional_filterlist, returnwhich, filtermode, flattened2, verbose2)
                                result_ndim_filter_length = len(gu1.flatten_list(result_ndim_filter))
                                
                                for sublist_result_filter in result_ndim_filter:
                                    # check if possible empty sublists werent removed
                                    self.assertNotEqual(sublist_result_filter, [])


                                    if returnwhich == 'filtered' and filtermode == 'strict':
                                        # content of filtered cant be in unfiltered
                                        opposite = (gu1.ndimensional_filter(to_filter, dimensional_filterlist, 'unfiltered', filtermode, flattened2, verbose2))

                                        for perm in sublist_result_filter:
                                            for opposite_sublist in opposite:
                                                self.assertNotIn(perm, opposite_sublist)

                                            for i, item in enumerate(perm):
                                                # check for item within filter at dimension i if filter isnt empty
                                                if dimensional_filterlist[i] != []:
                                                    self.assertIn(item, dimensional_filterlist[i])
                                                
                                                for item in to_permute:
                                                    if item not in dimensional_filterlist[i]:
                                                        # check for item not within filter at dimension i
                                                        self.assertNotIn(item, dimensional_filterlist[i])
                                        # filtered and unfiltered lists lengths should always sum up to the length of the original list
                                        length_sum = result_ndim_filter_length + len(gu1.flatten_list(opposite))
                                        self.assertEqual(length_sum, to_filter_length)

                                    elif returnwhich == 'filtered' and filtermode == 'loose':
                                        # content of filtered cant be in unfiltered
                                        opposite = (gu1.ndimensional_filter(to_filter, dimensional_filterlist, 'unfiltered', filtermode, flattened2, verbose2))

                                        for perm in sublist_result_filter:
                                            for opposite_sublist in opposite:

                                                
                                                self.assertNotIn(perm, opposite_sublist)
                                        
                                            one_item_in_any_demension_in_filter = False
                                            for i, item in enumerate(perm):
                                                # if dimensional item in any dimension is found in filter evaluate True
                                                if item in dimensional_filterlist[i] or dimensional_filterlist[i] == []:
                                                    one_item_in_any_demension_in_filter = True
                                                    break
                                            self.assertTrue(one_item_in_any_demension_in_filter)
                                        # filtered and unfiltered lists lengths should always sum up to the length of the original list
                                        length_sum = result_ndim_filter_length + len(gu1.flatten_list(opposite))
                                        self.assertEqual(length_sum, to_filter_length)
                                              

                                    elif returnwhich == 'unfiltered' and filtermode == 'strict':
                                        # content of unfiltered cant be in filtered
                                        opposite = (gu1.ndimensional_filter(to_filter, dimensional_filterlist, 'filtered', filtermode, flattened2, verbose2))
                                        for perm in sublist_result_filter:
                                            for opposite_sublist in opposite:
                                                self.assertNotIn(perm, opposite_sublist)
                                        # filtered and unfiltered lists lengths should always sum up to the length of the original list
                                        length_sum = result_ndim_filter_length + len(gu1.flatten_list(opposite))
                                        self.assertEqual(length_sum, to_filter_length)

                                    elif returnwhich == 'unfiltered' and filtermode == 'loose':
                                        # content of unfiltered cant be in filtered
                                        opposite = (gu1.ndimensional_filter(to_filter, dimensional_filterlist, 'filtered', filtermode, flattened2, verbose2))
                                        for perm in sublist_result_filter:
                                            for opposite_sublist in opposite:
                                                self.assertNotIn(perm, opposite_sublist)
                                        # filtered and unfiltered lists lengths should always sum up to the length of the original list
                                        length_sum = result_ndim_filter_length + len(gu1.flatten_list(opposite))
                                        self.assertEqual(length_sum, to_filter_length)




if __name__ == '__main__':
    unittest.main(argv=['ignored', '-v'], exit=False)


