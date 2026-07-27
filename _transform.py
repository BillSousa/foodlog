# Author:
#         Bill Sousa
#
# License: BSD 3 clause
#



# from .._type_aliases import (
#     InstructionType,
#     InternalXContainer
# )
#
# import numpy as np
# import pandas as pd
# import polars as pl
# import scipy.sparse as ss



def _transform(
    _X: InternalXContainer,
    _instructions: InstructionType
) -> InternalXContainer:
    """Manage the constant columns in `X`.

    Apply the removal criteria given by `keep` via `_instructions` to
    the constant columns found during fit.

    Parameters
    ----------
    _X : InternalXContainer of shape (n_samples, n_features)
        The data to be transformed. Must be numpy ndarray, pandas
        dataframe, polars dataframe, or scipy sparse csc matrix/array.
    _instructions : InstructionType
        Instructions for keeping, deleting, or adding constant columns.

    Returns
    -------
    _X : InternalXContainer of shape (n_samples, n_transformed_features)
        The transformed data.

    """


    # validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *

    assert isinstance(
        _X,
        (np.ndarray, pd.DataFrame, pl.DataFrame, ss.csc_array,
         ss.csc_matrix)
    )
    assert isinstance(_instructions, dict)
    assert len(_instructions) == 3

    # END validation ** * ** * ** * ** * ** * ** * ** * ** * ** * ** *


    # class InstructionType(TypedDict):
    #
    #     keep: Required[None | list[int]]
    #     delete: Required[None | list[int]]
    #     add: Required[None | dict[str, Any]]

    # 'keep' isnt needed to modify X, it is only in the dictionary for
    # ease of making self.kept_columns_ later.


    # build the mask that will take out deleted columns
    KEEP_MASK = np.ones(_X.shape[1]).astype(bool)
    if _instructions['delete'] is not None:
        # if _instructions['delete'] is None numpy actually maps
        # assignment to all positions! so that means we must put this
        # statement under an if that only allows when not None
        KEEP_MASK[_instructions['delete']] = False

    # remove the columns
    if isinstance(_X, pd.DataFrame):
        _X = _X.iloc[:, KEEP_MASK]
    else:
        _X = _X[:, KEEP_MASK]


    # if :param: keep is dict, add the new intercept
    if _instructions['add']:

        _key = list(_instructions['add'].keys())[0]
        _value = _instructions['add'][_key]
        _new_column = np.full((_X.shape[0], 1), _value)
        try:
            float(_value)
            _dtype = {'pd': np.float64, 'pl': pl.Float64}
        except:
            _dtype = {'pd': object, 'pl': pl.Object}

        if isinstance(_X, np.ndarray):

            # this just rams the fill value into _X, and conforms to
            # whatever dtype _X is (with some caveats)
            # str dtypes are changing here. also on windows int dtypes
            # are changing to int64.
            _X = np.hstack((_X, _new_column))
            # there does not seem to be an obvious connection between
            # what the dtype of _value is and the resultant dtype (for
            # example, _X with dtype '<U10' when appending float(1.0),
            # the output dtype is '<U21' (???, maybe the floating points
            # on the float?) )

        elif isinstance(_X, pd.DataFrame):
            _X[_key] = _new_column.astype(_dtype['pd'])

        elif isinstance(_X, pl.DataFrame):
            if _dtype['pl'] == pl.Float64:
                # need to do this so that polars can cast the dtype. it
                # wont cast it on the numpy array
                _new_column = list(map(float, _new_column.ravel()))
            _X = _X.with_columns(
                pl.DataFrame({_key: _new_column}).cast(_dtype['pl'])
            )

        elif isinstance(_X, (ss.csc_matrix, ss.csc_array)):
            _X = ss.hstack((_X, type(_X)(_new_column)))


        del _key, _value, _new_column, _dtype


    return _X





