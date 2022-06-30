#%%

########################################
if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from _usable_util.formatting import formatter
    from _usable_util.read_write_files import write_to_file
    from _usable_util.formatting.thousands_formatter \
            import thousands_formatter as tf
########################################
    
from itertools import product
from math import ceil
# for type annotations:
from typing import Any, Generator, Iterable
# for superclasses for subclassing by user
#from collections.abc import Iterable
from functools import partial
from datetime import datetime
from multiprocessing import cpu_count, get_context 

import sys

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
    # prevent function call of max_dup_check if max_duplicates is not 0
    if max_duplicates > 0:
        checkdups = True
    else:   # if max_duplicates is 0 set all to legal
        maxduplegal = True 
    #print(f'Hi, im process {os.getpid()}\t{data_iterable[:2] = }')

    for combination in data_iterable:
        # init flags for each combination
        filtered = False
        unfiltered = False

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
                    #print(f'filtered ({filtermode}):{combination}')

                    break
# if combination hasnt been unfiltered, append to filtered_sub_list 
            if not filtered:
                #print(f'unfiltered ({filtermode}):{combination}')

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
                    #print(f'first unfiltered ({filtermode}):{combination}')

                    break
            #print(f'{unfiltered = }')
# if combination hasnt been unfiltered, append to filtered_sub_list 
            if not unfiltered:
                #print(f'filtered ({filtermode}):{combination}')

                filtered_list.append(combination)

        else:
            #print(f'last unfiltered ({filtermode}):{combination}')

            unfiltered_list.append(combination)
    #print(len(filtered_list), len(unfiltered_list))

    return filtered_list, unfiltered_list

                                        
def chunked_gen(generator: Generator[tuple, None, None],
                chunksize: int) \
                                -> Generator[list[tuple], None, None]:
    """
    returns generator chunk wise as lists.
    """
    while True:
        chunk = []
        for i, data in enumerate(generator):
            chunk.append(data)
# chunksize - 1 because data needs to be appended before checking, otherwise
# always going to miss last item of chunk
            if i >= chunksize - 1:
                break
        yield chunk

def cartesian_product_filtered(alphabet: Iterable[Any],
                            dimensional_filterlist: Iterable[Iterable[Any]],
                            filtermode: str,
                            returnwhich: str = 'filtered',
                            max_duplicates: int = 0,
                            threshold: int = 1_000,
                            verbose: int = 0) \
                    -> list[tuple[Any]] | Generator[tuple, None, None]:
    """
    Function for brute forcing a cartesian product of all items in alphabet and
    filtering by maximum number of duplicated items within all items of the
    cartesian product specific filterlist.
    filterlist-lists. filterlist needs to be set with empty lists in dimensions
    which are not to be filtered to dictate dimensionality of combination
    correctly.

    alphabet: list of entries to permute.
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
    ALPHSIZE = len(alphabet) 
    DIMENSIONS = len(dimensional_filterlist)
    COMBINATIONS = ALPHSIZE ** DIMENSIONS
    filtered_list = []
    unfiltered_list = []
    # generator returning cartesian product
    cart_prod_gen = product(alphabet, repeat=DIMENSIONS)
    # number of processes to spawn for multiprocessing
    tospawn = cpu_count()

    # if no filter is given in ANY dimension, return all combinations
    empty_filter = True
    for f in dimensional_filterlist:
        if f != []:
            empty_filter = False
            break

    multi_factor = 1    # multi_factor for adjustment of chunksize chunksneeded
    THRESHOLD = threshold  # threshold for deciding if mulitiproc will be used
    count = 1           # counter for automatic chunk sizes
    # following code determines chunks size from threshold and cpu count
    # (tospawn). if threshold isnt reached, dont use multi processing
    multi_flag = False

    if COMBINATIONS > THRESHOLD:
        # init chunksize for while loop if threshold is reached
        CHUNKSIZE = COMBINATIONS
        multi_flag = True
    else:
        CHUNKSIZE = 0
    while CHUNKSIZE > THRESHOLD:
        CHUNKSNEEDED = tospawn * multi_factor * count
        CHUNKSIZE = int(ceil(COMBINATIONS // CHUNKSNEEDED) + 1)
        count += 1
    # size of last chunk will be smaller if COMBINATIONS % CHUNKSNEEDED != 0
    # LASTCHUNKSIZE value is needed for sanitychecking of result
    LASTCHUNKSIZE = CHUNKSIZE - (CHUNKSIZE * CHUNKSNEEDED - COMBINATIONS)

    if verbose > 0: # status print
        print(f'cartesian product filtered:\tmax possible combinations '
                f'{ALPHSIZE}^{DIMENSIONS} = {tf(COMBINATIONS)}\n'
                f'{filtermode = }\t{returnwhich = }\n')
        for i, filt in enumerate(dimensional_filterlist):
            print(f'dim: {i + 1}\t{filt}')
        if multi_flag:
            print(f'\nprocessing data using {CHUNKSNEEDED} chunks of size '
                    f'{tf(CHUNKSIZE)}. threshold: {tf(THRESHOLD)}')

    if not empty_filter:
        if not multi_flag:
            res = ndimensional_filter_lists(list(cart_prod_gen),
                                                dimensional_filterlist,
                                                max_duplicates,
                                                filtermode)
            filtered_list, unfiltered_list = res

        elif multi_flag:
            # init partial function to work with imap
            partial_filter = partial(ndimensional_filter_lists,
                                        filter=dimensional_filterlist,
                                        max_duplicates=max_duplicates,
                                        filtermode=filtermode)
            chunked_cart_prod_gen = chunked_gen(cart_prod_gen, CHUNKSIZE)
                
            with get_context('spawn').Pool(processes=tospawn) as pool:

                for i, res in enumerate(pool.imap(partial_filter,
                                        chunked_cart_prod_gen,
                                        chunksize=1)):
                    if i >= CHUNKSNEEDED:
                        break

                    if returnwhich == 'filtered':
                        filtered_list.extend(res[0])
                    elif returnwhich == 'unfiltered':
                        unfiltered_list.extend(res[1])
                    
                    if i < CHUNKSNEEDED:
                        if verbose > 1:
                            print(f'{i+1}:\t{len(res[0])}\t{len(res[1])}') 
                            print(f'{res[0][:2] = }\n{res[1][:2] = }\n') 
        # for last chunk set CHUNKSIZE to LASTCHUNKSIZE for sanity checking
                        if i == CHUNKSNEEDED - 1:
                            CHUNKSIZE = LASTCHUNKSIZE
                        nfiltered = len(res[0])
                        nunfiltered = len(res[1])
                        # sanity checking each return
                        if CHUNKSIZE != nfiltered + nunfiltered:
                            print(f'sanity check failed\t{CHUNKSIZE = }\t'
                                    f'{nfiltered = }\t{nunfiltered = }')
                            raise SanityCheckError

    # which list to return
    if returnwhich == 'filtered' and not empty_filter: 
        result = filtered_list
        nunfiltered = COMBINATIONS - len(filtered_list)
    elif returnwhich == 'unfiltered' and not empty_filter:
        result = unfiltered_list
        nfiltered = COMBINATIONS - len(unfiltered_list)
    elif returnwhich == 'filtered' and empty_filter:
        try:
            result = list(cart_prod_gen)
        except Exception as e:
            print(f'{e}\n returning generator instead of result list')
            result = cart_prod_gen
        nfiltered = COMBINATIONS
        nunfiltered = 0
    elif returnwhich == 'unfiltered' and empty_filter:
        result = []
        nfiltered = 0
        nunfiltered = COMBINATIONS

    if verbose > 0:
        print(f'filtered: {tf(nfiltered)}\nunfiltered: {tf(nunfiltered)}\n')

    return result

class SanityCheckError(Exception):
    pass

#@gu1.timerdecorator(4, 's')
def main():
    toprod = ['Paul', 'Basti', 'Merle', 'Kim', 'Jonas', 'Lennard']
    toprod = ['ying young', 'sheesh', 'skrrr skrrrt', 'therapiegalaxie', 'kraterkosmos', 'narkosehelikopter', 'hitler']
    toprod = [0,1,2,3,4,5,6,7,8,9]
    toprod = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    filter_list = [[0], [1], ['lol'], [(1, 2)], [], []]
    filter_list = [['ying young'], [], ['sheesh', 'skrrr skrrrt'], [],
                ['therapiegalaxie', 'kraterkosmos', 'narkosehelikopter'], []]
    filter_list = [[], [], [], [], [], []]
    filter_list = [[], [], [], []]
    filter_list = [[],[],[1,'A','B','C','D','E','F'],[0,1,2,'A','B','C','D','E','F']]
    filter_list = [[],[],[1,'A','B','C','D','E','F'],[0,1,2,'A','B','C','D','E','F'], [], [], []]
    filter_list = [[],[],[1,'A','B','C','D','E','F'],[0,1,2,'A','B','C','D','E','F'], [], []]
    
    cpf3 = cartesian_product_filtered(alphabet=toprod,
                                        dimensional_filterlist=filter_list,
                                        returnwhich='filtered',
                                        filtermode='strict',
                                        max_duplicates=0,
                                        threshold=400_000,
                                        verbose=2)
    print(f'\nafter cpf3\n')
# make hexcodes from tuples
    cpf3 = formatter.stringify(iterlist=cpf3, delimiter='')
    formed = formatter.formatter(toform=cpf3,
                                columns=32,
                                prefix=formatter.line_numbers(10))
    for f in formed[:10]:
        print(f'{f}')
        
    
    windesk = r'C:\Users\lvedd\Desktop'
    target = 'rwlinestesting'
    timestr = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
    timestr = timestr[:-3]
    fname = f'{timestr} cart prod list'

    write_to_file(tofile=formed,
                    fileextension='txt',
                    parentdir=windesk,
                    targetdir=target,
                    filename=fname,
                    overwrite='append',
                    verbose=2)
    

        
'''wanted behaviour filtering perm [1,2,3] with [[1],[1,2],[]]:
loosely:
    if dim 0 contains 1 OR dim 1 contains 1 or 2: filter combination
    else unfilter combination
strictly:
    if dim 0 contains 1 AND dim 1 contains 1 or 2: filter combination
    else unfilter combination
'''
    

if __name__ == '__main__':
    main()
    

