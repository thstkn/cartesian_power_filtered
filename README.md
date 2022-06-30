# Cartesian Power Filtered
Makes cartesian product of any values of given dimensionality with various options for filtering the result.

- This is a usefull tool to generate test data with a **_certain, concrete_** pattern.

# Parameters and how to use
Function for computing a cartesian power of all items in alphabet and filtering by maximum number of duplicated items within all items of the cartesian power specific filterlist. filterlist needs to be set with empty lists in dimensions which are not to be filtered to dictate dimensionality of combination correctly. Returns generator of lists of (un)filtered cartesian power with maxsize of threshold

- ```alphabet```: Sequence of entries to permute. Entries can be of any type.

- ```dimensional_filterlist```: n-dimensional list of lists of entries to filter out. len(filterlist) = number of dimensions, dictates dimensionality of resulting combinations. If inner list at dimension n is empty, dimension n will be ignored by filters: <br/>
Thus empty lists are needed at appropriate dimensions to set correct dimensionality of resulting tuples, if not all dimensions are to be filtered! <br/>
See examples below, where ```dimensional_filterlist[2] == []```.

- ```filtermode```: takes 'strict' or 'loose' as a string. if 'strict', combinations which strictly contain only items which are set in dimensional_filterlist will be filtered. if 'loose', combinations which contain at least one item which is set in dimensional_filterlist in a given dimension of all dimensions are filtered.

- ```max_duplicates```: if set to a number > 0, combinations which contain more than max_duplicates of the same item in a given combination will be filtered out. This is useful to set to reduce computation for huge datasets time as the check is applied before dimensional filtering.

- ```returnwhich```: takes 'filtered' or 'unfiltered' as a string. if 'filtered', only filtered combinations will be returned, otherwise unfiltered

- ```result_size```: determines chunksize of generated result-lists as well as the size of chunks for multiprocessing workers. If number of resulting combinations ( = ```len(alphabet) ** len(dimensioncal_filterlist)```) of cartesian product is bigger than result_size, multiprocessing will be used for filtering.

- ```verbose```: takes values from 0-2 inclusive


- ```return```: From ```Sequence[Any]``` returns ```Generator[list[tuple[Any]]]``` (Generator[list[combinations[Any]]])

# Example usage and expected outputs
with ```alphabet = ['A', 'B', 'C']``` and ```dimensional_filterlist = [ ['A'], ['A', 'B'], [] ]```
 <br/> <br/>

 - strict filter: ```cartesian_power_filtered(alphabet, dimensional_filterlist, filtermode = 'strict')```
expected result:

```
AAA AAB AAC ABA ABB ABC
```

as (omitted showing original output 'list[tuple[Any]]' in following examples):

```
[('A', 'A', 'A'), ('A', 'A', 'B'), ('A', 'A', 'C'), ('A', 'B', 'A'), ('A', 'B', 'B'), ('A', 'B', 'C')]
```
<br/>


- loose filter: ```cartesian_power_filtered(alphabet, dimensional_filterlist, filtermode = 'loose')```
expected result:

```
AAA AAB AAC ABA ABB ABC
ACA ACB ACC BAA BAB BAC
BBA BBB BBC BCA BCB BCC
CAA CAB CAC CBA CBB CBC
CCA CCB CCC
```
 <br/>


- loose filter, max_duplicates = 1: ```cartesian_power_filtered(alphabet, dimensional_filterlist, 'loose', max_duplicates = 1)```
this setting actually imitates functionality of ```itertools.permutations())``` <br/>
expected result:

```
ABC ACB BAC BCA CAB CBA
```
