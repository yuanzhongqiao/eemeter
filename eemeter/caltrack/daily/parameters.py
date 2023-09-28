#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

   Copyright 2014-2023 OpenEEmeter contributors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""
import numpy as np
from typing import Dict, Any
from pydantic import BaseModel
from enum import Enum


class ModelType(str, Enum):
    # Full model \_/
    HDD_TIDD_CDD_SMOOTH = "hdd_tidd_cdd_smooth"
    HDD_TIDD_CDD = "hdd_tidd_cdd"

    # Heating, temp independent \__
    HDD_TIDD_SMOOTH = "hdd_tidd_smooth"
    HDD_TIDD = "hdd_tidd"

    # Temp independent, cooling __/
    TIDD_CDD_SMOOTH = "tidd_cdd_smooth"
    TIDD_CDD = "tidd_cdd"

    # Temp independent, ___
    TIDD = "tidd"


class ModelCoefficients(BaseModel):
    """
    A class used to represent the coefficients of a model.

    Attributes
    ----------
    model_type : ModelType
        The type of the model.
    intercept : float
        The intercept of the model.
    hdd_bp : float | None
        The heating degree days breakpoint of the model, if applicable.
    hdd_beta : float | None
        The heating degree days beta of the model, if applicable.
    hdd_k : float | None
        The heating degree days k of the model, if applicable.
    cdd_bp : float | None
        The cooling degree days breakpoint of the model, if applicable.
    cdd_beta : float | None
        The cooling degree days beta of the model, if applicable.
    cdd_k : float | None
        The cooling degree days k of the model, if applicable.

    Methods
    -------
    from_np_arrays(coefficients, coefficient_ids)
        Constructs a ModelCoefficients object from numpy arrays of coefficients and their corresponding ids.
    to_np_array()
        Converts the ModelCoefficients object to a numpy array.
    """
    """
    A class used to represent the coefficients of a model.

    Attributes
    ----------
    model_type : ModelType
        The type of the model.
    intercept : float
        The intercept of the model.
    hdd_bp : float | None
        The heating degree days breakpoint of the model, if applicable.
    hdd_beta : float | None
        The heating degree days beta of the model, if applicable.
    hdd_k : float | None
        The heating degree days k of the model, if applicable.
    cdd_bp : float | None
        The cooling degree days breakpoint of the model, if applicable.
    cdd_beta : float | None
        The cooling degree days beta of the model, if applicable.
    cdd_k : float | None
        The cooling degree days k of the model, if applicable.

    Methods
    -------
    from_np_arrays(coefficients, coefficient_ids)
        Constructs a ModelCoefficients object from numpy arrays of coefficients and their corresponding ids.
    to_np_array()
        Converts the ModelCoefficients object to a numpy array.
    """
    
    model_type: ModelType
    intercept: float
    hdd_bp: float | None = None
    hdd_beta: float | None = None
    hdd_k: float | None = None
    cdd_bp: float | None = None
    cdd_beta: float | None = None
    cdd_k: float | None = None

    @property
    def is_smooth(self):
        return self.model_type in [
            ModelType.HDD_TIDD_CDD_SMOOTH,
            ModelType.HDD_TIDD_SMOOTH,
            ModelType.TIDD_CDD_SMOOTH,
        ]

    @property
    def model_key(self):
        """Used inside OptimizedResult when reducing model"""
        match self.model_type:
            case ModelType.HDD_TIDD_CDD_SMOOTH:
                return "hdd_tidd_cdd_smooth"
            case ModelType.HDD_TIDD_CDD:
                return "hdd_tidd_cdd"
            case ModelType.HDD_TIDD_SMOOTH | ModelType.TIDD_CDD_SMOOTH:
                return "c_hdd_tidd_smooth"
            case ModelType.HDD_TIDD | ModelType.TIDD_CDD:
                return "c_hdd_tidd"
            case ModelType.TIDD:
                return "tidd"

    @classmethod
    def from_np_arrays(cls, coefficients, coefficient_ids):
        """
        This class method creates a ModelCoefficients instance from numpy arrays of coefficients and their corresponding ids.

        Args:
            cls (class): The class to which this class method belongs.
            coefficients (np.array): A numpy array of coefficients.
            coefficient_ids (list): A list of coefficient ids.

        Returns:
            ModelCoefficients: An instance of ModelCoefficients class.

        Raises:
            ValueError: If the coefficient_ids do not match any of the expected patterns.

        The method matches the coefficient_ids to predefined patterns and based on the match, 
        it initializes a ModelCoefficients instance with the corresponding model_type and coefficients. 
        If the coefficient_ids do not match any of the predefined patterns, it raises a ValueError.
        """

        match coefficient_ids:
            case [
                "hdd_bp",
                "hdd_beta",
                "hdd_k",
                "cdd_bp",
                "cdd_beta",
                "cdd_k",
                "intercept",
            ]:
                hdd_bp=coefficients[0]
                hdd_beta=coefficients[1]
                hdd_k=coefficients[2]
                cdd_bp=coefficients[3]
                cdd_beta=coefficients[4]
                cdd_k=coefficients[5]
                if cdd_bp < hdd_bp:
                    hdd_bp, cdd_bp = cdd_bp, hdd_bp
                    hdd_beta, cdd_beta = cdd_beta, hdd_beta
                    hdd_k, cdd_k = cdd_k, hdd_k
                return ModelCoefficients(
                    model_type=ModelType.HDD_TIDD_CDD_SMOOTH,
                    hdd_bp=hdd_bp,
                    hdd_beta=hdd_beta,
                    hdd_k=hdd_k,
                    cdd_bp=cdd_bp,
                    cdd_beta=cdd_bp,
                    cdd_k=cdd_bp,
                    intercept=coefficients[6],
                )
            case [
                "hdd_bp",
                "hdd_beta",
                "cdd_bp",
                "cdd_beta",
                "intercept",
            ]:
                hdd_bp=coefficients[0]
                hdd_beta=coefficients[1]
                cdd_bp=coefficients[2]
                cdd_beta=coefficients[3]
                if cdd_bp < hdd_bp:
                    hdd_bp, cdd_bp = cdd_bp, hdd_bp
                    hdd_beta, cdd_beta = cdd_beta, hdd_beta
                return ModelCoefficients(
                    model_type=ModelType.HDD_TIDD_CDD,
                    hdd_bp=hdd_bp,
                    hdd_beta=hdd_beta,
                    cdd_bp=cdd_bp,
                    cdd_beta=cdd_beta,
                    intercept=coefficients[4],
                )
            case [
                "c_hdd_bp",
                "c_hdd_beta",
                "c_hdd_k",
                "intercept",
            ]:
                if coefficients[1] < 0:  # model is heating dependent
                    hdd_bp = coefficients[0]
                    hdd_beta = coefficients[1]
                    hdd_k = coefficients[2]
                    cdd_bp = cdd_beta = cdd_k = None
                    model_type = ModelType.HDD_TIDD_SMOOTH
                else:  # model is cooling dependent
                    cdd_bp = coefficients[0]
                    cdd_beta = coefficients[1]
                    cdd_k = coefficients[2]
                    hdd_bp = hdd_beta = hdd_k = None
                    model_type = ModelType.TIDD_CDD_SMOOTH
                return ModelCoefficients(
                    model_type=model_type,
                    hdd_bp=hdd_bp,
                    hdd_beta=hdd_beta,
                    hdd_k=hdd_k,
                    cdd_bp=cdd_bp,
                    cdd_beta=cdd_beta,
                    cdd_k=cdd_k,
                    intercept=coefficients[3],
                )
            case [
                "c_hdd_bp",
                "c_hdd_beta",
                "intercept",
            ]:
                if coefficients[1] < 0:  # model is heating dependent
                    hdd_bp = coefficients[0]
                    hdd_beta = coefficients[1]
                    cdd_bp = cdd_beta = None
                    model_type = ModelType.HDD_TIDD
                else:  # model is cooling dependent
                    cdd_bp = coefficients[0]
                    cdd_beta = coefficients[1]
                    hdd_bp = hdd_beta = None
                    model_type = ModelType.TIDD_CDD
                return ModelCoefficients(
                    model_type=model_type,
                    hdd_bp=hdd_bp,
                    hdd_beta=hdd_beta,
                    cdd_bp=cdd_bp,
                    cdd_beta=cdd_beta,
                    intercept=coefficients[2],
                )
            case [
                "intercept",
            ]:
                return ModelCoefficients(
                    model_type=ModelType.TIDD,
                    intercept=coefficients[0],
                )
            case _:
                raise ValueError

    def to_np_array(self):
        """
        This method converts the model parameters into a numpy array based on the model type.

        The model type determines which parameters are included in the array. The parameters are:
        - hdd_bp: The base point for heating degree days (HDD)
        - hdd_beta: The beta coefficient for HDD
        - hdd_k: The smoothing parameter for HDD
        - cdd_bp: The base point for cooling degree days (CDD)
        - cdd_beta: The beta coefficient for CDD
        - cdd_k: The smoothing parameter for CDD
        - intercept: The model's intercept

        Returns:
            np.array: A numpy array containing the relevant parameters for the model type.
        """

        match self.model_type:
            case ModelType.HDD_TIDD_CDD_SMOOTH:
                return np.array(
                    [
                        self.hdd_bp,
                        self.hdd_beta,
                        self.hdd_k,
                        self.cdd_bp,
                        self.cdd_beta,
                        self.cdd_k,
                        self.intercept,
                    ]
                )
            case ModelType.HDD_TIDD_CDD:
                return np.array(
                    [
                        self.hdd_bp,
                        self.hdd_beta,
                        self.cdd_bp,
                        self.cdd_beta,
                        self.intercept,
                    ]
                )
            case ModelType.HDD_TIDD_SMOOTH:
                return np.array(
                    [self.hdd_bp, self.hdd_beta, self.hdd_k, self.intercept]
                )
            case ModelType.TIDD_CDD_SMOOTH:
                return np.array(
                    [self.cdd_bp, self.cdd_beta, self.cdd_k, self.intercept]
                )
            case ModelType.HDD_TIDD:
                return np.array([self.hdd_bp, self.hdd_beta, self.intercept])
            case ModelType.TIDD_CDD:
                return np.array([self.cdd_bp, self.cdd_beta, self.intercept])
            case ModelType.TIDD:
                return np.array([self.intercept])


class DailySubmodelParameters(BaseModel):
    coefficients: ModelCoefficients
    temperature_constraints: Dict[str, float]
    f_unc: float
    CVRMSE: float

    @property
    def model_type(self):
        return self.coefficients.model_type


class DailyModelParameters(BaseModel):
    settings: Dict[str, Any]
    metrics: Dict[str, Any]
    submodels: Dict[str, DailySubmodelParameters]
