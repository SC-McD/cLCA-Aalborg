# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Using pymrio without a parser (small IO example)

# Pymrio provides parsing function to load existing MRIO databases. However, it is also possible to assign data directly to the attributes of an IOSystem instance.
#
# This tutorial exemplify this functionality. The tables used here are taken from *Miller and Blair (2009)*: Miller, Ronald E, and Peter D Blair. Input-Output Analysis: Foundations and Extensions. Cambridge (England); New York: Cambridge University Press, 2009. ISBN: 978-0-521-51713-3
#

# ## Preperation

# ### Import pymrio

# First import the pymrio module and other packages needed:

# +
import pymrio

import pandas as pd
import numpy as np
# -

# ### Get external IO table

# For this example we use the IO table given in *Miller and Blair (2009)*: Table 2.3 (on page 22 in the 2009 edition).

# This table contains an interindustry trade flow matrix, final demand columns for household demand and exports and a value added row. The latter we consider as an extensions (factor inputs). To assign these values to the IOSystem attributes, the tables must be pandas
# <a href="http://pandas.pydata.org/pandas-docs/dev/dsintro.html#dataframe">DataFrames</a> with <a href="http://pandas.pydata.org/pandas-docs/dev/indexing.html#hierarchical-indexing-multiindex">multiindex</a> for columns and index.

# First we set up the Z matrix by defining the index of rows and columns. The example IO tables contains only domestic tables, but since pymrio was designed with multi regions IO tables in mind, also a region index is needed.

_sectors = ['sector1', 'sector2']
_regions = ['reg1']
_Z_multiindex = pd.MultiIndex.from_product(
                [_regions, _sectors], names = [u'region', u'sector'])

# Next we setup the total Z matrix. Here we just put in the name the values manually. However, pandas provides several possibility to ease the <a href="http://pandas.pydata.org/pandas-docs/stable/io.html">data input</a>.

Z = pd.DataFrame(
    data = np.array([
            [150,500],
            [200,100]]),
    index = _Z_multiindex,
    columns = _Z_multiindex
    )

Z

# Final demand is treated in the same way:

_categories = ['final demand']
_fd_multiindex = pd.MultiIndex.from_product(
                 [_regions, _categories], names = [u'region', u'category'])

Y = pd.DataFrame(
    data=np.array([[350], [1700]]),
    index = _Z_multiindex,
    columns = _fd_multiindex)


Y

# Factor inputs are given as 'Payment sectors' in the table:

F = pd.DataFrame(
    data = np.array([[650, 1400]]),
    index = ['Payments_sectors'],
    columns = _Z_multiindex)


F

# ## Include tables in the IOSystem object

# In the next step, an empty instance of an IOSYstem has to be set up.

io = pymrio.IOSystem()

# Now we can add the tables to the IOSystem instance:

io.Z = Z
io.Y = Y

# Extension are defined as objects within the IOSystem. The Extension instance can be instanced independently (the parameter 'name' is required):

factor_input = pymrio.Extension(name = 'Factor Input', F=F)

io.factor_input = factor_input

# For consistency and plotting we can add a DataFrame containg the units per row:

io.factor_input.unit = pd.DataFrame(data = ['USD'], index = F.index, columns = ['unit'])

# We can check whats in the system:

str(io)

# At this point we have everything to calculate the full IO system.

# ## Calculate the missing parts

io.calc_all()

# This gives, among others, the A and L matrix which we can compare with the tables given in *Miller and Blair (2009)* (Table 2.4 and L given on the next page afterwards):

io.A

io.L

# ## Update to system for a new final demand

# The example in *Miller and Blair (2009)* goes on with using the L matrix to calculate the new industry output x for a changing finald demand Y. This step can easly reproduced with the pymrio module.
#
# To do so we first have to set up the new final demand:

Ynew = Y.copy()
Ynew[('reg1','final_demand')] = np.array([[600],
                                          [1500]])

# We copy the original IOSystem:

io_new_fd = io.copy()

# To calculate for the new final demand we have to remove everything from the system except for the coefficients (A,L,S,M)

io_new_fd.reset_all_to_coefficients()

# Now we can assign the new final demand and recalculate the system:

io_new_fd.Y = Ynew

io_new_fd.calc_all()

# The new x equalls the xnew values given in *Miller and Blair (2009)* at formula 2.13:

io_new_fd.x

# As for all IO System, we can have a look at the modification history:

io_new_fd.meta
