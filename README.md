Cartesian Power Filtered
========================

Makes cartesian power of any values and with a defined dimensionality with various options for filtering the resulting set. <br/>

A cartesian power is a form of a [cartesian product](https://en.wikipedia.org/wiki/Cartesian_product) where all sets (resp. alphabets, see next section) are the same. [Itertools 'product()'](https://docs.python.org/3/library/itertools.html#itertools.product) is working at the core of this implementation. <br/>

This can be a usefull tool to generate test data with a ***certain, concrete*** pattern and type. Probably also for brute forcing in some cases where the length of the combination is known and symbols are fixed in a known position of that combination as this might reduce complexity by a lot.

For a simple example, the 3-dimensional cartesian power of the set (0, 1) is the set of all binary numbers from 000 to 111 (if concatenated):
```
000 001 010 011
100 101 110 111
```

<br/>

Parameters and how to use
=======================

Filterlist needs to be set with empty lists in dimensions which are not to be filtered to dictate dimensionality of resulting combinations correctly. Returns generator of lists (with maxsize of threshold) of (un)filtered cartesian power.

- ```alphabet```: Sequence (resp. set) of entries to compute all possible ordered pairs of. Entries can be of any type.

- ```dimensional_filterlist```: n-dimensional list of lists of entries to filter out. len(filterlist) = number of dimensions, dictates dimensionality of resulting combinations. If inner list at dimension n is empty, dimension n will be ignored by filters: <br/>
Thus empty lists are needed at appropriate dimensions to set correct dimensionality of resulting tuples, if not all dimensions are to be filtered! <br/>
See examples below, where ```dimensional_filterlist[2] == []```.

- ```filtermode```: takes 'strict' or 'loose' as a string. if 'strict', combinations which strictly contain only items which are set in dimensional_filterlist will be filtered. if 'loose', combinations which contain at least one item which is set in dimensional_filterlist in a given dimension of all dimensions are filtered.

- ```max_duplicates```: if set to a number > 0, combinations which contain more than max_duplicates of the same item in a given combination will be filtered out. This is useful to set to reduce computation for huge datasets time as the check is applied before dimensional filtering.

- ```returnwhich```: takes 'filtered' or 'unfiltered' as a string. if 'filtered', only filtered combinations will be returned, otherwise unfiltered

- ```result_size```: determines chunksize of generated result-lists as well as the size of chunks for multiprocessing workers. If number of resulting combinations ( = ```len(alphabet) ** len(dimensioncal_filterlist)```) of cartesian product is bigger than result_size, multiprocessing will be used for filtering.

- ```verbose```: takes values from 0-2 inclusive


- ```return```: From ```Sequence[Any]``` returns ```Generator[list[tuple[Any]]]``` where ```tuple``` are the resulting combinations.
<br/> <br/>

Example usage and expected outputs
=================================

with ```alphabet = ['A', 'B', 'C']``` and ```dimensional_filterlist = [ ['A'], ['A', 'B'], [] ]```
 <br/> <br/>

- strict filter: ```cartesian_power_filtered(alphabet, dimensional_filterlist, filtermode = 'strict')``` <br/>
- note how in every tuple the first dimensions item is always ```'A'``` and the second dimensions items are either ```'A'``` or ```'B'```, while the third dimensions items are any from ```alphabet```.
omitting to show original output ```list[tuple]``` in following examples.

```
AAA AAB AAC
ABA ABB ABC
```

as :

```
[('A', 'A', 'A'), ('A', 'A', 'B'), ('A', 'A', 'C'),
 ('A', 'B', 'A'), ('A', 'B', 'B'), ('A', 'B', 'C')]
```
<br/><br/>


- loose filter: ```cartesian_power_filtered(alphabet, dimensional_filterlist, filtermode = 'loose')``` <br/>
- note how here in in comparison to strict filtering above, items in any dimension can in principle be any element from ```alphabet```, as long as in first dimension is an ```'A'``` or in second dimension is either an ```'A'``` or a ```'B'```, while the items in third dimension can be any from ```alphabet``` as above.

```
AAA AAB AAC ABA ABB ABC
ACA ACB ACC BAA BAB BAC
BBA BBB BBC CAA CAB CAC
CBA CBB CBC
```
 <br/><br/>


- loose filter, max_duplicates = 1: ```cartesian_power_filtered(alphabet, dimensional_filterlist, 'loose', max_duplicates = 1)``` <br/>
	 - this setting actually imitates functionality of ```itertools.permutations())``` <br/>
expected result:

```
ABC ACB BAC BCA CAB CBA
```
