#%%

##########################################
if __name__ == '__main__':
    import sys
    sys.path.append('..')
    from _usable_util.formatting import formatter
    from _usable_util.read_write_files import write_to_file
    from _usable_util.formatting.thousands_formatter \
            import thousands_formatter as tf
########################################
    
from datetime import datetime
from itertools import product
from math import ceil
# for type annotations:
from typing import Any, Generator, Iterable, Literal
# superclasses for subclassing by user
from collections.abc import Sequence
from functools import partial
from multiprocessing import cpu_count, get_context


def ndimensional_filter(combination: Sequence[Any],
                        filter: Sequence[Sequence[Any]], 
                        max_duplicates: int,
                        filtermode: str) \
                        -> bool:
    """Returns True if the combination is accepted by filter, otherwise false.
    """
    if max_duplicates > 0:
        # returns true if no item has been found more than max_dup times in c
        if not all(combination.count(item) <= max_duplicates for
                                       item in combination):
            return False
    if filtermode == 'loose':
        # return TRUE if any combination[dimension] is in filter[dimension]
        # while dim_filter is not empty
        return any(combination[dim] in dim_filter
                                    if dim_filter else True
                                    for dim, dim_filter in enumerate(filter))
    if filtermode == 'strict':
        # return FALSE if combination[item] is not in filter[dimension]
        return all(combination[dim] in dim_filter
                                    if dim_filter else True
                                    for dim, dim_filter in enumerate(filter))
                                        
def filter_worker(chunk: Sequence[Sequence[Any]],
                  filter: Sequence[Sequence[Any]],
                  max_duplicates: int,
                  filtermode: str) \
                                                -> list[Any]:
    """ Returns a filtered list of combinations.
    """
    return [combination for combination in chunk 
                                    if ndimensional_filter(combination,
                                                            filter,
                                                            max_duplicates,
                                                            filtermode)]

def chunked_gen(iterable: Iterable,
                chunksize: int) \
                                -> Generator[list[Any], None, None]:
    """ generator to yield other iterable chunk wise as lists. needed for 
        multiprocessing. Will it though?
    """
    yield from [list(iterable) for _ in range(chunksize)]

def cartesian_power_filtered(alphabet: Sequence[Any], 
                               dimensional_filterlist: list[list[Any]],
                               filtermode: Literal['loose', 'strict'],
                               returnwhich: Literal['filtered', 'unfiltered'] \
                                                                = 'filtered',
                               max_duplicates: int = 0,
                               threshold: int = 1_000,
                               verbose: int = 0) \
                                            -> Generator[list[Any], None, None]:
    """ Function for brute forcing a cartesian power of all items in alphabet
    and filtering by maximum number of duplicated items within all items of the
    cartesian power specific filterlist.
    filterlist needs to be set with empty lists in dimensions which are not to 
    be filtered to dictate dimensionality of combination correctly.
        Returns generator of lists of (un)filtered cartesian power with
    maxsize of threshold    

    * alphabet: Sequence of entries to permute.
    * dimensional_filterlist: n-dimensional list of lists of entries to filter
        out. len(filterlist) = number of dimensions, dictates dimensionality of 
        combination. if inner lists are empty, no filtering will take place in 
        that dimension. 
    * returnwhich: takes 'filtered' or 'unfiltered' as a string. if 'filtered',
        only filtered combinations will be returned, otherwise unfiltered 
    * filtermode: takes 'strict' or 'loose' as a string. if 'strict',
        combinations which strictly contain only items which are set in
        dimensional_filterlist will be filtered. if 'loose', combinations which
        contain at least one item which is set in dimensional_filterlist in a
        given dimension of all dimensions are filtered.
    * max_duplicates: if set to a number > 0, combinations which contain more
        than max_duplicates of the same item in a given combination will be
        filtered out. This is useful to set to reduce computation time.
    * threshold: determines chunksize of generated lists
    * verbose: takes values from 0-2 inclusively
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
    # set empty filter flag to True if ALL filterlists are empty
    empty_filter = all(dim_fil == [] for dim_fil in dimensional_filterlist)
    # number of processes to spawn for multiprocessing
    tospawn = cpu_count()
    multi_factor = 1    # multi_factor for adjustment of chunksize chunksneeded
    count = 1           # counter for automatic chunk sizes
    # following code determines chunks size from threshold and cpu count
    # (tospawn). if threshold isnt reached, dont use multi processing
    chunksize = COMBINATIONS
    chunksneeded = 0
    while chunksize > threshold:
        chunksneeded = tospawn * multi_factor * count
        chunksize = int(ceil(COMBINATIONS // chunksneeded) + 1)
        count += 1

    if verbose > 0: # status print
        print(f'cartesian power filtered:\tmax possible combinations '
                f'{ALPHSIZE}^{DIMENSIONS} = {tf(COMBINATIONS)}\n'
                f'{filtermode = }\t{returnwhich = }\n')
        for i, filt in enumerate(dimensional_filterlist):
            print(f'dim: {i + 1}\t{filt}')
        if chunksneeded > 0:
            print(f'\nprocessing data using {chunksneeded} chunks of size '
                    f'{tf(chunksize)}. threshold: {tf(threshold)}')

    # generator returning cartesian power
    cart_prod_gen = product(alphabet, repeat=DIMENSIONS)

    if returnwhich == 'unfiltered' and empty_filter:
        yield []

    if chunksneeded == 0:
        # quickest route if no multiprocessing and no filters
        if returnwhich == 'filtered' and empty_filter:
            yield list(cart_prod_gen)
        # no multiprocessing, but filters
        elif returnwhich == 'filtered':
            yield [comb for comb in cart_prod_gen if 
                                            ndimensional_filter(comb,
                                            dimensional_filterlist,
                                            max_duplicates,
                                            filtermode)]
        elif returnwhich == 'unfiltered':
            yield [comb for comb in cart_prod_gen if not
                                            ndimensional_filter(comb,
                                            dimensional_filterlist,
                                            max_duplicates,
                                            filtermode)]
    elif chunksneeded > 0:
        chunked_cart_prod_gen = chunked_gen(cart_prod_gen, chunksize)
        # quickest route if multiprocessing and no filters. this true?
        if returnwhich == 'filtered' and empty_filter:
            yield from chunked_cart_prod_gen
        # init partial function to work with imap
        mp_filter_worker = partial(filter_worker,
                                    filter=dimensional_filterlist,
                                    max_duplicates=max_duplicates,
                                    filtermode=filtermode)
        # oh wow! how to this???
        with get_context('spawn').Pool(processes=tospawn) as pool:
            # multiprocessing and filters
            yield from pool.imap(mp_filter_worker, chunked_cart_prod_gen)

def main():
    toprod = ['ying young', 'sheesh', 'skrrr skrrrt', 'therapiegalaxie', 'kraterkosmos', 'narkosehelikopter', 'hitler']
    toprod = [0,1,2,3,4,5,6,7,8,9]
    toprod = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'D', 'E', 'F']
    filter_list = [[0], [1], ['lol'], [(1, 2)], [], []]
    filter_list = [['ying young'], [], ['sheesh', 'skrrr skrrrt'], [],
                ['therapiegalaxie', 'kraterkosmos', 'narkosehelikopter'], []]
    filter_list = [[],[],[1,'A','B','C','D','E','F'],[0,1,2,'A','B','C','D','E','F'], [], [], []]
    filter_list = [[],[],[1,'A','B','C','D','E','F'],[0,1,2,'A','B','C','D','E','F'], [], []]
    filter_list = [[], [], [], [], [], []]
    filter_list = [[], [], [], []]
    filter_list = [['A','B','C','D','E','F'],['A','B','C','D','E','F'],['A','B','C','D','E','F']]
    
    cpf3 = cartesian_power_filtered(alphabet=toprod,
                                        dimensional_filterlist=filter_list,
                                        returnwhich='filtered',
                                        filtermode='loose',
                                        max_duplicates=1,
                                        threshold=400_000,
                                        verbose=2)
    # make hexcodes from tuples
    cpf3 = [chunk for chunk in cpf3]
    cpf3 = cpf3[0]

    cpf3 = formatter.stringify(iterabl=cpf3, delimiter='')
    print()
    formed = formatter.formatter(toform=cpf3,
                                columns=16,
                                prefix=formatter.line_numbers(10))
    for f in formed:
        print(f'{f}')
    return
    
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
        
''' behaviour filtering perm [1,2,3] with [[1],[1,2],[]]:
loosely:
    if dim 0 contains 1 OR dim 1 contains 1 or 2: filter combination
    else: unfilter combination
strictly:
    if dim 0 contains 1 AND dim 1 contains 1 or 2: filter combination
    else: unfilter combination
'''

if __name__ == '__main__':
    main()
    

