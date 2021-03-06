# smood

**s**imple **m**apping **o**f **o**ccurrence **d**ata: a package for making species distribution maps with Maxent.

## Feature requests?

`smood` is in its earliest stages right now and therefore is very simple. While simplicity is one of my goals, I also want the package to be *flexible* enough to be useful for a bunch of types of projects. Please don't hesitate to raise an issue on Github if there's something else you want `smood` to do!

## Maxent

[Maxent](https://biodiversityinformatics.amnh.org/open_source/maxent/) is a java application that models the suitability of grid cells in a landscape using observational data (in our case, from [GBIF](https://www.gbif.org/)) and environmental background layers (in our case, from [WorldClim](https://www.worldclim.org/)).

+ Steven J. Phillips, Miroslav Dud�k, Robert E. Schapire. [Internet] Maxent software for modeling species niches and distributions (Version 3.4.1). Available from url: http://biodiversityinformatics.amnh.org/open_source/maxent/. Accessed on 2019-11-25.

## Installation

`git clone https://github.com/pmckenz1/smood.git`  
`pip install smood`

## Demonstration

### We just have to provide 1) a species name and 2) lat/lon coordinates for a bounding box. `smood` then automatically collects gbif observations and pushes them through maxent to make fun maps.


```python
import smood
```

### we can define our species and boundary right away:


```python
# define our object
mapobj = smood.Mapper(sp_name = "Monarda fistulosa",
                      lat_range=[19.0,52.0],
                      lon_range=[-125.0,-68.0])
```




### now we can use a simple `run()` function to make things go:

The `run()` function calls gbif to find all observations of the species within the bounding box, and then it runs maxent using these observations and the designated worldclim layers.

Although this writes to disk, everything that is written is then cleaned up unless you ask for it to stay with `write_outputs=True`.


```python
mapobj.run()
```

## results

### raw png output from maxent (including occurrence data and the prediction densities)


```python
mapobj.maxent_image
```




![png](imgfiles/output_21_0.png)



### we can look at the occurrence data by itself


```python
# list of longitudes
mapobj.lons
```




```python
# list of latitudes
mapobj.lats
```


### we can also work directly with the density matrix


```python
smood.plot_density(density_mat=mapobj.density_mat)
```


![png](imgfiles/output_26_0.png)


### if we want, we can set a threshold on this matrix over which everything is considered "filled" and under which everything is considered "empty"

#### start with a high threshold:


```python
smood.plot_threshold(density_mat=mapobj.density_mat, 
                     threshold=.8)
```


![png](imgfiles/output_29_0.png)


#### now try with a lower threshold:


```python
smood.plot_threshold(density_mat=mapobj.density_mat,
                     threshold=.5)
```


![png](imgfiles/output_31_0.png)

