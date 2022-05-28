#%%

### only needed for timing decorator ###
if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from _usable_util import general_util_1 as gu1
    timer = gu1.timerdecorator()
else: timer = None
########################################
    
#import sys
#sys.path.append('..')
#from _usable_util import general_util_1 as gu1

def flatten_list(list_of_iterable: list[list]) -> list:
    return [item for sublist in list_of_iterable for item in sublist]


#@gu1.timerdecorator(2, 'ms')
def ndimensional_product(permlist: list, dimensions: int, max_duplicates: 
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


#@gu1.timerdecorator(2, 'ms')
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
    filter_dimensions = len(dimensional_filterlist)
    first_init = True
    empty_filter = True
    
    for f in dimensional_filterlist:
        if f != []:
            empty_filter = False

    if filtermode == 'loose' and not empty_filter:
        for data_sub_list in data_list:
            filtered_sub_list = []
            unfiltered_sub_list = []

            for perm_index, perm in enumerate(data_sub_list):
                filtered = False

                for dimension, filter_values in enumerate(dimensional_filterlist):
                    
                    # go to next dimension if filter is empty
                    if filter_values == []:
                        continue

                    # append perm[dimension] to filtered_sub if it is in filter
                    # and break
                    elif filter_values != [] and perm[dimension] in filter_values:
                        filtered_sub_list.append(perm)
                        filtered = True
                        break
                    
                # if perm hasnt been unfiltered, append to filtered_sub_list 
                if not filtered:
                    unfiltered_sub_list.append(perm)
                        
            # only append sublists if they are not empty
            if filtered_sub_list != []:
                filtered_list.append(filtered_sub_list)
            if unfiltered_sub_list != []:
                unfiltered_list.append(unfiltered_sub_list)

            if verbose > 1:
                print(f'filtered: {len(flatten_list(filtered_list))}'
                f'\tunfiltered: {len(flatten_list(unfiltered_list))}')
    
    elif filtermode == 'strict' and not empty_filter:
        for data_sub_list in data_list:
            filtered_sub_list = []
            unfiltered_sub_list = []

            for perm_index, perm in enumerate(data_sub_list):
                unfiltered = False

                for dimension, filter_values in enumerate(dimensional_filterlist):
                    
                    # go to next dimension if filter is empty
                    if filter_values == []:
                        continue

                    # go to next dimension if perm[dimension] is in filter
                    elif filter_values != [] and perm[dimension] in filter_values:
                        continue
                    
                    # append perm[dimension] to unfiltered_sub if not in filter
                    # and break
                    elif filter_values != [] and perm[dimension] not in filter_values:
                        unfiltered_sub_list.append(perm)
                        unfiltered = True
                        break
                    
                # if perm hasnt been unfiltered, append to filtered_sub_list 
                if not unfiltered:
                    filtered_sub_list.append(perm)
                        
            # only append sublists if they are not empty
            if filtered_sub_list != []:
                filtered_list.append(filtered_sub_list)
            if unfiltered_sub_list != []:
                unfiltered_list.append(unfiltered_sub_list)

            if verbose > 1:
                print(f'filtered: {len(flatten_list(filtered_list))}'
                f'\tunfiltered: {len(flatten_list(unfiltered_list))}')


    if returnwhich == 'filtered' and not empty_filter: # which list to return
        data_list = filtered_list
    elif returnwhich == 'unfiltered' and not empty_filter:
        data_list = unfiltered_list
    elif returnwhich == 'filtered' and empty_filter:
        data_list = data_list
    elif returnwhich == 'unfiltered' and empty_filter:
        data_list = []

    if not empty_filter:
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


def cartesian_product_filtered(permlist: list,
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
    permuted_list = ndimensional_product(permlist=permlist,
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


#@gu1.timerdecorator(4, 's')
def main_cpf():
    #perm = ['Paul', 'Basti', 'Merle', 'Kim', 'Jonas', 'Lennard']
    #perm = ['ying young', 'sheesh', 'skrrr skrrrt', 'therapiegalaxie', 'kraterkosmos', 'narkosehelikopter', 'hitler']
    perm = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    perm = [0,1,2,3]

    filter_list = [['ying young'], ['sheesh', 'skrrr skrrrt'], [],
        ['therapiegalaxie', 'kraterkosmos', 'narkosehelikopter'], []]

    filter_list = [[0], [1], ['lol'], [(1, 2)], [], []]
    filter_list = [[], [], [], []]
    filter_list = [[],[],['A','B','C','D','E','F'],['A','B','C','D','E','F']]
    
    filter_list = [[0],[0,1],[0,1,2],[]]
    filter_list = [[],[]]
    
    pf2 = ndimensional_permute_filtered(permlist=perm,
                                        dimensional_filterlist=filter_list,
                                        returnwhich='filtered',
                                        filtermode='loose',
                                        max_duplicates=3,
                                        flattened=True,
                                        verbose=1,
                                        print_param=10)
    
    
    for p in pf2:
        print(f'{p}')    

        #joined = ' '.join(pf2)
        #print(f'{pf2 = }\n')
        
'''wanted behaviour filtering perm [1,2,3] with [[1],[1,2],[]]:
loosely:
    if dim 0 contains 1 OR dim 1 contains 1 or 2: filter permutation
    else unfilter permutation
strictly:
    if dim 0 contains 1 AND dim 1 contains 1 or 2: filter permutation
    else unfilter permutation
'''
    

if __name__ == '__main__':
    main_cpf()
    

