
#%%

### only needed for timing decorator ###
if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from _usable_util import general_util_1 as gu1
    from _usable_util import formatter
else: timer = None
########################################
    
from itertools import product
from scipy.special import binom

from typing import Any
from collections.abc import Iterable
from functools import partial
from multiprocessing import cpu_count, Pool, get_context, Pipe, Lock, Process, Queue

import sys, os


def flatten_list(iterable_of_iterable: Iterable[Iterable[Any]]) -> list:
    return [item for subiter in iterable_of_iterable for item in subiter]

def chunker(to_split:Iterable[Any], chunksize:int) -> list[list[Any]]:
    """
    Takes list (to_split) to return list of lists of chunked data.
    chunksize defines the amount of items in each sublist.
    """
    # chunkborders are defining index ranges for each single chunk?
    # range(start, stop, step)
    chunkborders = range(0, len(to_split), chunksize)
    chunked = [to_split[border:border + chunksize] for border in chunkborders]
    # filter all None values from last Chunk if there are any
    if None in chunked[-1]:
        chunked[-1] = list(filter(None, chunked[-1]))
    return chunked
                                        
def max_dup_filter(data_iter: Iterable[Iterable[Any]],
                    max_duplicates: int,
                    verbose: int = 0) \
                                    -> tuple[list[Any], list[Any]]:
    """
    Filters iter of subiter of items by max amount of the same items in subiters
    Returns tuple of filtered- and unfiltered_list where all entries have been
        filtered by max_duplicates integer. Filtered are all entries with less
        then or equal to max_duplicates. unfiltered the rest.
    """
    if verbose > 2:
        print(f'{os.getpid() = }')
    filtered_list = []
    unfiltered_list = []
    first = True
    #for combination in next(cartesian_product_gen):
    for combination in data_iter:
        illegal = False
        # for each item check if combination contains more than
        # max_duplicates of the same item
        for item in combination:
            # status printing
            if first and verbose > 2:
                print(f'{type(combination) = }\t{combination = }\t{item = }\t '
                    f'{combination.count(item) = }')
                first = False
            # acutal checking here
            if combination.count(item) > max_duplicates:
                illegal = True
                unfiltered_list.append(combination)
                if verbose > 2:
                    print(f'{combination = }\t\t{item = }')
                break
        if not illegal:
            filtered_list.append(combination)

    return filtered_list, unfiltered_list



#@gu1.timerdecorator()
def ndimensional_product(prodit: Iterable[Any],
                        dimensions: int,
                        maxduplicates: int = 0,
                        returnwhich:str = 'filtered',
                        verbose: int = 0)               -> list[tuple[Any]]:
    """
    Function for n-dimensional permuting all entries of permlist and filtering
        resulting tuples by amount of duplicates of their elements. Returns a
        list of tuples.
    prodit: list of entries to permute, takes any datatypes.
    dimensions: number of dimensions to permute itmes from permlist to.
    max_duplicates: if set to a number > 0, permutations which contain more
        than max_duplicates of the same item in a given permutation will be
        filtered out. Defaulting to 0.
    flattened: if True, returns a flattened list of permuted entries.
    verbose: 0 for no printouts, 1 for printouts, 2 for all printouts
    """

    if returnwhich not in ['filtered', 'unfiltered']:
        returnwhich = 'filtered'
        print('returnwhich must be either "filtered" or "unfiltered". '
                'defaulting to "filtered"')
    if maxduplicates < 0:
        maxduplicates = 0
    # max number of possible combinations to be calculated
    combinations = len(prodit) ** dimensions
    filtered_list = []          # init empty lists for storing results and
    unfiltered_list = []        # correct reporting at the end

    to_spawn = cpu_count()      # number of processes to spawn
    multi_arr = None            # if threshold is reached, this list will be
                                # used for chunking
    multi_factor = 2            # arbitrary factor for adjustment of chunksize
                                # and amount of chunks
    threshold = 50_000          # min data before chunking and multiprocessing
    count = 1                   # init counter=1 for automatic chunk sizes
    # get generator from itertools and listify. next version of this script will
    # rely on generators instead of performing such list operations with them
    cart_prod_gen = product(prodit, repeat=dimensions)
    cart_prod_list = list(cart_prod_gen)

    if verbose > 0:
        print(f' ndim_product says:\t{dimensions = }\t{maxduplicates = }\t'
                f'possible combinations: {combinations}')
        if multi_arr is not None:
                print(f' Chunks: {chunksneeded}\tChunksize: {chunksize}')

    if maxduplicates == 0:
        filtered_list = cart_prod_list

    elif maxduplicates > 0:
        # following code determines chunks size from threshold
        if combinations > threshold:
            chunksneeded = cpu_count() * multi_factor * count
            chunksize = combinations // chunksneeded + 1
            while chunksize > threshold:
                count += 1
                chunksneeded = cpu_count() * multi_factor * count
                chunksize = combinations // chunksneeded + 1
            multi_arr = chunker(cart_prod_list, chunksize)

        if multi_arr is None:
            filtered_list, unfiltered_list = max_dup_filter(cart_prod_list,
                                                            maxduplicates)

        elif multi_arr is not None:
            with get_context('spawn').Pool(processes=to_spawn) as pool:

                multiresult = pool.starmap(max_dup_filter,
                                            [(multi_arr[i],
                                            maxduplicates, verbose) for i in \
                                            range(len(multi_arr))])
                # [0] and [1] are filtered and unfiltered results, while each
                # arr equals the result of a single chunk
                for arr in multiresult:
                    filtered_list.extend(arr[0])
                    unfiltered_list.extend(arr[1])

        if verbose > 1:
            print(f'{len(multi_arr) = }\t{len(multiresult) = }\t'
                f'{len(multiresult[0]) = }\t{len(multiresult[0][0]) = }\t'
                f'{len(multiresult[0][0][0]) = }\t'
                f'{multiresult[0][0][0] = }\n')
            
    nfiltered = len(filtered_list)
    nunfiltered = len(unfiltered_list)
    if combinations != nfiltered + nunfiltered:
        print(f'sanity check failed:\n{combinations = }\t{nfiltered = }\t '
            f'{nunfiltered = }')
    if verbose > 0 and maxduplicates > 0:
        print(f'removed {nunfiltered} combinations of {combinations} '
                f'containing more than {maxduplicates} duplicates\n')

    if returnwhich == 'filtered':
        return filtered_list
    elif returnwhich == 'unfiltered':
        return unfiltered_list


def loose_filter(data: Iterable[Any],
                    filter: Iterable[Iterable[Any]]) \
                                                    -> tuple[list, list]:
    filtered_list = []
    unfiltered_list = []
    for combination in data:
        filtered = False

        for dimension, filter_values in enumerate(filter):
            # go to next dimension if filter is empty
            if filter_values == []:
                continue
            # append perm to filtered_sub if it is in filter and break
            elif filter_values != [] and \
                combination[dimension] in filter_values:

                filtered_list.append(combination)
                filtered = True
                break
        # if perm hasnt been unfiltered, append to filtered_sub_list 
        if not filtered:
            unfiltered_list.append(combination)

    return filtered_list, unfiltered_list

def strict_filter(data: Iterable[Any],
                    filter: Iterable[Iterable[Any]]) \
                                                    -> tuple[list, list]:
    filtered_list = []
    unfiltered_list = []
    for combination in data:
        unfiltered = False

        for dimension, filter_values in enumerate(filter):
            # go to next dimension if filter is empty
            if filter_values == []:
                continue
            # go to next dimension if perm[dimension] is in filter
            elif filter_values != [] and \
                combination[dimension] in filter_values:
                continue
            # append perm[dimension] to unfiltered_sub if not in filter
            # and break
            elif filter_values != [] and \
                combination[dimension] not in filter_values:
                unfiltered_list.append(combination)
                unfiltered = True
                break
        # if perm hasnt been unfiltered, append to filtered_sub_list 
        if not unfiltered:
            filtered_list.append(combination)
                    
    return filtered_list, unfiltered_list

#@gu1.timerdecorator(2, 'ms')
def ndimensional_filter(data_iter: Iterable[Iterable[Any]],
                        dimensional_filterlist: Iterable[Iterable[Any]],
                        returnwhich: str = 'filtered',
                        filtermode: str = 'loose',
                        verbose: int = 0) \
                                            -> list[tuple]:
    '''
    Filtering n-dimensional data lists by items in dimensional_filterlist
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

    combinations = len(data_iter)
    if verbose > 0:
        print(f' ndim_filter says:\treceived combinations = '
        f'{combinations}\t{filtermode = }\t{returnwhich = }'
        f'\n{dimensional_filterlist = }')

    filtered_list = []
    unfiltered_list = []
    # if no filter is given in ANY dimension, return all permutations
    empty_filter = True
    for f in dimensional_filterlist:
        if f != []:
            empty_filter = False
            break

    tospawn = cpu_count()      # number of processes to spawn
    multi_arr = None            # if threshold is reached, multi_arr will be
    multi_factor = 2            # used for chunked data. m_factor for adjustment
    threshold = 50_000
    count = 1                   # counter for automatic chunk sizes
    # following code determines chunks size from threshold
    if combinations > threshold:
        chunksneeded = cpu_count() * multi_factor * count
        chunksize = combinations // chunksneeded + 1
        while chunksize > threshold:
            count += 1
            chunksneeded = cpu_count() * multi_factor * count
            chunksize = combinations // chunksneeded + 1

        multi_arr = chunker(list(data_iter), chunksize)

    if filtermode == 'loose':
        filterfunc = loose_filter
    elif filtermode == 'strict':
        filterfunc = strict_filter

    if not empty_filter:
        if multi_arr is None:
            res = filterfunc(data_iter, dimensional_filterlist)
            filtered_list, unfiltered_list = res
        else:
            with get_context('spawn').Pool(processes=tospawn) as pool:

                multiresult = pool.starmap(filterfunc, [(multi_arr[i],
                                            dimensional_filterlist) for i in \
                                            range(len(multi_arr))])
                # arr[0] and [1] are filtered and unfiltered results, while each
                # arr equals the result of a single chunk
                for arr in multiresult:
                    filtered_list.extend(arr[0])
                    unfiltered_list.extend(arr[1])
    
    if verbose > 0:
        print(f'filtered: {len(filtered_list)}'
        f'\tunfiltered: {len(unfiltered_list)}')

    if returnwhich == 'filtered' and not empty_filter: # which list to return
        data_iter = filtered_list
    elif returnwhich == 'unfiltered' and not empty_filter:
        data_iter = unfiltered_list
    elif returnwhich == 'filtered' and empty_filter:
        data_iter = data_iter
    elif returnwhich == 'unfiltered' and empty_filter:
        data_iter = []

    return data_iter


def cartesian_product_filtered(prodit: Iterable[Any],
                                dimensional_filterlist: Iterable[Iterable[Any]],
                                returnwhich: str = 'filtered',
                                filtermode: str = 'loose',
                                max_duplicates: int = 0,
                                verbose: int = 0) \
                                                    -> list[tuple[Any]]:
    """
    Function for brute forcing a cartesian product of all items in prodit and
    filtering by maximum number of duplicated items within all items of the
    cartesian product specific filterlist.
    filterlist-lists. filterlist needs to be set with empty lists in dimensions
    which are not to be filtered to dictate dimensionality of permutation
    correctly.

    prodit: list of entries to permute.
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
    """

    dimensions = len(dimensional_filterlist)

    if returnwhich not in ['filtered', 'unfiltered']:
        returnwhich = 'filtered'
        print('returnwhich must be either "filtered" or "unfiltered". '
                'defaulting to "filtered"')
    if filtermode not in ['loose', 'strict']:
        filtermode = 'loose'
        print('returnwhich must be either "loose" or "strict". defaulting to '
                '"loose"')

    cartesian_product_list = ndimensional_product(prodit=prodit,
                                dimensions=dimensions,
                                maxduplicates=max_duplicates,
                                verbose=verbose)
    if verbose > 2:
        print(f'cartesian product: {cartesian_product_list = }')
    product_filtered_list = ndimensional_filter(
                                data_iter=cartesian_product_list,
                                dimensional_filterlist=dimensional_filterlist, 
                                returnwhich=returnwhich,
                                filtermode=filtermode,
                                verbose=verbose)

    return product_filtered_list


#@gu1.timerdecorator(4, 's')
def main_permute():
    toprod = ['Paul', 'Basti', 'Merle', 'Kim', 'Jonas', 'Lennard']
    toprod = ['ying young', 'sheesh', 'skrrr skrrrt', 'therapiegalaxie', 'kraterkosmos', 'narkosehelikopter', 'hitler']
    toprod = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    toprod = [0,1,2,3,4,5,6,7,8,9]
    toprod = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    toprod = ['ying young', 'sheesh', 'skrrr skrrrt', 'therapiegalaxie', 'kraterkosmos', 'narkosehelikopter', 'hitler']

    filter_list = [[0], [1], ['lol'], [(1, 2)], [], []]
    filter_list = [[],[],['A','B','C','D','E','F'],['A','B','C','D','E','F']]
    filter_list = [[0],[0,1],[0,1,2],[]]
    filter_list = [[],[]]
    filter_list = [[], [], [], [], [], []]
    filter_list = [[], [], [], []]
    filter_list = [['ying young'], [], ['sheesh', 'skrrr skrrrt'], [],
                ['therapiegalaxie', 'kraterkosmos', 'narkosehelikopter'], []]
    
    pf2 = cartesian_product_filtered(prodit=toprod,
                                    dimensional_filterlist=filter_list,
                                    returnwhich='filtered',
                                    filtermode='strict',
                                    max_duplicates=2,
                                    verbose=1,
                                    print_param=10)
    
    for p in pf2[:10]:
        print(f'{p}')    

    pf2 = formatter.stringify(data=pf2, delimiter=' ')
    formed = formatter.formatter(iterable=pf2,
                                columns=2,
                                prefix=formatter.line_numbers(10))
    for f in formed[:10]:
        print(f'{f}')
        
'''wanted behaviour filtering perm [1,2,3] with [[1],[1,2],[]]:
loosely:
    if dim 0 contains 1 OR dim 1 contains 1 or 2: filter permutation
    else unfilter permutation
strictly:
    if dim 0 contains 1 AND dim 1 contains 1 or 2: filter permutation
    else unfilter permutation
'''
    

if __name__ == '__main__':

    main_permute()
    


# %%
