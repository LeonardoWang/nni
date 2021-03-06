# Search Space

## Overview

In NNI, tuner will sample parameters/architecture according to the search space, which is defined as a json file.

To define a search space, users should define the name of variable, the type of sampling strategy and its parameters.

* An example of search space definition as follow:

```yaml
{
    "dropout_rate": {"_type": "uniform", "_value": [0.1, 0.5]},
    "conv_size": {"_type": "choice", "_value": [2, 3, 5, 7]},
    "hidden_size": {"_type": "choice", "_value": [124, 512, 1024]},
    "batch_size": {"_type": "choice", "_value": [50, 250, 500]},
    "learning_rate": {"_type": "uniform", "_value": [0.0001, 0.1]}
}

```

Take the first line as an example. `dropout_rate` is defined as a variable whose priori distribution is a uniform distribution of a range from `0.1` and `0.5`.

## Types

All types of sampling strategies and their parameter are listed here:

* `{"_type": "choice", "_value": options}`

  * Which means the variable's value is one of the options. Here 'options' should be a list. Each element of options is a number of string. It could also be a nested sub-search-space, this sub-search-space takes effect only when the corresponding element is chosen. The variables in this sub-search-space could be seen as conditional variables.

  * An simple [example](https://github.com/microsoft/nni/tree/master/examples/trials/mnist-nested-search-space/search_space.json) of [nested] search space definition. If an element in the options list is a dict, it is a sub-search-space, and for our built-in tuners you have to add a key `_name` in this dict, which helps you to identify which element is chosen. Accordingly, here is a [sample](https://github.com/microsoft/nni/tree/master/examples/trials/mnist-nested-search-space/sample.json) which users can get from nni with nested search space definition. Tuners which support nested search space is as follows:

    - Random Search 
    - TPE
    - Anneal
    - Evolution

* `{"_type": "randint", "_value": [lower, upper]}`
  * Choosing a random integer from `lower` (inclusive) to `upper` (exclusive).
  * Note: Different tuners may interpret `randint` differently. Some (e.g., TPE, GridSearch) treat integers from lower 
    to upper as unordered ones, while others respect the ordering (e.g., SMAC). If you want all the tuners to respect 
    the ordering, please use `quniform` with `q=1`.

* `{"_type": "uniform", "_value": [low, high]}`
  * Which means the variable value is a value uniformly between low and high.
  * When optimizing, this variable is constrained to a two-sided interval.

* `{"_type": "quniform", "_value": [low, high, q]}`
  * Which means the variable value is a value like `clip(round(uniform(low, high) / q) * q, low, high)`, where the clip operation is used to constraint the generated value in the bound. For example, for `_value` specified as [0, 10, 2.5], possible values are [0, 2.5, 5.0, 7.5, 10.0]; For `_value` specified as [2, 10, 5], possible values are [2, 5, 10].
  * Suitable for a discrete value with respect to which the objective is still somewhat "smooth", but which should be bounded both above and below. If you want to uniformly choose integer from a range [low, high], you can write `_value` like this: `[low, high, 1]`.

* `{"_type": "loguniform", "_value": [low, high]}`
  * Which means the variable value is a value drawn from a range [low, high] according to a loguniform distribution like exp(uniform(log(low), log(high))), so that the logarithm of the return value is uniformly distributed.
  * When optimizing, this variable is constrained to be positive.

* `{"_type": "qloguniform", "_value": [low, high, q]}`
  * Which means the variable value is a value like `clip(round(loguniform(low, high) / q) * q, low, high)`, where the clip operation is used to constraint the generated value in the bound.
  * Suitable for a discrete variable with respect to which the objective is "smooth" and gets smoother with the size of the value, but which should be bounded both above and below.

* `{"_type": "normal", "_value": [mu, sigma]}`
  * Which means the variable value is a real value that's normally-distributed with mean mu and standard deviation sigma. When optimizing, this is an unconstrained variable.

* `{"_type": "qnormal", "_value": [mu, sigma, q]}`
  * Which means the variable value is a value like `round(normal(mu, sigma) / q) * q`
  * Suitable for a discrete variable that probably takes a value around mu, but is fundamentally unbounded.

* `{"_type": "lognormal", "_value": [mu, sigma]}`
  * Which means the variable value is a value drawn according to `exp(normal(mu, sigma))` so that the logarithm of the return value is normally distributed. When optimizing, this variable is constrained to be positive.

* `{"_type": "qlognormal", "_value": [mu, sigma, q]}`
  * Which means the variable value is a value like `round(exp(normal(mu, sigma)) / q) * q`
  * Suitable for a discrete variable with respect to which the objective is smooth and gets smoother with the size of the variable, which is bounded from one side.

* `{"_type": "mutable_layer", "_value": {mutable_layer_infomation}}`
  * Type for [Neural Architecture Search Space][1]. Value is also a dictionary, which contains key-value pairs representing respectively name and search space of each mutable_layer.
  * For now, users can only use this type of search space with annotation, which means that there is no need to define a json file for search space since it will be automatically generated according to the annotation in trial code.
  * For detailed usage, please refer to [General NAS Interfaces][1].

## Search Space Types Supported by Each Tuner

|                   | choice  | randint | uniform | quniform | loguniform | qloguniform | normal  | qnormal | lognormal | qlognormal |
|:------:|:------:|:------:|:------:|:------:|:------:|:------:|:------:|:------:|:------:|:------:|
| TPE Tuner         | &#10003; | &#10003; | &#10003; | &#10003;  | &#10003;    | &#10003;     | &#10003; | &#10003; | &#10003;   | &#10003;    |
| Random Search Tuner| &#10003; | &#10003; | &#10003; | &#10003;  | &#10003;    | &#10003;     | &#10003; | &#10003; | &#10003;   | &#10003;    |
| Anneal Tuner   | &#10003; | &#10003; | &#10003; | &#10003;  | &#10003;    | &#10003;     | &#10003; | &#10003; | &#10003;   | &#10003;    |
| Evolution Tuner   | &#10003; | &#10003; | &#10003; | &#10003;  | &#10003;    | &#10003;     | &#10003; | &#10003; | &#10003;   | &#10003;    |
| SMAC Tuner        | &#10003; | &#10003; | &#10003; | &#10003;  | &#10003;    |      |  |  |    |     |
| Batch Tuner       | &#10003; |  |  |   |     |      |  |  |    |     |
| Grid Search Tuner | &#10003; | &#10003; |  | &#10003;  |     | |  |  |    |     |
| Hyperband Advisor | &#10003; | &#10003; | &#10003; | &#10003;  | &#10003;    | &#10003;     | &#10003; | &#10003; | &#10003;   | &#10003;    |
| Metis Tuner   | &#10003; | &#10003; | &#10003; | &#10003;  |     |      |  |  |    |     |
| GP Tuner   | &#10003; | &#10003; | &#10003; | &#10003; | &#10003; | &#10003; |  |  |    |     |


Known Limitations:

* Note that Metis Tuner only supports numerical `choice` now

* Note that for nested search space:

    * Only Random Search/TPE/Anneal/Evolution tuner supports nested search space

    * We do not support nested search space "Hyper Parameter" in visualization now, the enhancement is being considered in #1110(https://github.com/microsoft/nni/issues/1110), any suggestions or discussions or contributions are warmly welcomed

[1]: ../AdvancedFeature/GeneralNasInterfaces.md
