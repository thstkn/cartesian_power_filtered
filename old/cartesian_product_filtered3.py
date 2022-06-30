
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
from math import ceil
# for type annotations:
from typing import Any, Generator, Iterable
# for superclasses for subclassing by user
#from collections.abc import Iterable
from functools import partial
from multiprocessing import cpu_count, Pool, get_context, Pipe, Lock, Process, Queue

import sys, os

def max_dup_check(iterable: Iterable[Any], max_duplicates: int) -> bool:
    """
    determines if any item in input iterable is found more than
        max_duplicates times within iterable.
    returns true if no item has been found more than max_dup times
        in iterable
    """

    print(f'{iterable = }')
    for item in iterable:
        if iterable.count(item) > max_duplicates:
            print(f'{item = }\t{iterable.count(item) = }\n')
            return False
    print(f'{item = }\t{iterable.count(item) = }\n')
    return True

def ndimensional_filter_lists(data_iterable: Iterable[Iterable[Any]],
                        filter: Iterable[Iterable[Any]], 
                        max_duplicates: int,
                        filtermode: str) \
                                                    -> tuple[list, list]:
    filtered_list = []
    unfiltered_list = []
    checkdups = False
    if max_duplicates > 0:
        checkdups = True
    else:
        maxduplegal = True

    print(f'Hi, im process {os.getpid()} with:\n{data_iterable = }\n')

    for combination in data_iterable:
        filtered = False
        if checkdups:
            maxduplegal = max_dup_check(combination, max_duplicates)

        #print(f'{maxduplegal = }')

        if maxduplegal and filtermode == 'loose':
            for dimension, filter_values in enumerate(filter):
                # go to next dimension if filter is empty
                if filter_values == []:
                    continue
            # append combination to filtered_sub if it is in filter and break
                elif filter_values != [] and \
                    combination[dimension] in filter_values:

                    filtered_list.append(combination)
                    filtered = True
                    break
            # if combination hasnt been unfiltered, append to filtered_sub_list 
            if not filtered:
                unfiltered_list.append(combination)

        if maxduplegal and filtermode == 'strict':
            for dimension, filter_values in enumerate(filter):
                # go to next dimension if filter is empty
                if filter_values == []:
                    continue
                # go to next dimension if combination[dimension] is in filter
                elif filter_values != [] and \
                    combination[dimension] in filter_values:
                    continue
# append combination[dimension] to unfiltered_sub if not in filter and break
                elif filter_values != [] and \
                    combination[dimension] not in filter_values:
                    unfiltered_list.append(combination)
                    unfiltered = True
                    break
            # if combination hasnt been unfiltered, append to filtered_sub_list 
            if not unfiltered:
                filtered_list.append(combination)

        else:
            unfiltered_list.append(combination)

    return filtered_list, unfiltered_list

def ndimensional_filter_single(combination: Iterable[Any],
                                filter: Iterable[Iterable[Any]], 
                                max_duplicates: int,
                                filtermode: str) \
                                -> tuple[tuple | None, tuple | None]:
    checkdups = False
    if max_duplicates > 0:
        checkdups = True
    else:
        maxduplegal = True

    print(f'Hi, im process {os.getpid()} with:\n{combination = }\n')

    if checkdups:
        maxduplegal = max_dup_check(combination, max_duplicates)

    filtered = None
    unfiltered = None
    if maxduplegal and filtermode == 'loose':
        for dimension, filter_values in enumerate(filter):
            # go to next dimension if filter is empty
            if filter_values == []:
                continue
        # append combination to filtered_sub if it is in filter and break
            elif filter_values != [] and \
                combination[dimension] in filter_values:
                    filtered = combination
        # if combination hasnt been unfiltered, append to filtered_sub_list 
        if filtered is None:
            unfiltered = combination

    if maxduplegal and filtermode == 'strict':
        for dimension, filter_values in enumerate(filter):
            # go to next dimension if filter is empty
            if filter_values == []:
                continue
            # go to next dimension if combination[dimension] is in filter
            elif filter_values != [] and \
                combination[dimension] in filter_values:
                continue
# append combination[dimension] to unfiltered_sub if not in filter and break
            elif filter_values != [] and \
                combination[dimension] not in filter_values:
                    unfiltered = combination
        # if combination hasnt been unfiltered, append to filtered_sub_list 
        if not unfiltered:
            filtered_list.append(combination)

    else:
        unfiltered_list.append(combination)

    return (filtered, unfiltered)


def multiproc(dimensional_filterlist: list[list[Any]],
                max_duplicates: int,
                filtermode: str,
                chunked_cart_prod_gen: Generator[tuple, None, None],
                imapchunksize: int,
                prodgenchunksize: int) \
                                                    -> tuple[list, list]:
    filtered_list = []
    unfiltered_list = []
    # number of processes to spawn for multiprocessing
    tospawn = cpu_count()

    partial_filter = partial(ndimensional_filter_lists,
                            filter=dimensional_filterlist,
                            max_duplicates=max_duplicates,
                            filtermode=filtermode)

    with get_context('spawn').Pool(processes=tospawn) as pool:
        for res in pool.imap(partial_filter,
                            chunked_cart_prod_gen,
                            chunksize=imapchunksize):
            filtered_list.append(res[0])
            unfiltered_list.append(res[1])
            print(f'{res[:5] = }\t{res[1][:5] = }') 

    return filtered_list, unfiltered_list

def chunked_generator(generator: Generator[tuple, None, None],
                            chunksize: int) \
                                                -> Generator[tuple, None, None]:
    """
    returns generator chunk wise.
    """
    for i, data in enumerate(generator):
        yield data
        if i >= chunksize:
            break


def cartesian_product_filtered(alphabet: Iterable[Any],
                                dimensional_filterlist: Iterable[Iterable[Any]],
                                filtermode: str,
                                returnwhich: str = 'filtered',
                                max_duplicates: int = 0,
                                imapchunksize: int = 1,
                                verbose: int = 0) \
                    -> list[tuple[Any]] | Generator[tuple, None, None]:
    """
    Function for brute forcing a cartesian product of all items in prodit and
    filtering by maximum number of duplicated items within all items of the
    cartesian product specific filterlist.
    filterlist-lists. filterlist needs to be set with empty lists in dimensions
    which are not to be filtered to dictate dimensionality of combination
    correctly.

    prodit: list of entries to permute.
    dimensional_filterlist: n-dimensional list of lists of entries to filter
        out. format is [[dimension 1], [dimension 2], ...].
        len(filterlist) = number of inner lists = number of dimensions and
        dictates dimensionality of combination. if inner lists are empty, no
        filtering will take place in that dimension. otherwise, all
        combinations which contain any item of inner lists at defined dimension
        will be filtered.
    returnwhich: takes 'filtered' or 'unfiltered' as a string. if 'filtered',
        only filtered combinations will be returned. Otherwise filtered 
        combinations will be deleted from combination list and leftovers will
        be returned.
    filtermode: takes 'strict' or 'loose' as a string. if 'strict',
        combinations which strictly contain only items which are set in
        dimensional_filterlist will be filtered. if 'loose', combinations which
        contain at least one item which is set in dimensional_filterlist in a
        given dimension are filtered.
    max_duplicates: if set to a number > 0, combinations which contain more
        than max_duplicates of the same item in a given combination will be
        filtered out. This is useful to set to reduce computation time.
    flattened: if True, returns a flattened list of permuted entries.
    verbose: takes values from 0-2 inclusively for different levels of verbosity
    print_param: int to dictate how many lines of printout should be generated
        from within loops. use 0 for infinite.
    """

    if returnwhich not in ['filtered', 'unfiltered']:
        returnwhich = 'filtered'
        print('returnwhich must be either "filtered" or "unfiltered". '
                'defaulting to "filtered"')
    if filtermode not in ['loose', 'strict']:
        filtermode = 'loose'
        print('returnwhich must be either "loose" or "strict". defaulting to '
                '"loose"')

    # determine meta data for status printing and chunksiz estimation
    alphsize = len(alphabet) 
    dimensions = len(dimensional_filterlist)
    combinations = alphsize ** dimensions

    filtered_list = []
    unfiltered_list = []

    cart_prod_gen = product(alphabet, repeat=dimensions)

    # if no filter is given in ANY dimension, return all combinations
    empty_filter = True
    for f in dimensional_filterlist:
        if f != []:
            empty_filter = False
            break

    multi_factor = 1        # multi_factor for adjustment of chunksize
                            # chunksneeded
    threshold = 50_000      # threshold for deciding if mulitiproc will be used
    count = 1               # counter for automatic chunk sizes
    # following code determines chunks size from threshold and cpu count
    # (tospawn). if threshold isnt reached, dont use multi processing
    multi_flag = False
    if combinations > threshold:
        multi_flag = True
        chunksneeded = cpu_count() * multi_factor * count
        generatorchunksize = int(ceil(combinations // chunksneeded))
        while generatorchunksize > threshold:
            count += 1
            chunksneeded = cpu_count() * multi_factor * count
            generatorchunksize = int(ceil(combinations // chunksneeded))

    if verbose > 0: # status print
        print(f'cartesian product filtered:\tmax possible combinations '
                f'({alphsize}^{dimensions}) = {combinations}\n{filtermode = }'
                f'\t{returnwhich = }\n')
        for i, filt in enumerate(dimensional_filterlist):
            print(f'dim: {i + 1}\t{filt}')
        if multi_flag:
            print(f'\nprocessing data using {chunksneeded} chunks of size '
                    f'{generatorchunksize}')

    if not empty_filter:
        if not multi_flag:
            res = ndimensional_filter_lists(list(cart_prod_gen),
                                                dimensional_filterlist,
                                                max_duplicates,
                                                filtermode)
            filtered_list, unfiltered_list = res

        elif multi_flag:
            partial_filter = partial(ndimensional_filter_lists,
                                        filter=dimensional_filterlist,
                                        max_duplicates=max_duplicates,
                                        filtermode=filtermode)

            print(f'{partial_filter(chunked_generator(cart_prod_gen, 10)) = }')

            partial_filter = partial(ndimensional_filter_single,
                                        filter=dimensional_filterlist,
                                        max_duplicates=max_duplicates,
                                        filtermode=filtermode)

            # number of processes to spawn for multiprocessing
            tospawn = cpu_count()

            with get_context('spawn').Pool(processes=tospawn) as pool:

                for res in pool.imap(partial_filter,
                        chunked_generator(cart_prod_gen, generatorchunksize),
                        chunksize=imapchunksize):
                    filtered_list.append(res[0])
                    unfiltered_list.append(res[1])
                print(f'{res[:5] = }\t{res[1][:5] = }') 

                #res = multiproc(dimensional_filterlist=dimensional_filterlist, max_duplicates=max_duplicates, filtermode=filtermode, chunked_cart_prod_gen=chunk, imapchunksize=1)

    nfiltered = len(filtered_list)
    nunfiltered = len(unfiltered_list)
    assert(combinations == nfiltered + nunfiltered), f'sanity check failed'
    if combinations != nfiltered + nunfiltered:
        print(f'sanity check failed\t{combinations = }\t{nfiltered = }\t'
                f'{nunfiltered = }')
        raise SanityCheckExcpetion
    if verbose > 0:
        print(f'filtered: {nfiltered}'
                f'\tunfiltered: {nunfiltered}')

    if returnwhich == 'filtered' and not empty_filter: # which list to return
        result = filtered_list
    elif returnwhich == 'unfiltered' and not empty_filter:
        result = unfiltered_list
    elif returnwhich == 'filtered' and empty_filter:
        try:
            result = list(cart_prod_gen)
        except Exception as e:
            print(f'{e}\n returning generator instead of result list')
            result = cart_prod_gen
    elif returnwhich == 'unfiltered' and empty_filter:
        result = []

    return result

class SanityCheckExcpetion(Exception):
    pass

#@gu1.timerdecorator(4, 's')
def main_permute():
    toprod = ['Paul', 'Basti', 'Merle', 'Kim', 'Jonas', 'Lennard']
    toprod = ['ying young', 'sheesh', 'skrrr skrrrt', 'therapiegalaxie', 'kraterkosmos', 'narkosehelikopter', 'hitler']
    toprod = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    toprod = [0,1,2,3,4,5,6,7,8,9]
    toprod = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    filter_list = [[0], [1], ['lol'], [(1, 2)], [], []]
    filter_list = [['ying young'], [], ['sheesh', 'skrrr skrrrt'], [],
                ['therapiegalaxie', 'kraterkosmos', 'narkosehelikopter'], []]
    filter_list = [[], [], [], [], [], []]
    filter_list = [[], [], [], []]
    filter_list = [[],[],['A','B','C','D','E','F'],[0,1,2,'A','B','C','D','E','F']]
    
    cpf3 = cartesian_product_filtered(alphabet=toprod,
                                        dimensional_filterlist=filter_list,
                                        returnwhich='filtered',
                                        filtermode='strict',
                                        max_duplicates=0,
                                        verbose=1)
    print(f'\nafter cpf3\n')
# make hexcodes from tuples
    cpf3 = formatter.stringify(iterlist=cpf3, delimiter='')
    formed = formatter.formatter(toform=cpf3,
                                columns=16,
                                prefix=formatter.line_numbers(10))
    for f in formed[:10]:
        print(f'{f}')
        
'''wanted behaviour filtering perm [1,2,3] with [[1],[1,2],[]]:
loosely:
    if dim 0 contains 1 OR dim 1 contains 1 or 2: filter combination
    else unfilter combination
strictly:
    if dim 0 contains 1 AND dim 1 contains 1 or 2: filter combination
    else unfilter combination
'''
    

if __name__ == '__main__':

    main_permute()
    


# %%
