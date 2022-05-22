

### only needed for timing decorator ###
import sys
sys.path.append('..')
from UTIL import general_util_1 as gu1
########################################
    

def flatten_list(list_of_lists: list[list]) -> list:
    return [item for sublist in list_of_lists for item in sublist]


def ndimensional_permute(permlist: list, dimensions: int, max_duplicates: 
    int = 0, flattened: bool = False, verbose: int = 0) -> list:
    '''Function for n-dimensional permuting all entries of permlist.
    permlist: list of entries to permute, takes any datatypes.
    dimensions: number of dimensions to permute itmes from permlist to.
    max_duplicates: if set to a number > 0, permutations which contain more
        than max_duplicates of the same item in a given permutation will be
        filtered out.
    flattened: if True, returns a flattened list of permuted entries.
    verbose: 0 for no printouts, 1 for printouts, 2 for all printouts
    '''
    # -2 because dimensions dictates permutation while loop and initialized
    # permuted_list is already 2D
    loop_condition = dimensions - 2
    dim = 2
    # init permuted list with 2D permutation
    permuted_list = [[[y, x] for x in permlist] for y in permlist]
    # count keeping track of filtered permutations by duplicates
    counter = 0
    filtered_permuted_list = []

    # n-dimensional permuting #
    while loop_condition > 0:
        permuted_list = flatten_list(permuted_list)
        permuted_list = [[[y, *x] for x in permuted_list] for y in permlist]
        loop_condition -= 1
        dim += 1
        if verbose > 0:
            print(f'ndim_permute says:\tdimensions = {dim}\t{max_duplicates = }'
                    f'\t{len(flatten_list(permuted_list)) = }\n')

    if dimensions - 2 < 1 and verbose > 0:
        print(f'ndim_permute says:\tdimensions = {dim}\t{max_duplicates = }\t'
                f'{len(flatten_list(permuted_list)) = }\n')

    orig_len = len(flatten_list(permuted_list))

    # filtering out permutations with more than max_duplicates of the same item
    # in a given permutation
    if max_duplicates > 0:
        for sublist in permuted_list:
            filtered_permuted_sub_list = []

            for i in range(len(sublist)):
                # correction for removed duplicates in index of sublist
                perm = sublist[i - counter]
                # for each item check if permutation contains more than
                # max_duplicates of the same item
                for item in perm:
                    if not perm.count(item) <= max_duplicates:
                        sublist.remove(perm)
                        if verbose > 2:
                            print(f'{perm = }\t\t{item = }')
                        counter += 1
                        break

            # reinitialize counter to zero after each sublist
            counter = 0
            # only after all permutations from sublist have been filtered, add
            # sublist to filtered_permuted_list
            filtered_permuted_sub_list = sublist
            if verbose > 2:
                print(f'{filtered_permuted_sub_list = }')
            elif verbose > 1:
                print(f'{filtered_permuted_sub_list[:10] = }')

            if filtered_permuted_sub_list != []:
                filtered_permuted_list.append(filtered_permuted_sub_list)

        permuted_list = filtered_permuted_list

    leftovers = orig_len - len(flatten_list(permuted_list))
    if verbose > 0:
        print(f'filtered {leftovers} permutations of {orig_len} containing '
                f'more than {max_duplicates} duplicates\n')

    if not flattened:
        return permuted_list                        # not flattened
    else:
        return flatten_list(permuted_list)          # flatten nested lists


def ndimensional_filter(data_list: list,
                        dimensional_filterlist: list[list],
                        returnwhich: str = 'filtered',
                        filtermode: str = 'loose',
                        flattened: bool = False,
                        verbose: int = 0,
                        print_param: int = 3) -> list:
    ''' Filtering n-dimensional data lists by items in dimensional_filterlist
    sublists. Returning filtered n-dimensional data as list
    data_list: list of n-dimensional data tuples.
    dimensional_filterlist: n-dimensional list of lists of items to filter out.
        format is [[dimension 1], [dimension 2], ...]. empty inner lists are
        needed to declare dimensionality correctly in case of not filtering all
        dimensions
    returnwhich: takes 'filtered' or 'unfiltered' as a string. if 'filtered',
        only filtered permutations will be returned. otherwise filtered
        permutations will be deleted from permutation list and leftovers will
        be returned.
    filtermode: takes 'strict' or 'loose' as a string. if 'strict',
        permutations which strictly contain only items which are set in
        dimensional_filterlist will be filtered. if 'loose', permutations which
        contain at least one item which is set in dimensional_filterlist in a
        given dimension are filtered.
    flattend: if True, returns a flattened list of permuted entries.
    verbose: takes values from 0-2 inclusively. 0 = silent, 1 = print filtered
    list, 2 = print all
    print_param: int to dictate how many lines of printout should be generated
    from within loops. use 0 for infinite.
    '''
    if returnwhich not in ['filtered', 'unfiltered']:
        returnwhich = 'filtered'
        print('returnwhich must be either "filtered" or "unfiltered". '
                'defaulting to "filtered"')
    if filtermode not in ['loose', 'strict']:
        filtermode = 'loose'
        print('returnwhich must be either "loose" or "strict". defaulting to '
                '"loose"')

    permutations_taken = len(flatten_list(data_list))
    if verbose > 0:
        print(f'ndim_filter says:\toverall number of permutations = '
        f'{permutations_taken}\t{dimensional_filterlist = }\t{returnwhich = }'
        f'\t{filtermode = }\tverbose level = {verbose}\t{print_param = }\n')
    filtered_list = []
    unfiltered_list = []
    first_init = True

    if filtermode == 'loose':
        for dimension, filter_values in enumerate(dimensional_filterlist):
            # only if filter isnt empty
            if filter_values != []:

                for filter_index, filter in enumerate(filter_values):
                    # iterating over permuted_list
                    for data_sub_list in data_list: 
                        if verbose > 1:
                            print(f'{data_sub_list = }\n')
                        filtered_sub_list = []
                        unfiltered_sub_list = []

                        for permutation_index, perm in enumerate(data_sub_list):
                            # if filter values DOES match perm[dimension]
                            # append permutation to filtered_sub_list
                            if filter == perm[dimension] and perm not in filtered_sub_list and perm not in flatten_list(filtered_list):
                                filtered_sub_list.append(perm)
                                if print_param > permutation_index and verbose > 1:
                                    print(f'filtered: {perm = }')
                                    if print_param-1 == permutation_index:
                                        print('\n')

                            # if filter values DOES NOT match perm[dimension]
                            # append permutation to unfiltered_sub_list
                            elif filter != perm[dimension] and perm not in unfiltered_sub_list and perm not in flatten_list(unfiltered_list) and perm not in filtered_sub_list and perm not in flatten_list(filtered_list):
                                unfiltered_sub_list.append(perm)
                                if print_param > permutation_index and verbose > 1:
                                    print(f'unfiltered: {perm = }')
                                    if print_param-1 == permutation_index:
                                        print('\n')

                        if filtered_sub_list != []:
                            filtered_list.append(filtered_sub_list)
                        if unfiltered_sub_list != []:
                            unfiltered_list.append(unfiltered_sub_list)

                        # try deleting all filtered permutations from 
                        # unfiltered_list
                        for perm in filtered_sub_list:
                            for sublist in unfiltered_list:
                                try:
                                    sublist.remove(perm)
                                except:
                                    pass
                                # clean up possible empty sublists
                                if sublist == []:
                                    unfiltered_list.remove(sublist)

                        if verbose > 1:
                            print(f'\n{filtered_list = }\n{unfiltered_list = }'
                            '\n')

                    data_list = unfiltered_list

                    if verbose > 0:
                        print(f'filtered: {len(flatten_list(filtered_list))}'
                        f'\tunfiltered: {len(flatten_list(unfiltered_list))}\t'
                        f'{dimension = }\t{filter_values = }\tactive filter: '
                        '{filter}\n')
                        
            elif filter_values == [] and not first_init:
                filtered_list = data_list

            if verbose > 0:
                print(f'filtered: {len(flatten_list(filtered_list))}'
                f'\tunfiltered: {len(flatten_list(unfiltered_list))}\t'
                f'{dimension = }\t{filter_values = }') 
            
            
            first_init = False


    elif filtermode == 'strict':
        for dimension, filter_values in enumerate(dimensional_filterlist):
            for filter_index, filter in enumerate(filter_values):

                for data_sub_list in data_list:
                    if verbose > 1:
                        print(f'{data_sub_list[:print_param] = }\n')
                    filtered_sub_list = []
                    unfiltered_sub_list = []
                    # permutations to be removed from filtered_list if found to
                    # be illegal when cheking later filter values
                    late_illegals = []

                    for permutation_index, perm in enumerate(data_sub_list):
                        permutation_is_legal = False

                        # if filter value DOES NOT match perm[dimension],
                        # permutation is illegal. if not yet in any list append
                        # permutation to unfiltered_sub_list
                        if perm[dimension] != filter and perm not in flatten_list(unfiltered_list) and perm not in flatten_list(filtered_list) and perm not in unfiltered_sub_list and perm not in filtered_sub_list:
                            unfiltered_sub_list.append(perm)
                            if print_param > permutation_index and verbose > 2:
                                print(f'unfiltered: {perm = }')

                        # if filter value DOES match perm[dimension],
                        # permutation is legal. if not yet in any filtered_list
                        # append to filtered_sub_list
                        elif perm[dimension] == filter and perm not in flatten_list(filtered_list) and perm not in filtered_sub_list:
                            filtered_sub_list.append(perm)
                            if print_param > permutation_index and verbose > 2:
                                print(f'filtered: {perm = }')

                        # if filter value DOES NOT match perm[dimension],
                        # permutation is illegal. if not first dimension and
                        # perm in filtered_list check for legal possibilities
                        # of other filters in this dimension
                        if perm[dimension] != filter and dimension != 0 and perm in flatten_list(filtered_list):

                            if len(filter_values) > 1:

                                for fil_index, fil in enumerate(filter_values):
                                    if perm[dimension] == fil and filter_values[filter_index] != fil:
                                        permutation_is_legal = True

                            if permutation_is_legal == False:
                                late_illegals.append(perm)
                            if print_param > permutation_index and verbose > 1:
                                print(f'late_illegals: {perm = }')

                    # add filtered items sublist to filtered_list
                    if filtered_sub_list != []:
                        filtered_list.append(filtered_sub_list)

                    # try deleting all later illegals from filtered_list
                    for perm in late_illegals:
                        for sublist in filtered_list:
                            try:
                                if perm in sublist:
                                    sublist.remove(perm)
                                    unfiltered_sub_list.append(perm)
                            except:
                                pass

                # try deleting all filtered permutations from unfiltered_list
                    for perm in flatten_list(filtered_list):
                        try:
                            unfiltered_sub_list.remove(perm)
                        except:
                            pass
                        for sublist in unfiltered_list:
                            try:
                                sublist.remove(perm)
                            except:
                                pass
                            if sublist == []: # clean up possible empty sublists
                                unfiltered_list.remove(sublist)

                    # add unfiltered items sublist to unfiltered_list
                    if unfiltered_sub_list != []:
                        unfiltered_list.append(unfiltered_sub_list)

                    if verbose > 2:
                        print(f'\n{filtered_list = }\n{unfiltered_list = }\n')

                if verbose > 0:
                    print(f'filtered: {len(flatten_list(filtered_list))}'
                    f'\tunfiltered: {len(flatten_list(unfiltered_list))}\t'
                    f'{dimension = }\t{filter_values = }\tactive filter: '
                    f'{filter}\n')

        # after all filters for one dimension are done, init data_list
        # strictly with filtered permutations for next dimensions filters
        if not filter_values == []:
            data_list = filtered_list
        # clean up possible empty sublists only after data_list has been
        # initialized to not confuse iterating loops in filter
        for sublist in filtered_list:
            if sublist == []:                               
                filtered_list.remove(sublist)


    if returnwhich == 'filtered':                    # which list to return
        data_list = filtered_list
    elif returnwhich == 'unfiltered':
        data_list = unfiltered_list

    for perm in filtered_list:                       # sanity check
        if perm in unfiltered_list and verbose > 0:
            print(f'Error in ndimensional_filter: {perm = } has been filtered '
                    'and unfiltered.')
    for perm in unfiltered_list:
        if perm in filtered_list and verbose > 0:
            print(f'Error in ndimensional_filter: {perm = } has been filtered '
                    'and unfiltered.')

    if not flattened:
        return data_list
    else:
        return flatten_list(data_list)  # flatten nested lists


def ndimensional_permute_filtered(permlist: list,
                                    dimensional_filterlist: list[list],
                                    returnwhich: str = 'filtered',
                                    filtermode: str = 'loose',
                                    max_duplicates: int = 0,
                                    flattened: bool = False,
                                    verbose: int = 0,
                                    print_param: int = 3) -> list:
    ''' Function for permuting entries of permlist, filtering out entries in
    filterlist-lists. filterlist needs to be set with empty lists in dimension
    which are not to be filtered to dictate dimensionality of permutation
    correctly.

    permlist: list of entries to permute.
    dimensional_filterlist: n-dimensional list of lists of entries to filter
        out. format is [[dimension 1], [dimension 2], ...].
        len(filterlist) = number of inner lists = number of dimensions and
        dictates dimensionality of permutation. if inner lists are empty, no
        filtering will take place in that dimension. otherwise, all
        permutations which contain any item of inner lists at defined dimension
        will be filtered.
    returnwhich: takes 'filtered' or 'unfiltered' as a string. if 'filtered',
        only filtered permutations will be returned. Otherwise filtered 
        permutations will be deleted from permutation list and leftovers will
        be returned.
    filtermode: takes 'strict' or 'loose' as a string. if 'strict',
        permutations which strictly contain only items which are set in
        dimensional_filterlist will be filtered. if 'loose', permutations which
        contain at least one item which is set in dimensional_filterlist in a
        given dimension are filtered.
    max_duplicates: if set to a number > 0, permutations which contain more
        than max_duplicates of the same item in a given permutation will be
        filtered out. This is useful to set to reduce computation time.
    flattened: if True, returns a flattened list of permuted entries.
    verbose: takes values from 0-2 inclusively for different levels of verbosity
    print_param: int to dictate how many lines of printout should be generated
        from within loops. use 0 for infinite.
    '''

    dimensions = len(dimensional_filterlist)

    if returnwhich not in ['filtered', 'unfiltered']:
        returnwhich = 'filtered'
        print('returnwhich must be either "filtered" or "unfiltered". '
                'defaulting to "filtered"')
    if filtermode not in ['loose', 'strict']:
        filtermode = 'loose'
        print('returnwhich must be either "loose" or "strict". defaulting to '
                '"loose"')

    # permuting, flattened needs to be False here #
    permuted_list = ndimensional_permute(permlist=permlist,
                                dimensions=dimensions,
                                max_duplicates=max_duplicates,
                                flattened=False,
                                verbose=verbose)

    if verbose > 2:
        print(f'ndimensional_permute_filtered: {permuted_list = }')
    if verbose > 1:
        pass
        #print(f'ndimensional_permute_filtered: {permuted_list[:print_param][:print_param][:print_param] = }')

    # filtering, flattened needs to be False here #
    permuted_filtered_list = ndimensional_filter(data_list=permuted_list,
                                dimensional_filterlist=dimensional_filterlist, 
                                returnwhich=returnwhich,
                                filtermode=filtermode,
                                flattened=False,
                                verbose=verbose,
                                print_param=print_param)

    if not flattened:
        return permuted_filtered_list  # not flattened
    else:
        return flatten_list(permuted_filtered_list)  # flatten nested lists


@gu1.timerdecorator(4, 's')
def main_permute():
    #perm = ['Paul', 'Basti', 'Merle', 'Kim', 'Jonas', 'Lennard']
    #perm = ['ying young', 'sheesh', 'skrrr skrrrt', 'therapiegalaxie', 'kraterkosmos', 'narkosehelikopter', 'hitler']
    perm = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    perm = [0,1,2,3]

    filter_list = [['ying young'], ['sheesh', 'skrrr skrrrt'], [],
        ['therapiegalaxie', 'kraterkosmos', 'narkosehelikopter'], []]

    filter_list = [[0], [1], ['lol'], [(1, 2)], [], []]
    filter_list = [[], [], [], []]
    filter_list = [[],[],['A','B','C','D','E','F'],['A','B','C','D','E','F']]
    
    filter_list = [[],[],[0,2,3],[3]]
    
    permuted_filtered2 = ndimensional_permute_filtered(permlist=perm,
                                            dimensional_filterlist=filter_list,
                                            returnwhich='filtered',
                                            filtermode='strict',
                                            max_duplicates=1,
                                            flattened=True,
                                            verbose=2,
                                            print_param=3)
    print(f'{permuted_filtered2 = }\n')
    

if __name__ == '__main__':
    main_permute()
    

