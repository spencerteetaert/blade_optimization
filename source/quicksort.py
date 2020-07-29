"""
Created on Sun Mar 10 18:09:35 2019

@note: Exchanging sort - Bubble Sort algorithm
@source: http://interactivepython.org/courselib/static/pythonds/SortSearch/TheQuickSort.html

Altered to support sorting of two lists in parallel (to keep matching x/y pairs)

"""

def quickSort(alist, sisterlist):
   print("\tSorting data...")
   quickSortHelper(alist,sisterlist,0,len(alist)-1)
   print("\tData sorted.")

def quickSortHelper(alist,sisterlist,first,last):
   if first<last:
       splitpoint = partition(alist,sisterlist,first,last)

       quickSortHelper(alist, sisterlist,first,splitpoint-1)
       quickSortHelper(alist, sisterlist,splitpoint+1,last)


def partition(alist,sisterlist,first,last):
   pivotvalue = alist[first]

   leftmark = first+1
   rightmark = last

   done = False
   while not done:

       while leftmark <= rightmark and alist[leftmark] <= pivotvalue:
           leftmark = leftmark + 1

       while alist[rightmark] >= pivotvalue and rightmark >= leftmark:
           rightmark = rightmark -1

       if rightmark < leftmark:
           done = True
       else:
           temp = alist[leftmark]
           alist[leftmark] = alist[rightmark]
           alist[rightmark] = temp

           temp = sisterlist[leftmark]
           sisterlist[leftmark] = sisterlist[rightmark]
           sisterlist[rightmark] = temp

   temp = alist[first]
   alist[first] = alist[rightmark]
   alist[rightmark] = temp

   temp = sisterlist[first]
   sisterlist[first] = sisterlist[rightmark]
   sisterlist[rightmark] = temp

   return rightmark